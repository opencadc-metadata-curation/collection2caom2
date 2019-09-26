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

Explain the problem solved in more detail:
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
and file structure, the HST structure is proprietary and covered by 
ITAR regulations, and DAO began taking data in 1918, on glass plates.

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

For blueprint-based implementations, when one attribute in the CAOM2 record is affected by a particular input
value, use the blueprint. When more than one attribute in the CAOM2 record is affected by a particular
input value, use the update method, which is invoked via a 'visitor'.

## Cardinality Examples 

TBD

## Pipeline Examples

### How To Create A Pipeline
1. Create an appropriately named repository in the opencadc-metadata-curation organization.
1. Duplicate the blank2caom2 repository, according to [these instructions](https://help.github.com/articles/duplicating-a-repository/).
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
- all pipeline execution control comes from the file config.yml, so it must exist in the working directory. See [here](https://github.com/opencadc-metadata-curation/collection2caom2/wiki/config.yml) for a description of it's contents.
- add the create/update - must read to update from /ams/caom2repo/sc2repo
- repos are all on master, so anyone at any time can pull a repo and build the correct container
- use feature flags to limit the side-effects of work-in-progress commits
- SimpleObservation algorithm name == 'exposure', CompositeObservation algorithm name == 'composite'. There are currently no other choices.

# Credits and Connections
- contributors
- sponsors

# Brief Revision History
