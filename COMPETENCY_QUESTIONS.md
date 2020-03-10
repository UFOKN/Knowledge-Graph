# Competency Questions

Google Doc: https://docs.google.com/document/d/15YcQOQBwhOLEZfFe4r4aGcLs0B2MxRmHVwYz1lVp0uo/edit#


## Nervous Norman

1. I see a storm is coming, will it flood near me? (Yes or No)

_Given:_
```
INSERT {
  ?home a ufokn:Home .
  ?home ufokn:identifiedBy ?id .
  ?id ufokn:hasIdentifierScheme {?scheme} .
  ?id ufokn:hasIdentifierValue {?value} .
  ?home ufokn:hasRiskPoint ?rp .
  ?rp sf:spatialRS <http://www.wikidata.org/entity/Q11902211> .
  ?rp geo:lat {?lat} .
  ?rp geo:lon {?lon} .
}
```

_Query:_
```
SELECT ?forecast ?observation
WHERE {
  {?home} ufokn:hasRiskPoint ?feature .
  ?feature a ufokn:RiskPointFeature .
  ?forecast ufokn:riskPointOfInterest ?feature .
  ?forecast a ufokn:RiskPointForecast .
  ?forecast ufokn:fromModelOutput [ ufokn:forecastTime ?time ] .
  FILTER (?time > {?now})
}
```


2. Is my home at 123 Main St, Anytown,USA in danger of being flooded during the approaching weather system?
3. Will I have access to food, power and fuel during this storm?
4. How long will I have to ride out the storm?
5. Is there a possibility of damage to my house?
6. Will I need to evacuate? If so, how soon and what is the safest route?
7. Will my water be safe to drink? Is there contamination in nearby water resources?
8. Alert me when a risk point in the given bounding box is predicted to be flooded.
9. Whom do I contact to report flooding near my house?
10. I’m considering purchasing 124 Main St, Anytown, USA. Tell me how often it has flooded in the past?
11. I'm a business owner that needs to shut-down operations. How long will the flooding last? When will I be able to return to the area to restart operations.
12. How do I claim flood insurance? Should I move or stay in the long-term?
