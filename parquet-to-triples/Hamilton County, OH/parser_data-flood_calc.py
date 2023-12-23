import pandas as pd
import os
import random

min_mnz = 0.001
max_mnz = 1.000

min_md = 0.001
max_md = 12.000

flood_dist_max = 0.009309595111480119
flood_dist_996 = 0.996 * flood_dist_max


def create_flood_data(source_df, flood_file: str) -> None:
    total_rows = 0
    proc_count = 0
    not_proc_count = 0

    for index, row in source_df.iterrows():
        new_feature = flood_proc(row)
        write_feature(new_feature, flood_file)
        proc_count += 1

        total_rows += 1
        if total_rows % 5000 == 0 and total_rows > 0:
            print(f'{total_rows} rows processed so far')

    print()
    print(total_rows, "rows in csv file.")
    print(proc_count, "rows processed.", f'{proc_count / total_rows * 100}%')
    print(not_proc_count, "rows skipped.", f'{not_proc_count / total_rows * 100}%')


def flood_proc(temp_row) -> str:
    uid = str(temp_row['UFOKN_ID'])
    flood_dist = float(temp_row['dist_to_floodway'])
    time_of_first_flood = calc_time_of_first_flood(flood_dist)
    time_of_max = calc_time_of_max(time_of_first_flood)
    min_non_zero = calc_min_non_zero(flood_dist)
    max_depth = calc_max_depth(min_non_zero, time_of_first_flood, time_of_max)

    flood = '''### http://schema.ufokn.org/ufokn_data/v2.1/FloodLevelObservation/''' + uid + '''
    <ufokn_data:FloodLevelObservation/''' + uid + '''> rdf:type owl:NamedIndividual , ufokn_fl:FloodLevelObservation ;
    ufokn_fl:firstFloodTime "''' + time_of_first_flood + '''" ;
    ufokn_fl:minNonZero "''' + str(min_non_zero) + '''"^^xsd:decimal ;
    ufokn_fl:maxFloodTime "''' + time_of_max + '''" ;
    ufokn_fl:maxDepth "''' + str(max_depth) + '''"^^xsd:decimal .
    
    <ufokn_data:RiskPoint/''' + uid + '''> ufokn_fl:hasFloodLevelObservation <ufokn_data:FloodLevelObservation/''' + uid + '''>  .''' + '\n'

    return flood + '\n'


def calc_min_non_zero(distance) -> float:
    proportion = distance / flood_dist_max
    return round(min_mnz + (1 - proportion) * (max_mnz - min_mnz), 3)


def calc_max_depth(mnz, time1, time2) -> float:
    rand = random.randint(1, 100)
    if time1 == time2:
        return mnz
    else:
        return round(mnz + rand / 100 * (max_md - mnz), 3)


def calc_time_of_first_flood(distance):
    if distance < flood_dist_996:
        return 't_1'
    else:
        q = random.randint(2, 18)
        return 't_' + str(q)


def calc_time_of_max(first):
    q = random.randint(1, 4)
    if q == 4:
        num = int(first[2:])
        new_num = num + random.randint(0, 18 - num)
        return 't_' + str(new_num)
    else:
        return first


def write_feature(sometext: str, filename: str) -> None:
    with open(filename, 'a+') as f:
        f.write(sometext)
        f.seek(0)
        f.write('\n')


def write_name_spaces(file):
    # basic header for well-formed ttl file format
    namespaces = '''
    @prefix : <http://schema.ufokn.org/flood/v2.1/> .
    @prefix ufokn_data: <http://schema.ufokn.org/data/v2.1/> .
    @prefix ufokn: <http://schema.ufokn.org/core/v2.1/> .
    @prefix ufokn_c: <http://schema.ufokn.org/utility-connection/v2.1/> .
    @prefix ufokn_fl: <http://schema.ufokn.org/flood/v2.1/> .
    @prefix ufokn_geo: <http://schema.ufokn.org/geo/v2.1/> .

    @prefix geo: <http://www.opengis.net/ont/geosparql#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix dcterms: <http://purl.org/dc/terms/> .

    @base <http://schema.ufokn.org/flood/v2.1/> .

    '''
    write_feature(namespaces, file)


def write_props(file):
    data_props = '''
    #########################
    #    Data properties    #
    #########################

    ###  http://schema.ufokn.org/geo/v2.1/hasWktGeometry
    ufokn_geo:hasWktGeometry rdf:type owl:DatatypeProperty ;
    rdfs:domain geo:Feature ;
    rdfs:range geo:wktLiteral .

    ### datatype properties for addresses

    ###  http://schema.ufokn.org/core/v2.1/unitNumber
    ufokn:unitNumber rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:UnitAddress ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/unitCount
    ufokn:unitCount rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:positiveInteger . 

    ###  http://schema.ufokn.org/core/v2.1/areaSize
    ufokn:areaSize rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:nonNegativeInteger . 

    ###  http://schema.ufokn.org/core/v2.1/street
    ufokn:street rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/streetNumber
    ufokn:streetNumber rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/secondAddressLine
    ufokn:secondAddressLine rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/region
    ufokn:region rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/city
    ufokn:city rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/state
    ufokn:state rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/country
    ufokn:country rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/district
    ufokn:district rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/postcode
    ufokn:postcode rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 

    ### Data Properties for Features-at-risk

    ###  http://schema.ufokn.org/core/v2.1/key
    ufokn:key rdf:type owl:DatatypeProperty ;
    rdfs:domain ufokn:FeatureAtRisk ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/value
    ufokn:value rdf:type owl:DatatypeProperty ;
    rdfs:domain ufokn:FeatureAtRisk ;
    rdfs:range xsd:string . 

    ###  http://schema.ufokn.org/core/v2.1/id
    ufokn:id rdf:type owl:DatatypeProperty ;
    rdfs:range xsd:string .

    ###  http://schema.ufokn.org/core/v2.1/osm_id
    ufokn:osm_id rdf:type owl:DatatypeProperty ;
    rdfs:subPropertyOf ufokn:id ;
    rdfs:domain ufokn:FeatureAtRisk ;
    rdfs:range xsd:string .

    ###  http://schema.ufokn.org/core/v2.1/ms_id
    ufokn:ms_id rdf:type owl:DatatypeProperty ;
    rdfs:subPropertyOf ufokn:id ;
    rdfs:domain ufokn:FeatureAtRisk ;
    rdfs:range xsd:string .

    ###  http://schema.ufokn.org/core/v2.1/oa_id
    ufokn:oa_id rdf:type owl:DatatypeProperty ;
    rdfs:subPropertyOf ufokn:id ;
    rdfs:domain ufokn:FeatureAtRisk ;
    rdfs:range xsd:string .

    ### other datatype properties 

    ###  http://schema.ufokn.org/core/v2.1/criticalDepth
    ufokn:criticalDepth rdf:type owl:DatatypeProperty ;
    rdfs:domain ufokn:RiskPoint ;
    rdfs:range ufokn:depth .

    ###  http://schema.ufokn.org/core/v2.1/dataSourceUri
    ufokn:dataSourceUri rdf:type owl:DatatypeProperty ;
    rdfs:range xsd:anyURI .

    '''
    write_feature(data_props, file)


if __name__ == '__main__':
    FLOOD_file = 'data_FLOOD.ttl'
    if os.path.exists(FLOOD_file):
        os.remove(FLOOD_file)
    write_name_spaces(FLOOD_file)
    write_props(FLOOD_file)

    flood_csv = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\data_floodzone_FEMA_buffer_4326_wkt.csv"
    df = pd.read_csv(flood_csv)
    df.rename(columns={'UFOKN ID': 'UFOKN_ID'}, inplace=True)

    create_flood_data(df, FLOOD_file)
