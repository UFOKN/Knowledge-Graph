# Competency Questions

Google Doc: https://docs.google.com/document/d/15YcQOQBwhOLEZfFe4r4aGcLs0B2MxRmHVwYz1lVp0uo/edit#

### Namespaces

```
PREFIX schema: <http://schema.org/>
PREFIX geosparql: <http://www.opengis.net/ont/geosparql#>
PREFIX geofunc: http://www.opengis.net/def/function/geosparql/
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns##>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sf: <http://www.opengis.net/ont/sf#>
PREFIX ufokn: <http://schema.ufokn.org/core/v1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```

## Nervous Norman


### 1. I see a storm is coming, will it flood near me? (Yes or No)

_Given:_ A real-time WGS84 coordinate ({?lat} {?lon}), and a radius of {?x} kilometers, any forecasted flooding?

_Query:_
```
SELECT DISTINCT ?forecast
WHERE {
    ?forecast a ufokn:RiskPointDepthForecast .
    
    ?forecast ufokn:isInundated "true"^^xsd:boolean .
    ?forecast prov:used [ ufokn:fromForecast ?f ] .
    ?f ufokn:forecastTime ?forDateTime .
    FILTER (?forDateTime > "{now in ISO datetime format}"^^xsd:dateTime)
    ?forecast ufokn:atRiskPoint ?rp .
    ?rp geosparql:hasGeometry ?sf .
    ?sf geofunc:nearby ("Point({?lon} {?lat} )"^^geosparql:wktLiteral {?x} unit:Kilometer) .
}
LIMIT 1
```

### 2. Is my home at 9219 Oak Knoll Ln, Houston, TX 77078 in danger of being flooded during the approaching weather system?

_Given: FeatureAtRisk <https://id.ufokn.org/feature-at-risk/9219-Oak-Knoll-Ln_Houston_TX-77078>

_Query:_
```
SELECT DISTINCT ?forecast
WHERE { 
    ?forecast a ufokn:RiskPointDepthForecast .
    ?forecast ufokn:isInundated "true"^^xsd:boolean .
    ?forecast prov:used [ ufokn:fromForecast ?f ] .
    ?f ufokn:forecastTime ?forDateTime .
    FILTER (?forDateTime > "{?now in ISO datetime format}"^^xsd:dateTime)
    ?forecast ufokn:atRiskPoint ?rp .
	?feature ufokn:impactedByRiskPoint ?rp .
    BIND (<https://id.ufokn.org/feature-at-risk/9219-Oak-Knoll-Ln_Houston_TX-77078> as ?feature)   
}
LIMIT 1
```

### 3. Will I have access to food, power and fuel during this storm?



### 4. How long will I have to ride out the storm?
_Given:_ Nervous Norman's home (<https://id.ufokn.org/feature-at-risk/9219-Oak-Knoll-Ln_Houston_TX-77078>) and a current datetime {?now}.

_Query:_
```
SELECT DISTINCT ?forDateTime
WHERE { 
    ?forecast a ufokn:RiskPointDepthForecast .
    ?forecast ufokn:isInundated "true"^^xsd:boolean .
    ?forecast prov:used [ ufokn:fromForecast ?f ] .
    ?f ufokn:forecastTime ?forDateTime .
    FILTER (?forDateTime > "{?now in ISO datetime format}"^^xsd:dateTime)
    ?forecast ufokn:atRiskPoint ?rp .
	?feature ufokn:impactedByRiskPoint ?rp .
    BIND (<https://id.ufokn.org/feature-at-risk/9219-Oak-Knoll-Ln_Houston_TX-77078> as ?feature)   
}
ORDER BY DESC(?forDateTime)
LIMIT 1
```

### 5. Is there a possibility of damage to my house?

_Given:_ minimum depth determined as a damage threshold (@see ufokn:FLOODLEVEL_Flooded??)
_Query:_
```
SELECT DISTINCT ?forecast
WHERE { 
    ?forecast a ufokn:RiskPointDepthForecast .
    ?forecast ufokn:isInundated "true"^^xsd:boolean .
    ?forecast ufokn:forecastDepth ?forecastedDepthAtRiskPoint .
    FILTER (?forecastedDepthAtRiskPoint > "{?threshold}"^^xsd:float)
    ?forecast prov:used [ ufokn:fromForecast ?f ] .
    ?f ufokn:forecastTime ?forDateTime .
    FILTER (?forDateTime > "{?now in ISO datetime format}"^^xsd:dateTime)
    ?forecast ufokn:atRiskPoint ?rp .
	?feature ufokn:impactedByRiskPoint ?rp .
    BIND (<https://id.ufokn.org/feature-at-risk/9219-Oak-Knoll-Ln_Houston_TX-77078> as ?feature)   
}
LIMIT 1
```

### 6. Will I need to evacuate? If so, how soon and what is the safest route?

_Given:_ some level of flooding type indicating evacuation needed {?lvl} (@see ufokn:FloodLevelMessage_MajorFlooding)

```
SELECT DISTINCT ?forecast
WHERE { 
    ?forecast a ufokn:RiskPointDepthForecast .
    ?forecast ufokn:isInundated "true"^^xsd:boolean .
    ?forecast ufokn:floodLevelMessage ?msg .
    ?msg a {?lvl} .
    ?forecast prov:used [ ufokn:fromForecast ?f ] .
    ?f ufokn:forecastTime ?forDateTime .
    FILTER (?forDateTime > "{?now in ISO datetime format}"^^xsd:dateTime)
    ?forecast ufokn:atRiskPoint ?rp .
	  ?feature ufokn:impactedByRiskPoint ?rp .
    BIND (<https://id.ufokn.org/feature-at-risk/9219-Oak-Knoll-Ln_Houston_TX-77078> as ?feature)   
}
LIMIT 1
```
### 7. Will my water be safe to drink? Is there contamination in nearby water resources?


### 8. Alert me when a risk point in the given bounding box is predicted to be flooded.

_Given_: {?south} {?west} {?north} {?east} coordinates of a bounding box

_Query_:
```
SELECT DISTINCT ?forecast
WHERE {
    ?forecast a ufokn:RiskPointDepthForecast .
    
    ?forecast ufokn:isInundated "true"^^xsd:boolean .
    ?forecast prov:used [ ufokn:fromForecast ?f ] .
    ?f ufokn:forecastTime ?forDateTime .
    FILTER (?forDateTime > "{now in ISO datetime format}"^^xsd:dateTime)
    ?forecast ufokn:atRiskPoint ?rp .
    ?rp geosparql:hasGeometry ?sf .
    ?sf geofunc:within ("POLYGON (({?south} {?west}, {?north} {?west}, {?north} {?east}, {?south} {?east}, {?south} {?west}))"^^geosparql:wktLiteral {?x} unit:Kilometer) .
}
LIMIT 1
```

### 9. Whom do I contact to report flooding near my house?

### 10. I’m considering purchasing 124 Main St, Anytown, USA. Tell me how often it has flooded in the past?


### 11. I'm a business owner that needs to shut-down operations. How long will the flooding last? When will I be able to return to the area to restart operations.

### 12. How do I claim flood insurance? Should I move or stay in the long-term?

