# Notes

## Scale

* .5 million per file, we have 6000 impact files so far so ~ 3 billion triples.
* 1 month is about 600 files, so 300 million triples per month  (this is highly dynamic, as it literally depends on the weather)

## Questions for collaboration in the review

* How to optimize calls for resources to do graph completion when there may be hundreds to thousands
   of resources to resolve
* Exp[lore SPARQL construct calls to return triples vs typical SPARQL results
* Do activity recording with prov (that can be shared)
* interop is drive by what?   grid cells + measurement / observation +  time (more recent measurements are more important)
    * the relation with SOSA for UFOKN is potentially useful
    * could we leverage such properties on the query as well?
* With SHACL AF we can make new triples too, a sort of poor man's inferred triples (is this logically sound?)
* Though out of scope, principles involved in this work as also connected with the CODATA work in CDIF, so it
is interesting to cross pollinate there.
* UFOKN can offer up the building data as a derived product from Open Streetmap, MS Buildings
combined with some of the ML work for building classification done by UFOKN

## Observations

* potential reduction in spatial alignment of resources by leveraging 
  discrete grid resolution hierarchy 
* provides the potential for spatial operations in a non-spatial aware triplestore
* The alignment of fine and course grained S2 grid cells is potentially a big win to reduce 
  integration overhead.  Allows for integration at the level of most course detail
* Initial interop is done by humans, exchanging examples and knowledge, could this be 
represented in SHACL or something similar?   
