CADC Data Engineering Process

The Canadian Astronomy Data Centre (CADC) Data Engineering Process (CDEP) is the extraction of metadata from a telescope, the transformation of that metadata into a Common Archive Object Model (CAOM) instance, and the making of that instance visible to users by loading it into CADC systems. This system excludes MAST.

![](cdep_context.png?raw=true)

The CDEP includes the:
   1. software that generates CAOM instances.
   1. people that code, test, review, and execute that software.
   1. process by which that software is coded, tested, made operational, and operated.
   1. collection metadata and data available from CADC.
   1. [CAOM model](https://www.opencadc.org/caom2/), in its current and future forms.
   1. people who understand the CAOM model, and the collection metadata and data, and can correlate the two.
   1. process by which these people correlate the collection metadata to the CAOM model.
   1. process by which CAOM content for collections is tested for completeness and correctness, reviewed for consistency with the CAOM representation of other collections, and assessed for general quality assurance.


CDEP Vocabulary:
   1. Pipeline - installed software required to create a CAOM instance for a collection.
   1. Blueprint - a mechanism for capturing the mapping between a Telescope Data Model (TDM) and CAOM.


## Who Does What
There are three roles in the CDEP - astronomers as subject matter expers, developers, and operators.

Astronomers are responsible for:
   1. coding or providing pseudocode for small applications that do astronomy-specific, collection-specific work
   1. coding or providing pseudocode for small functions that do common astronomy-specific work
   1. using github for any code
   1. defining the TDM->CAOM mapping
   1. identifying the cardinality for the TDM->CAOM mapping
   1. identifying the criteria under which CAOM instance creation/updates occur
   1. providing pipeline test data
   1. reviewing CAOM entries on sc2 for correctness and completeness
   1. reviewing CAOM entries in production for correctness and completeness
   1. reviewing CAOM entries for consistency with the representation of other collections
   1. reviewing CAOM entries for general quality assurance. This includes:
      1. extracting observation data from the relevant archive to check that the metadata is being expressed correctly
      1. checking that metadata in CADC agrees with metadata expressed at other telescope and archive sites
   1. general support of developers during the iterative automation of the Telescope->CAOM pipeline
   1. collaborative selection of which collections to include in the CAOM content
   1. using the content of the CAOM to execute science applications to ensure modeling utility
   1. exploring new metadata presentation and search approaches

Developers are responsible for:
   1. coding individual Telescope->CAOM pipelines, for each CADC and MAQ collection
   1. coding the TDM->CAOM mapping for a particular collection, into the pipeline execution
   1. coding the cardinality for the TDM->CAOM mapping into the pipeline execution
   1. coding the recognition of creates/updates to instigate pipeline execution
   1. coding tests for pipelines
   1. reviewing pipeline code
   1. identifying common code between pipelines, abstracting that code into libraries, and replacing the duplicate code in pipelines with the library versions
      1. document for consumption by astronomers as well as developers
      1. open-source software, available from github
   1. coding tests for common pipeline code
   1. reviewing common pipeline code
   1. providing pipeline code in Docker images
   1. instrumenting pipelines for debugging and operations support
   1. automating pipeline execution
   1. testing pipeline execution
   1. releasing the pipelines to operations
   1. providing operational support for pipeline execution
   1. interacting with astronomers for help with mappings, cardinality, and astronomy-specific code integration
   1. providing astronomers with assistance in coding and testing
      1. what does good code look like
   1. providing knowledge transfer for existing common libraries and functions that support pipeline development

Operators are responsible for:
   1. providing test environments for:
       1. pipeline execution
       1. storage interaction
          1. mitigate the need for Operations oversight by writing 0-byte files as the cleanup part of tests that touch the storage
       1. CADC service invocation (sc2)
   1. review operational requirements of pipelines prior to operational deployment
   1. providing an operational environment for repeated pipeline execution
   1. providing operational monitoring of pipeline execution, and feedback to developers upon failures

## How To Identify Common Bits

Identifying the bits that are common between pipelines will only be possible with familiarity with multiple pipelines.

The pipelines that currently exist at CADC are custom to each collection, and handled by individual DEs. A developer will achieve the necessary familiarity for the identification of common bits, by adopting the CDEP for each custom collection pipeline. 

The steps toward CDEP adoption for each collection will be:
   1. The astronomer will identify the existing bits for a pipeline. This may include:
      1. code
      1. scripts
      1. cron jobs
      1. VM Resource Requirements
         1. VM flavour
         1. additional installed software
         1. users
         1. credentials
         1. configuration
      1. representative test files that have existing CAOM instances
   1. A developer will assemble the existing bits into a github project.
   1. A developer will transition the existing bits to use the [Python caom2tools libarary](https://github.com/opencadc/caom2tools.git).
   1. A developer will verify the transition by comparing the output generated by Python with the existing CAOM instances, for the representative test files.
   1. The astronomer will confirm that any differences between the operational instance and the python-generated instance have no scientific implications.
      1. For example, there may be differences in the default WCS units in a Chunk element.
   1. A developer will automate the checking of the representative test files as integration tests for the collection.
   1. A developer will create a pipeline to be responsible for the following functionality, as necessary:
      1. file storage
      2. CAOM2 record creation
      3. supplementary files - e.g. thumbnails, previews
   1. A developer will build a Docker image for the pipeline.
   1. A developer will test the pipeline against sc2.
   1. A developer will make the initial collection2caom2 pipeline container available to Operations.
   1. Operations will execute the initial collection2caom2 pipeline based on the schedule given by the responsible astronomer.
   1. A developer will evaluate the custom collection pipeline information as collected in the github project and identify common behaviour with other pipelines. This can only happen with the second and following collections to be moved, but these seem to be common behaviours between collections, and candidates for extraction to common code:
      1. file retrieval from CADC storage
      2. file retrieval from https sites
      3. file retrieval from ftp sites
      4. file header retrieval from CADC storage
      5. footprint generation
      6. filter retrieval (spanish service)
      7. preview and thumbnail generation
      8. preview and thumbnail storage to CADC storage
      9. credential handling
      10. identification of new/modified files, and grouping for CAOM instance generation
      11. patterns for identifying inputs to an observation (based on file-naming patterns)
      12. script invocation
      13. checking whether a CAOM instance already exists, and retrieving the metadata if it does
      14. determining whether the caom2 service endpoint is create or update
      15. pushing CAOM instances to the caom2 service
      16. time axis metadata generation
   1. A developer will evaluate the custom collection pipeline information for astronomy-specific, collection-specific bits. 
      1. For each bit, the developer will extract that bit to a custom app. 
      1. Candidates for this extraction are limited to code that impacts multiple attributes in the CAOM model at a single invocation, or that cannot be retrieved by WCS-based, astropy-supported metadata. 
      1. This app will:
         1. be an appropriately-named .py script
         1. provide a function with the signature `visit(observation, **kwargs)`
            1. this is consistent with the current `caom2-repo` [visitor](https://github.com/opencadc/caom2tools.git/tree/master/caom2repo) 
         1. assume that all inputs have been provided
         1. assume that all outputs will be stored to CADC storage if they are data, and caom2 services if they are metadata
         1. live in a CDEP package
      1. For each app, the developer will create repeatable tests. 
   1. A developer will create a pipeline for the complete collection lifecycle.
      1. The first instance will be the foundation of the generic pipeline. The first iteration will be based on OMM.
      1. There will be a generic pipeline.
   1. A developer will create tests for the collection lifecycle pipeline. These will be based on the tests from the representative test files.
   1. A developer will identify and extract the common bits of the custom collection code to common libraries.
      1. The scope for the code considered for this library collection, is that it modifies the value of a single CAOM model attribute when invoked.
      1. Common library code will not reference FITS files, HDF5 files, or WCS keywords.
   1. A developer will replace existing duplicate code in a custom collection with common library implementations.
   1. A developer will code or adapt existing code to identify cardinality. An astronomer will provide the rules for the identification.
   1. A developer will test the cardinality identification code.
   1. The astronomer will review the results of the cardinality identification for correctness and completeness.
   1. The astronomer will review the CAOM instances for the representative test files for:
      1. consistency with the representation of other collections
      1. general quality assurance
   1. A developer will add the cardinality identification code to the extended pipeline.
   1. A developer will code or adapt existing code that identifies new inputs for dynamic collections.
   1. A developer will test the dynamic input identification code.
   1. A developer will add the dynamic input identification to the extended pipeline.
   1. A developer will build a Docker image for the extended pipeline.
   1. A developer will test the extended pipeline container against the development sandbox.
   1. A developer will test the extended pipeline container against operations.
   1. A developer will make the extended pipeline container available to Operations.
   1. Operations will execute the extended pipeline container based on the schedule given by the astronomer.
   1. The astronomer will review a subset of the operational CAOM instances for:
      1. consistency with the representation of other collections
      1. general quality assurance

These are the categories of code in a pipeline:
   1. custom apps, maintained by the astronomer
      1. affects multiple CAOM attributes at once
   1. common library code for pipeline management, maintained by the developer
   1. common library code for astronomy, maintained by the developer, with the assistance of interested astronomers
      1. not FITS or FITS keyword-specific
      2. not HDF5 specific
      3. affects a single CAOM attribute
   1. collection-specific code that integrates all the other pieces, maintained by the developer

A pipeline can run against the development sandbox (sc2) or production (www) web services.

The development lifecycle of all pipelines is iterative, and each pipeline will have to be addressed every time a collection is transitioned to pipeline behaviour. See the following diagram for a high-level abstraction of the lifecycle of a pipeline. Each box is a casual abstraction of a set of activities for a collection pipeline, and each arrow is an indication of iterative pipeline modification caused by genericization of yet another collection pipeline.

![](cdep_process.png?raw=true)


## Encapsulating the TDM->CAOM Mapping

There are multiple ways to encapsulate the TDM->CAOM mapping for a collection:
   1. Astronomers provide blueprint files, or code to generate the blueprint files. 
      1. This is new work for every collection except MEGAPIPE and CGPS.
   1. Astronomers provide code that creates a blueprint.
      1. This is new work for every collection.
   1. Astronomers provide code that creates an Observation.
      1. This exists for OMM.
   1. Astronomers provide code that works with the Java fits2caom2. Developers adapt it, with the approval of the reviewing astronomers, to the python fits2caom2 execution environment.
      1. This code exists for multiple collections. 
      1. There is new work required to test this code in the python environment. 
         1. The astronomer will identify a representative set of test files.
         1. The developer will set up repeatable tests that use this representative file set.
         1. Iteratively compare the python CAOM instances with operational CAOM instances, modify the drop-in changes, until the developer and the astronomer agree the python CAOM instances are correct.
   1. Astronomers update the UML for CAOM with the mapping for a collection, which is then turned into a blueprint.
      1. Blueprint generation from the updated model could be automated with the use of draw.io, and the development of a plugin.

## What Happens When CAOM Changes

Developers evaluate the impact of the model changes. Unless otherwise specified, work here is done by developers.

   1. Changes to the cardinality:
      1. recode the cardinality identification, with input from the astronomer for all collections
      1. update fits2caom2 blueprint code
      1. for all pipelined collections, update collection-based blueprints, depending on the mechanism the collection used to provide its blueprints
         1. depending on the model change, this may require astronomer support, in the form of science expertise, provisioning of test data, review of CAOM instances.
      1. test the pipelines
      1. manage the database transition for a breaking change
         1. create a view that represents the new model on the existing CAOM db
         1. export that view
         1. import that view into a new database
         1. re-direct services to new database
         1. run the pipelines with the new cardinality identification on all observations to fill in the blanks
   1. No changes to the cardinality:
      1. rework fits2caom2 blueprint code
      1. rework the collection-based blueprints as necessary, depending on the mechanism the collection used to provide its blueprints. 
         1. for model changes, depending on the model change, this may require astronomer support, in the form of science expertise, provisioning of test data, review of CAOM instances.
         1. for major metadata content fixes, depending on the fix, this may require astronomer support, in the form of science expertise, provisioning of test data, review of CAOM instances
         1. this can happen over time, collection by collection
      1. test the pipeline
         1. for model changes, manage the database transition for a non-breaking change as described below
         1. for major metadata content fixes, if, for example, the source data must be changed from etransfer (i.e. on local disk) to a storage system (i.e. ad), this pipeline deployment change should be limited to choosing a configuration option
         1. for visitor-style changes deploy a pipeline that executes caom2repo.core.main_app with appropriate arguments
      1. manage the database transition for a non-breaking change
         1. add new fields to db tables as required by the model change. 
            1. model changes that require modifications to existing column data will be handled by adding a new column.
         1. as each pipeline is updated, run the pipeline to fill in the new fields
         1. when all collections have adopted the new model, remove any deprecated fields
   1. When there is a change in the model, assist external users (i.e. JCMT) with the transition.

## How Developers Make Non-Mapping Code Changes

   1. Fork the affected repository within github.
   1. git clone the fork.
   1. Run existing unit tests to ensure they pass. These tests include ensuring that CAOM instance generation for the representative files remains consistent.
   1. Write new or update existing unit tests that cover the proposed changes.
   1. Code the changes.
   1. Repeat previous steps until all tests pass.
   1. Build the pipeline container.
   1. Test the pipeline container against sc2.
   1. Commit changes and push to github.
   1. Issue a github pull request.
   1. A different developer does a code review of the pull request.
   1. Rework based on review comments.
   1. Repeat previous steps until the reviewer accepts the pull request.
   1. Provide operations with the pipeline container.
   1. Depending on the nature of the change, operations ensures the container is used for all future ingestion, or operations ensures all existing CAOM instances are reprocessed.
   1. Developers ensure that updated CAOM instances are unaffected.


## How To Add New Collections And Instruments

   1. A new collection will require a new pipeline.
   1. A developer will create a <collection>_pipeline github project:
      1. populate it with the default minimal directory structure and content:
         1. python configuration files (setup.py, setup.cfg)
         1. Dockerfile
         1. docker-entrypoint.sh
      1. build the default docker container for the pipeline.
      1. the default project and container should be sufficient to ensure that a docker run <container details> python setup.py test command will execute without errors.
      1. it should be possible to create a template github project for this purpose, that can just be forked
   1. An astrnomer will identify a representative set of test files/inputs for the new collection that will serve as the integration tests for the pipeline.
   1. Together, a developer and an astronomer will evaluate what software is required for this pipeline:
      1. whether apps or methods already exist in cdep_apps, or new software must be created,
      1. whether the cardinality rules for this application require new software, or existing software will suffice,
      1. whether the dynamic input identification (i.e. how this pipeline discovers there are new observations to ingest) will require new software, or can make use of existing software, and
      1. how to handle data source credentials.
   1. An astronomer will provide the TDM -> CAOM mapping for the collection or instrument. See Encapsulating the TDM->CAOM Mapping for the ways this information can be communicated.
   1. A developer will assemble existing software into the new pipeline.
   1. A developer will write the non-astronomy new software.
   1. A developer will write new or update existing unit tests that cover the new non-astronomy software.
   1. Given the new pipeline skeleton, an astronomer will write the astronomy-specific software, or will provide sufficient instruction to the developer so that they can write the astronomy-specific software.
   1. Given the new pipeline skeleton, an astronomer or developer will write new or update existing unit tests that cover the new non-astronomy software.
   1. A developer and/or an astronomer will repeat until the stand-alone pipeline executes correctly, using the representative set of test files for confirmation.
   1. A developer will build the pipeline container.
   1. A developer will test the pipeline against sc2.
   1. An astronomer will review the sc2 CAOM instances for:
      1. completeness and correctness of the entities and attribute values,
      1. cardinality choice representations,
      1. consistency with the representation of other collections, and
      1. general quality assurance.
   1. Operations will configure for the new collection:
      1. production databases, 
      1. container deployment rules,
      1. monitoring, 
      1. logging, and
      1. TBD list here (I don’t know what goes here …).
   1. A developer will test the pipeline container against operations.
   1. A developer will make the extended pipeline container available to Operations.
   1. Operations will execute the extended pipeline container based on the schedule given by the astronomer.
   1. An astronomer will review a subset of the operational CAOM instances for:
      1. consistency with the representation of other collections, and
      1. general quality assurance.

To add support for new instruments to an existing pipeline, the above process would differ only in that the github project already exists.
  
## Pipeline Execution Triggers

A CAOM instance should be built-up by moving through a collection one file at a time.This is different from gathering all the data into a place and building an instance as a single occurrence. The workflow is clearer, more modular, and can be adapted when understanding evolves. 

Given this understanding of CAOM instance construction, the following types of events will trigger pipeline execution:
   1. Recognition of new or updated file arrival at CADC (in ad)
   1. manual
   1. TBD
  
## Implications

As part of the CDEP, the following will be enforced:
   1. All code, scripts, cron jobs, configuration, with the exception of user credentials, are in github.
   1. All code produced at CADC is python.
   1. All code will come with automated unit tests.
   1. All code will be reviewed.
   1. All code will be delivered to operations as a container.
   1. All code will be executable in a pipeline.
   1. All code will be versioned. Version increases will be enforced or automated.
   1. All execution will be automated.
   1. All configuration files, including blueprints, will be in YAML.
   1. The code will rely on feature flags (https://martinfowler.com/bliki/FeatureToggle.html).
   1. All github repositories will be configured to:
      1. require review before the acceptance of pull requests.
      1. utilize travis for unit test execution.
      1. utilize coveralls for unit test coverage measurement. Coverage will be configured to stay the same or go up.
   1. All code will be published under the approved CADC open source license choice.
   1. The python packages will be (see the diagram below):
      1. cdep_dags - new, will be enlarged over time as more collection executions are managed by pipeline control
         1. unique to each pipeline, and possibly each type of pipeline run as well (i.e. control priorities, catch-up vs dynamic, etc)
         1. <collection>2caom2 - new, one for each pipeline
      1. caom2tools - existing, some modification and refactoring as required
      1. caom2pipe 
         1. manage_composable - common management and other functions reside here
         1. astro_composable - this is where common functions affecting individual CAOM instance attributes will reside
         1. execute_composable - put the bits here together to make generic pipelines
   1. The github organization is [opencadc](https://github.com/opencadc).
  
## Goals
  
CDEP work needs to be maintainable and repeatable, and not the responsibility of DEs. To achieve that, these are the goals:
   1. automate everything, this means:
      1. working towards a goal of having every ingestion pipeline execution visible, for CADC collections and MAQ
      1. automated tests for all software
      1. automated deployment of the execution environment for all pipelines
      1. automated deployment of a collection’s pipeline execution environment
   1. extract the common bits out of every pipeline
   1. transition each pipeline away from DE execution
   1. address ways to communicate the TDM to CAOM2 mapping
   1. minimize the amount of tool knowledge required by DEs:
      1. github
      1. docker
      1. travis
      1. pipeline
      1. python
