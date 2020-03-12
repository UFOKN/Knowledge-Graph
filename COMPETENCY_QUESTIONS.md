# Competency Questions

Google Doc: https://docs.google.com/document/d/15YcQOQBwhOLEZfFe4r4aGcLs0B2MxRmHVwYz1lVp0uo/edit#

### Namespaces

```
PREFIX schema: <http://schema.org/>
PREFIX geoparql: <http://www.opengis.net/ont/geosparql#>
PREFIX geofunc: http://www.opengis.net/def/function/geosparql/
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns##>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sf: <http://www.opengis.net/ont/sf#>
PREFIX ufokn: <http://schema.ufokn.org/v1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```

## Nervous Norman


### 1. I see a storm is coming, will it flood near me? (Yes or No)

_Given:_ A real-time WGS84 coordinate ({?lat} {?lon}), and a radius of {?x} kilometers, any forecasted flooding?

_Query:_
```
SELECT ?forecast
WHERE {
  ?rp a ufokn:RiskPointFeature .
  ?rp geosparql:hasGeometry ?sf .
  ?sf geofunc:nearby ("Point({?lon} {?lat} )"^^geo:wktLiteral {?x} unit:Kilometer) .
  ?forecast ufokn:riskPointOfInterest ?rp .
  ?forecast a ufokn:RiskPointForecast .
  ?forecast ufokn:fromModelOutput [ ufokn:forecastTime ?time ] .
  FILTER (?time > {?now})
}
```

### 2. Is my home at 9219 Oak Knoll Ln, Houston, TX 77078 in danger of being flooded during the approaching weather system?

_Given: A home from the Zillow database _
```
INSERT {
  GRAPH <https://www.zillow.com/homedetails/9219-Oak-Knoll-Ln-Houston-TX-77078/28036610_zpid/> {
    ?home a ufokn:Home, schema:SingleFamilyResidence .
    ?home ufokn:hasRiskPoint ?rp .
      ?rp a ufokn:RiskPointFeature .
      ?rp geosparql:hasGeometry ?geom .
        ?geom a sf:Point .
        ?geom sf:spatialRS <http://www.wikidata.org/entity/Q11902211> .
        ?geom geo:asWKT "POINT(-95.252 29.839269)"^^geo:wktLiteral
    ?home ufokn:identifiedBy ?id .
      ?id ufokn:hasIdentifierScheme <http://www.wikidata.org/entity/Q8071921> .
      ?id ufokn:hasIdentifierValue "28036610_zpid"^^xsd:token .
    ?home schema:name "9219 Oak Knoll Ln, Houston, TX 77078"^^xsd:string .
    ?home schema:url "https://www.zillow.com/homedetails/9219-Oak-Knoll-Ln-Houston-TX-77078/28036610_zpid/"^^xsd:anyURI
    ?home schema:address ?address .
      ?address a schema:PostalAddress .
      ?address schema:streetAddress "9219 Oak Knoll Ln"^^xsd:string .   
      ?address schema:addressLocality "Houston"^^xsd:string . 
      ?address schema:addressRegion "TX"^^xsd:string .
      ?address schema:postalCode "77078"^^xsd:string .
  }
}
```

_Query:_
```
SELECT ?forecast
WHERE {
  {?home} ufokn:hasRiskPoint ?rp .
  ?rp a ufokn:RiskPointFeature .
  ?forecast ufokn:riskPointOfInterest ?rp .
  ?forecast a ufokn:RiskPointForecast .
  ?forecast ufokn:fromModelOutput [ ufokn:forecastTime ?time ] .
  FILTER (?time > {?now})
}
```

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
