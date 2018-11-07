# collection2caom2
Generic description of how to create CAOM2 instances for a collection.

# Making Telescope Data Findable
- introduction
- why product exists
- reference CAOM2
- similar?
- how will the software help, and why would anyone care?
- IVOA FAIR - findable, accessible, interoperable, resuable

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
