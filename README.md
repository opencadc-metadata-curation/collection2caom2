# Making Telescope Data Findable

The value of telescope data to the astronomical community increases if telescope data is findable by users other than the original PI. 

The principles of "discovery of, access to, integration and analysis of task-appropriate scientific data" are [generally-recognized](https://www.nature.com/articles/sdata201618), and have been formalized as "FAIR: Findable, Accessible, Interoperable, Re-Usable".

[What makes data 'findable'](https://www.force11.org/group/fairgroup/fairprinciples):

>  F1. (meta)data are assigned a globally unique and eternally persistent identifier.<br>
>  F2. data are described with rich metadata.<br>
>  F3. (meta)data are registered or indexed in a searchable resource.<br>
>  F4. metadata specify the data identifier.<br>

The repositories in this github organization address items F2 and F3 from above. 

The rich metadata (F2) for telescopes is described in [the Common Archive Observation Model](http://www.opencadc.org/caom2/).

The searchable resource (F3) is [here](http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/AdvancedSearch/).

This software eases the transition from the telescope model of the data to the CAOM data model. Once the data is described in CAOM metadata, the search interface provides a well-known location for Findable telescope data.

### Other Data Models and Search Facilities

1. [IVOA ObsCore Data Model](http://wiki.ivoa.net/internal/IVOA/ObsCoreDMvOnedotOne/WD-ObsCore-v1.1-20150605.pdf)
1. [IVOA TAP Query](http://www.ivoa.net/documents/TAP/)
1. [DaCHS](http://dc.g-vo.org/)

# Theory of Operation
- explain the problem solved in more detail
- describe the strategy it uses
- establish terminology
- be clear about why things are done as they are

# Detailed API Description

# Worked Examples
- with explanations and motivations

## Mapping Examples

### Direct Creation of Part- and Chunk-level WCS Information

See [here](https://github.com/opencadc/caom2tools/tree/master/caom2) for an example of how to create a minimal, or a complete Simple Observation, using the class definitions of the python caom2 module, where the WCS information is captured at the Chunk level.

Use this approach if FITS files are stored at CADC, and it's possible to utilize the existing CADC cutout functionality.

### Direct Creation of Plane-level WCS Information

See [the function _build_observation here](https://github.com/opencadc-metadata-curation/draost2caom2/blob/master/draost2caom2/main_app.py) for an example of how to create a Simple Observation, using the class definitions of the python caom2 module, where the WCS information is captured at the Plane level.

Use this approach if FITS files are not stored at CADC, or the data does not exist in FITS, and therefore there is no cutout functionality.

### Blueprint-Based Creation of CAOM2 Information

See [here](https://github.com/opencadc-metadata-curation/vlass2caom2/blob/master/vlass2caom2/vlass2caom2.py) for an example of how to capture the Telescope Data Model to CAOM2 instance mapping using blueprints.

Use this approach if the source data is in simple FITS files, and the mapping capabilities of the blueprint functionality are sufficient to capture the idiosyncracies of the TDM->CAOM2 mapping for the telescope in question.

## Cardinality Examples 

TBD

## Pipeline Examples

### How To Create A Pipeline
1. Create an appropriately named repository in the opencadc-metadata-curation organization.
1. Duplicate the blank2caom2 repository, according to [these instructions](https://help.github.com/articles/duplicating-a-repository/).
1. In the new repository, rename all the items named blank'Something'.

# Tricks and Traps
- what might confuse users about API and address it directly
- explain why each gothca is the way it is
- add the create/update - must read to update from /ams/caom2repo/sc2repo
- repos are all on master, so anyone at any time can pull a repo and build the correct container
- use feature flags to limit the side-effects of work-in-progress commits

# Credits and Connections
- contributors
- sponsors

# Brief Revision History
