# Knowledge-Graph
Keeps track of concepts, models, and axioms for the data

## Pitch

- [ ] Computational Capability
- [ ] Persona development
- [ ] How Personnas innteract w/ system


## Prototypes

- [ ] Notify me of potential flood (Nervous Norman). Is this paramterized? given a certain radius from a centroid?
- [ ] Where is it flooded?
    - [ ] 1-hr predictions
    - [ ] model run
    - [ ] Affected transportation routes (Powerful Pete/Proactive Paula) - i.e. From *here* to *there* what *route* is best for a given *vehicle type*?
        - [ ] Responding to event - should I take a boat?

## Conceptual Model

GOAL: to communicate the knowledge aspect of the network

### Concepts

- [ ] Vector files - graph stores Digital Object model (see @fils) for all vector files.
- [ ] Region
- [ ] Catchment
- [ ] Elevation
- [ ] Roadway
- [ ] Flow Line
- [ ] First Floor elevation
- [ ] Submitted model (inputs? outputs?)
- [ ] Synthetic power grid (As demo. replaceable by actual power grid)
- [ ] what else?

### Logical Model 

Build a working ontology for the graph data (@torsten)

## Submission 

## Crowdsourced data for the Network

GOAL: groundtruthing, prediction improvement, knowledge sharing

### Reporting App for Significant Flood Events

The Reporting App takes the geolocation of the reporting device and the date/time of the submitted event and contributes it into the knowledge graph.

Requirements: 
- [ ] user profile - for managing reputation inside the social network. handling false positives and fake data? See Waze.
    - [ ] profile types? Homeowner, Utility Manager, Civil Engineer, etc? as a proy for available event types
- [ ] geolocation data from the device
- [ ] date/time data from the device
- [ ] taxonomy of reportable events 
- [ ] 

#### What is the taxonomy for Event types? (Siddarth)
- [ ] Dam Breach
- [ ] Power Grid Failure
- [ ] Downed Power Line
- [ ] Flooded House
- [ ] ????

## Inferencing Tests - on any inntersection between a catchment and road.

- [ ] boolean flag for reclassifying flooded intersection
- [ ] model output value against the depth and flow rates of an intersection.

## Build for Model Submission (@siddarth - Jan. 2020)

### What parameters are required? units?


