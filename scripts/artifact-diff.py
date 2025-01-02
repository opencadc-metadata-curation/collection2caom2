import sys

from astropy.table import Table
from cadctap import CadcTapClient
from cadcutils.net import Subject
from datetime import datetime
from io import StringIO
from os.path import exists
from os import mkdir
from numpy import savetxt
from sys import argv

import pandas as pd


def _clean(t, is_si):
    t.contentChecksum = t.contentChecksum.astype('string')
    t.contentChecksum = t.contentChecksum.str.replace('md5:', '')
    t.contentLength = t.contentLength.apply(pd.to_numeric)
    if is_si:
        t.contentType = t.contentType.apply(_to_string_si)
    else:
        t.contentType = t.contentType.apply(_to_string)


def _run_query(
    query_string,
    client,
    timeout=60,
):
    # timeout is in minutes
    print('start')
    buffer = StringIO()
    client.query(
        query_string,
        output_file=buffer,
        data_only=True,
        response_format='tsv',
        timeout=timeout,
    )
    temp = Table.read(buffer.getvalue().split('\n'), format='ascii.tab')
    print(len(temp))
    print('end')
    return temp.to_pandas()


def _total_in_caom(collection, root_dir, subject, resource='ivo://cadc.nrc.ca/argus'):
    qs = f"""
    SELECT A.uri, A.contentChecksum, A.contentLength, A.contentType
    FROM caom2.Observation AS O
    JOIN caom2.Plane AS P ON O.obsID = P.obsID
    JOIN caom2.Artifact AS A ON A.planeID = P.planeID
    WHERE O.collection = '{collection}'
    """
    client = CadcTapClient(subject, resource_id=resource)
    t = _run_query(qs, client)
    _clean(t, False)
    t.to_csv(f'{root_dir}/in_caom.txt', header=False, index=False)
    return t


def _total_in_storage(
    collection,
    root_dir,
    subject,
    resource='ivo://cadc.nrc.ca/global/luskan',
):
    qs = f"""
    SELECT uri, contentChecksum, contentLength, contentType
    FROM inventory.Artifact AS A
    WHERE uri LIKE '%:{collection}/%'
    """
    client = CadcTapClient(subject, resource_id=resource)
    t = _run_query(qs, client)
    _clean(t, True)
    t.to_csv(f'{root_dir}/in_si.txt', header=False, index=False)
    return t


def _to_string_si(a):
    if a == '':
        return 'x'
    return a


def _to_string(a):
    if a == '':
        return 'y'
    return a


def main():
    collection = argv[1].upper()
    caom_resource = argv[2]
    si_resource = argv[3]
    print(f'collection {collection} caom_resource {caom_resource} si_resource {si_resource}')

    root_dir = f'/usr/src/app/{collection.lower()}'
    if not exists(root_dir):
        mkdir(root_dir)

    start = datetime.now()
    subject = Subject(certificate='/usr/src/app/cadcproxy.pem')
    total_in_caom = _total_in_caom(collection, root_dir, subject, caom_resource)
    # _clean(total_in_caom, False)
    print('done total_in_caom')
    sys.stdout.flush()
    total_in_storage = _total_in_storage(collection, root_dir, subject, si_resource)
    # _clean(total_in_storage, True)
    print('done total_in_storage')
    sys.stdout.flush()

    total_not_in_storage = total_in_caom[~total_in_caom.uri.isin(total_in_storage.uri)]
    total_not_in_storage.to_csv(f'{root_dir}/not_in_si.txt', header=False, index=False)
    len_total_not_in_storage = len(total_not_in_storage)
    del total_not_in_storage
    total_not_in_storage = pd.DataFrame()

    total_not_in_caom = total_in_storage[~total_in_storage.uri.isin(total_in_caom.uri)]
    total_not_in_caom.to_csv(f'{root_dir}/not_in_caom_si.txt', header=False, index=False)
    len_total_not_in_caom = len(total_not_in_caom)
    del total_not_in_caom
    total_not_in_caom = pd.DataFrame()

    print('done total_not_in_caom')
    sys.stdout.flush()
    # length of common should be:
    # len_common == len(total_in_caom) - len(total_not_in_storage) == len(total_in_storage) - len(total_not_in_caom)
    #
    total_correct = pd.merge(
        total_in_storage,
        total_in_caom,
        how='inner',
        on=['uri', 'contentLength', 'contentType', 'contentChecksum'],
    )
    total_correct.to_csv(f'{root_dir}/total_correct.txt', header=False, index=False)
    len_total_correct = len(total_correct)
    del total_correct
    total_correct = pd.DataFrame()

    common = total_in_storage[total_in_storage.uri.isin(total_in_caom.uri)]
    len_total_in_storage = len(total_in_storage)
    # del total_in_storage
    # total_in_storage = pd.DataFrame()

    # len_length, len_content_type, len_checksum = _drop_dups(common, total_in_caom, root_dir)
    len_length, len_content_type, len_checksum = _merges(total_in_storage, total_in_caom, root_dir)

    end = datetime.now()
    elapsed = end - start

    msg = f"""
{{
  "logType":"summary",
  "collection":"{collection}",
  "totalInCAOM":"{len(total_in_caom)}",
  "totalInStorage":"{len_total_in_storage}",
  "totalCorrect":"{len_total_correct}",
  "totalDiffChecksum":"{len_checksum}",
  "totalDiffLength":"{len_length}",
  "totalDiffType":"{len_content_type}",
  "totalNotInCAOM":"{len_total_not_in_caom}",
  "totalMissingFromStorage":"{len_total_not_in_storage}",
  "totalNotPublic":"0",
  "time":"{elapsed}"
}}
"""
    print(msg)

    with open(f'{root_dir}/{end.isoformat()}_summary_si.txt', 'w') as f:
        f.write(msg)


def _merges(total_in_storage, total_in_caom, root_dir):
    merged = pd.merge(total_in_storage, total_in_caom, how='inner', on=['uri'])
    checksum = merged[merged.contentChecksum_x != merged.contentChecksum_y]
    savetxt(f'{root_dir}/checksum_mismatch_si.txt', checksum, fmt='%s', delimiter=',')
    len_checksum = len(checksum)
    del checksum

    content_length = merged[merged.contentLength_x != merged.contentLength_y]
    savetxt(f'{root_dir}/length_mismatch_si.txt', content_length, fmt='%s', delimiter=',')
    len_length = len(content_length)
    del content_length

    content_type = merged[merged.contentType_x != merged.contentType_y]
    savetxt(f'{root_dir}/type_mismatch_si.txt', content_type, fmt='%s', delimiter=',')
    len_type = len(content_type)
    del content_type

    return len_length, len_type, len_checksum



def _drop_dups(common, total_in_caom, root_dir):
    length = pd.concat(
        [common, total_in_caom], join='inner'
    ).drop_duplicates(subset=['uri', 'contentLength'], keep=False).uri.unique()

    savetxt(f'{root_dir}/length_mismatch_si.txt', length, fmt='%s', delimiter=',')
    len_length = len(length)
    del length
    length = pd.DataFrame()
    print('done length')
    sys.stdout.flush()

    content_type = pd.concat(
        [common, total_in_caom], join='inner'
    ).drop_duplicates(subset=['uri', 'contentType'], keep=False).uri.unique()
    savetxt(f'{root_dir}/type_mismatch_si.txt', content_type, fmt='%s', delimiter=',')
    len_content_type = len(content_type)
    del content_type
    content_type = pd.DataFrame()
    print('done content_type')
    sys.stdout.flush()

    checksum = pd.concat(
        [common, total_in_caom], join='inner'
    ).drop_duplicates(subset=['uri', 'contentChecksum'], keep=False).uri.unique()
    savetxt(f'{root_dir}/checksum_mismatch_si.txt', checksum, fmt='%s', delimiter=',')
    len_checksum = len(checksum)
    del checksum
    checksum = pd.DataFrame()
    print('done checksum')
    sys.stdout.flush()

    return len_length, len_content_type, len_checksum


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import logging
        logging.error(e)

