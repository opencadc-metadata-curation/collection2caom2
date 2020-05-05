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

## The Problem Being Solved
What astronomers want to be able to do:
"The  ability to pose a single scientific query to multiple [collections] simultaneously" 
The [IVOA ObsCore Data Model](http://wiki.ivoa.net/internal/IVOA/ObsCoreDMvOnedotOne/WD-ObsCore-v1.1-20150605.pdf) explains use cases quite well (see also Appendix A). The summary information from Section 2 is repeated here:
- support multi-wavelength as well as positional and temporal searches.
- support any type of science data product (image, cube, spectrum, time series, instrumental data, etc.)
- directly  support  the  sorts  of  file  content  typically  found  in  archives  (FITS,  VOTable, compressed files, instrumental data, etc.

What inhibits this:
The data models that describe the output from different observatories are complex, the 
work of multiple creative individuals, enduring, expedient, and unique. To illustrate 
the wide range of models, the [ALMA measurement set specification](https://casa.nrao.edu/casadocs/casa-5.4.1/reference-material/measurement-set)
 includes directory 
and file structure, the [HST](https://archive.org/details/firstyearofhstob00kinn/page/270) structure is proprietary and covered by 
ITAR regulations, and [DAO](https://centreoftheuniverse.org/early-history) began taking data in 1918, on glass plates.

The CAOM2 data model provides a consistent description of the data from different observatories. Each &lt;collection&gt;2caom2 pipeline application captures the software which produces those consistent data descriptions. The captured descriptions are then exposed as a searchable inventory for use by anyone who is interested.

Looked at another way, the CAOM2 data model provides a way to group observational data for effective querying.

## The Strategy Being Used

There are three parts to having data end up in CAOM2 Observations:
- mapping the telescope data model to the CAOM2 data model. This happens generically in the
python module caom2utils, and collection-specifically in each &lt;collection&gt;2caom2 module.
- determining the relationship between telescope files and CAOM2 entities - i.e. how many Observations, Planes, Artifacts, Parts, and Chunks are created for each telescope file? This is called cardinality in the code.
This happens in collection-specific code only, in each &lt;collection&gt;2caom2 module.
- putting the pieces of mapping and cardinality together, into a repeatable pipeline for automated execution. 
This happens generically in the caom2pipe module, with collection-specific invocations
in &lt;collection&gt;2caom2 modules.

This diagram describes the dependencies between python modules: 

![](cdep_deps.png?raw=true)

- caom2utils - the generic mapping between the TDM and CAOM2, captured as the
ObsBlueprint class
- caom2 - the CAOM2 model
- caom2pipe - the bits of the pipelines, common between all collections
  - astro_composable - confine reusable code with dependencies on astropy here
  - caom_composable - confine reusable code with dependencies on CAOM2 here
  - execute_composable - common pipeline steps and execution control
    - StorageName - generic interface for managing naming issues for files in collections
    - CaomName - common code to hide CAOM-specific naming structures
    - CaomExecute - common code to implement each TaskType in a pipeline. Extended multiple ways for specific TaskType implementations.
    - OrganizeExecutor - takes the collection-specific Config, picks the appropriate CaomExecute children, and organizes a series of Tasks for execution. Also manages logging.
    - additional functions that contain common code used directly by the collections to execution the work to be done
  - manage_composable - common methods, used anywhere
    - Metrics - for tracking how long it takes to use CADC services
    - Rejected - for tracking known pipeline failures
    - Config - pipeline control
    - State - bookmarking pipeline execution
    - Work - generic interface for chunking the next items to be processed by a pipeline
    - Features - very basic feature flag implementation - False/True only
    - TaskType - enumeration of the allowable task types. This is the verbiage that a user will see in their config file.
- &lt;collection&gt;2caom2 - contains collection-specific code, including:
  - extension of the fits2caom2 module for TDM -&gt; CAOM mapping code
  - file -&gt; CAOM cardinality code
  - extension of the StorageName class, if unique behaviour is required
  - extension of the Work class as required. There may be multiple extensions, depending on the character of the collection.
  - invocation of the execution_composable.run_&lt;mechanism&gt;. These mechanism invocations are the pipeline execution points.

The Advanced Search UI provides a way to find and download data for processing. Other UIs (TBD) provide ways to find and analyze data through the UI.

## Terminology

1. Files are the current unit of input, as that is the output of every telescope currently being discussed here.

# Detailed API Description

## Metrics

If 'observe_execution' is set to True in the config.yml file, then the pipeline captures metrics for the CADC services invoked during its execution. In the observable_execution directory, there will be files named like 1568331248.133947.data.yml, 1568331248.133947.caom2.yml, and 1568331248.133947.fail.yml.

The ‘.data.yml’ file will have entries for ‘get’, and ‘put’, and for each file, will list the time in seconds, the rate in bytes/second, and the start time as seconds since the epoch. The ‘.caom2.yml’ file will have entries for ‘create’, ‘read’, and ‘update’, and for each CAOM2 observation, will list the time in seconds, the rate in bytes/second, and the start time as seconds since the epoch. The ‘.fail.yml’ file wil list, for each file affected by a failed action, a count of how many times it failed.

The files are created for every run of the pipeline.

## Reporting

At the end of a pipeline run, a file named <working directory basename>\_report.txt is created in the logging directory. The content will look like this:

```
********************************
Location: tests
Date: 2020-03-18T17:16:08.540069
Execution Time: 3.98 s
  Number of Inputs: 1
Number of Timeouts: 0
 Number of Retries: 1
  Number of Errors: 1
********************************
```

- Execution time: the time from initiating the pipeline to completion of execution.
- Number of inputs: the number of entries originally counted. Depending on the content of config.yml, this value will originate from a work file, or files on disk, or cumulative tracking of entries when working by state.
- Number of timeouts: the number of times exceptions that may involve timeouts were generated. Those exceptions include messages like "Read timed out", "reset by peer", "ConnectTimeoutError", and "Broken pipe". 
- Number of retries: the number of retries executed. Depending on whether and how retry is enabled in config.yml, this value is the cumulative number of entries processed more than once.
- Number of errors: the number of failures after the final retry. If this number is zero, a retry fixed the failures, so all entries were eventually ingested.


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

For blueprint-based implementations, when one attribute in the CAOM2 record is affected by a particular input
value, use the blueprint. When more than one attribute in the CAOM2 record is affected by a particular
input value, use the update method, which is invoked via a 'visitor'.

## Cardinality Examples 

TBD

## Pipeline Examples

### How To Create A Pipeline
1. Create an appropriately named repository in the opencadc-metadata-curation organization.
1. Create a new repository, using the blank2caom2 template repository, according to [these instructions](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-from-a-template).
1. In the new repository:
   1. rename all the items named blank'Something'.
   1. in main_app.py, capture the TDM -&gt; CAOM2 mapping using the blueprint for FITS keyword lookup,
   or for function execution. Also extend and over-ride StorageName here as necessary.
   1. in composable.py, capture the pipeline execution needs of the collection
      1. 'collection'_run assumes the generation of the todo.txt file is done externally
      1. 'collection'_run_by_state generates the todo.txt file content based on queries, whether of
      tap services or other time-boxed data sources
   1. in work.py, capture any query needs of the collection

# Tricks and Traps
- what might confuse users about API and address it directly
- explain why each gothca is the way it is
- all pipeline execution control comes from the file config.yml, so it must exist in the working directory. See [here](https://github.com/opencadc-metadata-curation/collection2caom2/wiki/config.yml) for a description of its contents.
- add the create/update - must read to update from /ams/caom2repo/sc2repo
- repos are all on master, so anyone at any time can pull a repo and build a working version of any pipeline container
- use feature flags to limit the side-effects of work-in-progress commits

## Authorization Doesn't Really Work With sc2 Record Viewing and Retrieval

1. Authorization only consults /ams content, so even if the group and membership configuration is consistent and correct, if something is not always and only public, it must exist in /ams for file download to work.

   Thumbnails and previews are also affected by this /ams-only check. Viewing these files only works on sc2 if the metadata that refers to the files is also present in /ams.

## Things To Know About CAOM2 Observation Construction

### Planes

1. Plane-level metadata is only computed for productType=science|calibration. Auxiliary artifacts (or parts or chunks) are expected to be part of another plane with science, unless it is a temporary state caused by ingestion order.

1. For radio, plane level position resolution is used to answer the question "what is the smallest scale that can be resolved?", and is most often the synthesized beam width.

### Artifacts

1. Grouping files into observations/planes/artifacts is determined by how independent the files are. A measure of file independence is whether or not the file can be scientifically understood in isolation. Some observational products may be made up of multiple files - e.g. NGVS .flag, .weight, .image files make up the same observational product. Some observational products may be made up of single files - e.g. CFHT o, p, and b files. In this example, the CFHT files are independent, and thus can be grouped in isolation from each other, while the NGVS files are dependent, and should be grouped together.

### Chunks

#### CoordAxis1D/CoordAxis2D

1. It is valid to have  bounds, range, and/or function as stated in the model. Practically, bounds is  redundant if you have a range. Bounds provides more detail than range, including gaps in coverage, and enables a crude tile-based cutout operation later. Historically, range was added later in the model life.

#### Chunk.naxis, Chunk.energy_axis, Chunk.time_axis, Chunk.polarization_axis, Chunk.custom_axis

1. In general, assigning axis indices above the value of naxis (3 and 4 here) is allowed but more or less pointless. The only use case that would justify it is that in a FITS file there could be a header with NAXIS=2 and WCSAXES=4 which would tell the fits reader to look for CTYPE1 through 4 and axes 3 and 4 are metadata. Assign those values to Chunk only if you care about capturing that the extra wcs matadata was really in the fits header and so the order could be preserved; in general do not assign the 3 and 4.

1. In an exposure where the position is not relevant and only the energy and time is relevent for discovery, the easiest correct thing to do is to leave naxis, energyAxis, and timeAxis all null: the same plane metadata should be generated and that should be valid. The most correct thing to do would be to set naxis=2, positionAxis1=1, positionAxis2=2 (to indicate image) and then use a suitable coordiante system description that meant "this patch of the inside of the dome" or maybe some description of the pixel coordinate system (because wcs kind of treats the sky and the pixels as two different systems)... I don't know how to do that and it adds very minimal value (it allows Plane.position.dimension to be assigned a value).

1. When there is no spatialWCS, setting naxis, position_axis_1, and position_axis_2 values to null allows services to know that they can't do WCS-based cutouts.  The pixel-based cutouts will still work as they do not use that information.

#### SubIntervals

1. SubIntervals are subject to the check "sorted by increasing value, so sample[i].upper < sample[i+1].lower"

#### What if there's no WCS?

1. There are OMM observations with no WCS information, because the astrometry software did not solve. The lack of solution may have been because of cloud cover or because a field is just not very populated with stars, like near the zenith, but the data still has value.

   There is the CoordError datatype which is set for a CoordAxes2D object that would capture this detail. By approximating a WCS solution, and providing a syser value that is representative of the point-model error of the facility (e.g. CFHT has approximately 1 arcmin), and then represent this by making the bounding box bigger by the value of the syser on the coord.

#### Under what conditions should chunk.productType be set?

1. Part.productType and Chunk.productType should be set if the applicable value differs from the parent. In many cases the value in the Artifact is sufficient. I think it best to set productType the minimum places, but it isn't wrong to set it everywhere.

   For example, a FITS file with two extensions: one science and one auxiliary. The Artifact.productType would be science and the Part.productType would be null (for the science part) and auxiliary for the auxiliary part. One would only need to set Chunk.productType if there are multiple chunks and some differed from the Artifact or Part productType.

### Inputs vs Members

1. Pat - Generally, members is what the grouping algorithm intended to include in the processing and inputs is what was actually included. In an ideal world, the inputs are simply the plane(s) of the member(s). Then one has to decide what to do with inputs that were rejected at processing time (inputs is a subset of members since we don't have any role or flags in the input relationship?) and whether inputs should refer to non-member (eg calibration inputs for a science co-add) entities. That's in principle within scope of provenance but I don't have any use cases to guide me in giving advice and we don't really have any s/w or systems that use the provenance metadata. Mostly we want users to be able to tell whether A and B have common "photon ancestry", bit only because we always thought it was important for people to know that (not that we know of anyone doing the necessary queries).

1. Members - Pat - members would all be the same type as the DerivedObservation, so in the typical case the members of a science DerivedObservation would be the science observations that were combined to create it. Thus the members list describes the intended operation.

1. Inputs - Pat - inputs describes the provenance of the resulting data, so it captures what actually happened. That normally includes the planes from each of the members that was used and could also include other kinds of inputs (eg calibration inputs) that do not correspond to any observation in the members list.

    There is currently no role information in the provenance/inputs but it is needed to really generalise the usage beyond just science data. If the goal is to give someone enough info to reproduce a plane from the provenance then other info would be needed.
    
    So, for now, I would only put the real components in members and put at least the planes from those in the inputs; adding more inputs (eg calibration inputs of a science product) can be done but I don't think it is justified right now.

    If the DerivedObservation has intent=science then the members would all be intent = science.

### Permissions

1. The 3 types of read access tuples can be generated in two ways:
    1. The collection can be configured (sc2repo.properties) with an operatorGroup (aka CADC), and staffGroup (aka NGVS) and these directly enable creation of tuples for those two groups; if staffGroup is set, then a 3rd option proposalGroup=true enables generation of groups based on Observation.collection and Observation.proposal.id (and as a side effect, creation of those groups and adding the staffGroup as admin); the TEST collection has the full config; None of these are set for NGVS so no tuples are generated.
     1. in CAOM-2.4 these permissions are part of the model and read access group URIs can be included in the observation;  thus the client could in principle create arbitrary tuples; this hasn't been done before and it could be a good idea or a bad one depending on the case at hand and how much responsibility the client wants to take (vs using the simple canned rules)

### Outstanding Questions

1. Where in the CAOM2 model do we keep the dimensions of the FITS data?  This is useful metadata for queries.  When searching for FLAT/BIAS calibrations one needs to have ones with the same NAXIS1/NAXIS2 values.

# Credits and Connections
- contributors

## Sponsors

[CADC](http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/)

# Brief Revision History
