# converts a parquet file of UFOKN building information into a set of RDF triples (in turtle syntax)
# consistent with the UFOKN ontology
# authors V1 (Feb. 23, 2022) Sean McWillie, Torsten Hahmann, Urban Flooding
#    current modification (April 13, 2023) David Kedrowski

# usage:
# python3 parser_data-parquet.py

import usaddress
import os
import pandas as pd
from collections import Counter


def load_parquet(parquet_file: str):
    return pd.read_parquet(parquet_file, engine='pyarrow')


def export_csv(target_df, csv_file=r'parquet_output.csv') -> None:
    target_df.to_csv(csv_file, index=False)


def write_feature(sometext: str, filename: str) -> None:
    with open(filename, 'a+') as f:
        f.write(sometext)
        f.seek(0)
        f.write('\n')


def source_harness(sometext: str) -> str:
    if sometext:
        return "ufokn:fromDataSource " + \
            ",".join((sometext.replace("oa", "ufokn:OAdataSource", 1).replace(
                "ms", "ufokn:MSdataSource", 1).replace(
                "osm", "ufokn:OSMdataSource", 1)).split("-")) + ";"


def router(source_df, lim: int, feature_file: str, elec_util_file: str, medical_file: str, water_file: str) -> None:
    total_rows = 0
    no_ufokn_id = 0
    far_count = 0
    elec_util_count = 0
    med_util_count = 0
    water_util_count = 0
    not_proc_count = 0
    used_uids = []
    # services = ['hospital', 'fire_station', 'police']

    for index, row in source_df.iterrows():
        # source = row['Description'].split(':')[0]
        key = row['Description'].split(':')[1]
        value = row['Description'].split(':')[2]

        if row['UFOKN_ID'] is None:
            # TODO there is a problem here: we have no UFOKN_ID to identify the building
            no_ufokn_id += 1
        elif key == 'power':
            if value == 'station':
                new_feature = elec_util_proc(total_rows, Counter(used_uids))
                write_feature(new_feature, elec_util_file)
                elec_util_count += 1
        # elif key == 'amenity' and value == 'hospital':
        elif value == 'hospital':
            new_feature = med_util_proc(total_rows, Counter(used_uids))
            write_feature(new_feature, medical_file)
            med_util_count += 1
        elif value == 'water_tower':
            new_feature = water_util_proc(total_rows, Counter(used_uids))
            write_feature(new_feature, water_file)
            water_util_count += 1
        else:
            if total_rows % 10 == 0:
                new_feature = far_proc(total_rows, Counter(used_uids))
                write_feature(new_feature, feature_file)
                far_count += 1

        total_rows += 1
        if total_rows % 10000 == 0 and total_rows > 0:
            print(f'{total_rows} rows processed so far')
        if total_rows == lim:
            break

        # used_uids.append(row['UFOKN_ID'])

    print(total_rows, "rows in parquet file.")
    print(elec_util_count, "rows added as electric services.")
    print(med_util_count, "rows added as medical services.")
    print(water_util_count, "rows added as water services")
    print(far_count, "rows added as features at risk.")
    print(no_ufokn_id, "rows ignored with no UFOKN_ID.")
    print(not_proc_count, "other rows not processed.")


def far_proc(temp_pointer: int, used_uids: dict) -> str:
    uid = str(df.loc[temp_pointer]['UFOKN_ID'])
    if uid in used_uids.keys():
        uid += '-' + str(used_uids[uid] + 1)
    key = str(df.loc[temp_pointer]['Description']).split(':')[1]
    val = str(df.loc[temp_pointer]['Description']).split(':')[2]
    street_number, street, city, state, postcode = extract_address_info(temp_pointer)
    lon = str(df.loc[temp_pointer]['X'])
    lat = str(df.loc[temp_pointer]['Y'])

    far = '''### http://schema.ufokn.org/ufokn_data/v2.1/FeatureAtRisk/''' + uid + '''
    <ufokn_data:FeatureAtRisk/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:StandaloneFeatureAtRisk ;
    ufokn:hasAddress <ufokn_data:Address/''' + uid + '''> ;
    ufokn:hasRiskPoint <ufokn_data:RiskPoint/''' + uid + '''> ;
    ufokn_c:requiresUtilityType ufokn_c:ElectricService ,
                              ufokn_c:MedicalService ,
                              ufokn_c:WaterService ,
                              ufokn_c:CommunicationService ;
    ufokn:id "''' + uid + '''" ;
    ufokn:key "''' + key + '''" ;
    ufokn:value "''' + val + '''" .''' + '\n'

    far_addr = '''###  http://schema.ufokn.org/ufokn_data/v2.1/Address/''' + uid + '''
    <ufokn_data:Address/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:StreetAddress ;
    ufokn:streetNumber "''' + street_number + '''";
    ufokn:street "''' + street + '''" ;
    ufokn:city "''' + city + '''" ; 
    ufokn:region "" ; 
    ufokn:state "''' + state + '''";
    ufokn:postcode "''' + postcode + '''".''' + '\n'

    far_rp = '''###  http://schema.ufokn.org/ufokn_data/v2.1/RiskPoint/''' + uid + '''
    <ufokn_data:RiskPoint/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:RiskPoint ;
    ufokn:criticalDepth "0"^^xsd:decimal ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/4326> POINT (''' + lon + ''' ''' + lat + ''')"^^geo:wktLiteral .''' + '\n'

    return far_rp + '\n' + far_addr + '\n' + far + '\n'


def elec_util_proc(temp_pointer: int, used_uids: dict) -> str:
    uid = str(df.loc[temp_pointer]['UFOKN_ID'])
    if uid in used_uids.keys():
        uid += '-' + str(used_uids[uid] + 1)
    try:
        wkt = str(df_elec_area[df_elec_area['UFOKN_ID'] == uid]['WKT'].values[0])
    except:
        wkt = 'POLYGON (())'
    key = str(df.loc[temp_pointer]['Description']).split(':')[1]
    val = str(df.loc[temp_pointer]['Description']).split(':')[2]
    street_number, street, city, state, postcode = extract_address_info(temp_pointer)
    lon = str(df.loc[temp_pointer]['X'])
    lat = str(df.loc[temp_pointer]['Y'])

    elec_serv_area = '''### ServiceArea for ElectricService-''' + uid + ''' coded as ElectricArea-''' + uid + '''
    <ufokn_data:ServiceArea/ElectricArea-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:ElectricServiceArea ;
    ufokn_c:ofUtilityType ufokn_c:ElectricService ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/4326> ''' + wkt + '''"^^geo:wktLiteral .''' + '\n'

    elec_serv = '''### An ElectricService coded as ElectricService-''' + uid + '''
    <ufokn_data:UtilityService/ElectricService-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:UtilityService ;
    ufokn_c:servesArea <ufokn_data:ServiceArea/ElectricArea-''' + uid + '''> ;
    ufokn_c:ofUtilityType ufokn_c:ElectricService ;
    ufokn_c:providedByProvider <ufokn_data:UtilityProvider/DukeEnergy> .''' + '\n'

    elec_asset = '''### An ElectricUtilityAsset coded as ElectricAsset-''' + uid + ''' (ElectricService-''' + uid + ''')
    <ufokn_data:UtilityAsset/ElectricAsset-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:ElectricUtilityAsset ;
    ufokn:hasAddress <ufokn_data:Address/''' + uid + '''> ;
    ufokn:hasRiskPoint <ufokn_data:RiskPoint/''' + uid + '''> ;
    ufokn_c:requiresUtilityType ufokn_c:ElectricService ;
    ufokn:id "''' + uid + '''" ;
    ufokn:key "''' + key + '''" ;
    ufokn:value "''' + val + '''" ;
    ufokn_c:providesUtilityService <ufokn_data:UtilityService/ElectricService-''' + uid + '''> ;
    ufokn_c:ofUtilityType ufokn_c:ElectricService .''' + '\n'

    elec_asset_addr = '''### Address for ElectricUtilityAsset coded as ElectricAsset-''' + uid + '''
    <ufokn_data:Address/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:StreetAddress ;
    ufokn:streetNumber "''' + street_number + '''";
    ufokn:street "''' + street + '''" ;
    ufokn:city "''' + city + '''" ; 
    ufokn:region "" ; 
    ufokn:state "''' + state + ''''";
    ufokn:postcode "''' + postcode + '''".''' + '\n'

    elec_asset_rp = '''### RiskPoint for ElectricUtilityAsset coded as ElectricAsset-''' + uid + '''
    <ufokn_data:RiskPoint/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:RiskPoint ;
    ufokn:criticalDepth "0"^^xsd:decimal ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/4326> POINT (''' + lon + ''' ''' + lat + ''')"^^geo:wktLiteral .''' + '\n'

    return elec_asset_rp + '\n' + elec_serv_area + '\n' + elec_serv + '\n' + elec_asset_addr + '\n' + elec_asset + '\n'


def med_util_proc(temp_pointer: int, used_uids: dict) -> str:
    uid = str(df.loc[temp_pointer]['UFOKN_ID'])
    if uid in used_uids.keys():
        uid += '-' + str(used_uids[uid] + 1)
    try:
        wkt = str(df_med_area[df_med_area['join_UFOKN'] == uid]['WKT'].values[0])
    except:
        wkt = 'MULTIPOLYGON Z ((()))'
    key = str(df.loc[temp_pointer]['Description']).split(':')[1]
    val = str(df.loc[temp_pointer]['Description']).split(':')[2]
    street_number, street, city, state, postcode = extract_address_info(temp_pointer)
    lon = str(df.loc[temp_pointer]['X'])
    lat = str(df.loc[temp_pointer]['Y'])

    med_serv_area = '''### ServiceArea for MedicalService-''' + uid + ''' coded as MedicalArea-''' + uid + '''
    <ufokn_data:ServiceArea/MedicalArea-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:MedicalServiceArea ;
    ufokn_c:ofUtilityType ufokn_c:MedicalService ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/4326> ''' + wkt + '''"^^geo:wktLiteral .''' + '\n'

    med_serv = '''### A MedicalService coded as MedicaService-''' + uid + '''
    <ufokn_data:UtilityService/MedicalService-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:UtilityService ;
    ufokn_c:servesArea <ufokn_data:ServiceArea/MedicalArea-''' + uid + '''> ;
    ufokn_c:ofUtilityType ufokn_c:MedicalService .''' + '\n'

    med_asset = '''### A MedicalUtilityAsset coded as MedicalAsset-''' + uid + ''' (MedicalService-''' + uid + ''')
    <ufokn_data:UtilityAsset/MedicalAsset-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:MedicalUtilityAsset ;
    ufokn:hasAddress <ufokn_data:Address/''' + uid + '''> ;
    ufokn:hasRiskPoint <ufokn_data:RiskPoint/''' + uid + '''> ;
    ufokn_c:requiresUtilityType ufokn_c:ElectricService ,
                              ufokn_c:MedicalService ,
                              ufokn_c:WaterService ;
    ufokn:id "''' + uid + '''" ;
    ufokn:key "''' + key + '''" ;
    ufokn:value "''' + val + '''" ;
    ufokn_c:providesUtilityService <ufokn_data:UtilityService/MedicalService-''' + uid + '''> ;
    ufokn_c:ofUtilityType ufokn_c:MedicalService .''' + '\n'

    med_asset_addr = '''### Address for MedicalUtilityAsset coded as MedicalAsset-''' + uid + '''
    <ufokn_data:Address/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:StreetAddress ;
    ufokn:streetNumber "''' + street_number + '''";
    ufokn:street "''' + street + '''" ;
    ufokn:city "''' + city + '''" ; 
    ufokn:region "" ; 
    ufokn:state "''' + state + ''''";
    ufokn:postcode "''' + postcode + '''".''' + '\n'

    med_asset_rp = '''### RiskPoint for MedicalUtilityAsset coded as MedicalAsset-''' + uid + '''
    <ufokn_data:RiskPoint/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:RiskPoint ;
    ufokn:criticalDepth "0"^^xsd:decimal ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/4326> POINT (''' + lon + ''' ''' + lat + ''')"^^geo:wktLiteral .''' + '\n'

    return med_asset_rp + '\n' + med_serv_area + '\n' + med_serv + '\n' + med_asset_addr + '\n' + med_asset + '\n'


def water_util_proc(temp_pointer: int, used_uids: dict) -> str:
    uid = str(df.loc[temp_pointer]['UFOKN_ID'])
    if uid in used_uids.keys():
        uid += '-' + str(used_uids[uid] + 1)
    try:
        wkt = str(df_water_area[df_water_area['UFOKN_ID'] == uid]['WKT'].values[0])
    except:
        wkt = 'MULTIPOLYGON ((()))'
    key = str(df.loc[temp_pointer]['Description']).split(':')[1]
    val = str(df.loc[temp_pointer]['Description']).split(':')[2]
    street_number, street, city, state, postcode = extract_address_info(temp_pointer)
    lon = str(df.loc[temp_pointer]['X'])
    lat = str(df.loc[temp_pointer]['Y'])

    water_serv_area = '''### ServiceArea for WaterService-''' + uid + ''' coded as WaterArea-''' + uid + '''
    <ufokn_data:ServiceArea/WaterArea-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:WaterServiceArea ;
    ufokn_c:ofUtilityType ufokn_c:WaterService ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/4326> ''' + wkt + '''"^^geo:wktLiteral .''' + '\n'

    water_serv = '''### A WaterService coded as WaterService-''' + uid + '''
    <ufokn_data:UtilityService/WaterService-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:UtilityService ;
    ufokn_c:servesArea <ufokn_data:ServiceArea/WaterArea-''' + uid + '''> ;
    ufokn_c:ofUtilityType ufokn_c:WaterService ;
    ufokn_c:providedByProvider <ufokn_data:UtilityProvider/HamiltonCountyWWTA> .''' + '\n'

    water_asset = '''### An WaterUtilityAsset coded as WaterAsset-''' + uid + ''' (WaterService-''' + uid + ''')
    <ufokn_data:UtilityAsset/WaterAsset-''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn_c:WaterUtilityAsset ;
    ufokn:hasAddress <ufokn_data:Address/''' + uid + '''> ;
    ufokn:hasRiskPoint <ufokn_data:RiskPoint/''' + uid + '''> ;
    ufokn_c:requiresUtilityType ufokn_c:ElectricService ,
                              ufokn_c:WaterService ;
    ufokn:id "''' + uid + '''" ;
    ufokn:key "''' + key + '''" ;
    ufokn:value "''' + val + '''" ;
    ufokn_c:providesUtilityService <ufokn_data:UtilityService/WaterService-''' + uid + '''> ;
    ufokn_c:ofUtilityType ufokn_c:WaterService .''' + '\n'

    water_asset_addr = '''### Address for WaterUtilityAsset coded as WaterAsset-''' + uid + '''
    <ufokn_data:Address/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:StreetAddress ;
    ufokn:streetNumber "''' + street_number + '''";
    ufokn:street "''' + street + '''" ;
    ufokn:city "''' + city + '''" ; 
    ufokn:region "" ; 
    ufokn:state "''' + state + ''''";
    ufokn:postcode "''' + postcode + '''".''' + '\n'

    water_asset_rp = '''### RiskPoint for WaterUtilityAsset coded as WaterAsset-''' + uid + '''
    <ufokn_data:RiskPoint/''' + uid + '''> rdf:type owl:NamedIndividual ,
    ufokn:RiskPoint ;
    ufokn:criticalDepth "0"^^xsd:decimal ;
    geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/4326> POINT (''' + lon + ''' ''' + lat + ''')"^^geo:wktLiteral .''' + '\n'

    return water_asset_rp + '\n' + water_serv_area + '\n' + water_serv + '\n' + water_asset_addr + '\n' + water_asset + '\n'


def extract_address_info(temp_pointer: int):
    address = df.loc[temp_pointer]['Address'].replace(' HAM ', ' ')
    address = address.replace('HAMILTON, ', '')  # works since Hamilton, OH is not in Hamilton County, OH
    address = address.replace('CT', 'COURT')
    try:
        data = usaddress.tag(address, tag_mapping={
            'AddressNumber': 'streetNumber',
            'StreetName': 'street',
            'StreetNamePreDirectional': 'street',
            'StreetNamePreModifier': 'street',
            'StreetNamePreType': 'street',
            'StreetNamePostDirectional': 'street',
            'StreetNamePostModifier': 'street',
            'StreetNamePostType': 'street',
            'PlaceName': 'city',
            'StateName': 'state',
            'ZipCode': 'postcode'
        })
        street = data[0]['street'] if 'street' in data[0] else ''
        street_number = data[0]['streetNumber'] if 'streetNumber' in data[0] else ''
        city = data[0]['city'] if 'city' in data[0] else ''
        state = data[0]['state'] if 'state' in data[0] else ''
        postcode = data[0]['postcode'] if 'postcode' in data[0] else ''
    except usaddress.RepeatedLabelError as e:
        print('RepeatedLabelError')
        print(f'  Original: {e.original_string}')
        print(f'  Parsed: {e.parsed_string}\n')
        street_number, street, city, state, postcode = '', '', '', '', ''
    return street_number, street, city, state, postcode


def write_name_spaces(file):
    # basic header for well-formed ttl file format
    namespaces = '''
    @prefix : <http://schema.ufokn.org/data/v2.1/> .
    @prefix ufokn_data: <http://schema.ufokn.org/data/v2.1/> .
    @prefix ufokn: <http://schema.ufokn.org/core/v2.1/> .
    @prefix ufokn_c: <http://schema.ufokn.org/utility-connection/v2.1/> .
    @prefix ufokn_geo: <http://schema.ufokn.org/geo/v2.1/> .
    
    @prefix geo: <http://www.opengis.net/ont/geosparql#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix dcterms: <http://purl.org/dc/terms/> .
    
    @base <http://schema.ufokn.org/data/v2.1/> .
    
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
            
    ###  http://schema.ufokn.org/core/v2.1/streetNumber
    ufokn:streetNumber rdf:type owl:DatatypeProperty ;
    rdf:type owl:FunctionalProperty ;
    rdfs:domain ufokn:Address ;
    rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2.1/street
    ufokn:street rdf:type owl:DatatypeProperty ;
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
    FAR_file = 'data_FAR_tenth.ttl'
    if os.path.exists(FAR_file):
        os.remove(FAR_file)
    write_name_spaces(FAR_file)
    write_props(FAR_file)

    ELEC_file = 'data_ELEC.ttl'
    if os.path.exists(ELEC_file):
        os.remove(ELEC_file)
    write_name_spaces(ELEC_file)
    write_props(ELEC_file)

    MED_file = 'data_HOSP.ttl'
    if os.path.exists(MED_file):
        os.remove(MED_file)
    write_name_spaces(MED_file)
    write_props(MED_file)

    WATER_file = 'data_WATER.ttl'
    if os.path.exists(WATER_file):
        os.remove(WATER_file)
    write_name_spaces(WATER_file)
    write_props(WATER_file)

    pqt_file = 'data.parquet'
    df = load_parquet(pqt_file)

    elec_area_file = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\data_power-station_voronoi_wkt.csv"
    df_elec_area = pd.read_csv(elec_area_file)
    df_elec_area.rename(columns={'UFOKN ID': 'UFOKN_ID'}, inplace=True)

    med_area_file = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\CSNA_dh_dissolved_4326_all.csv"
    df_med_area = pd.read_csv(med_area_file)

    water_area_file = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\data_watertower_voronoi_clipped_4326.csv"
    df_water_area = pd.read_csv(water_area_file)
    df_water_area.rename(columns={'UFOKN ID': 'UFOKN_ID'}, inplace=True)

    router(df, -1, FAR_file, ELEC_file, MED_file, WATER_file)  # set limit to -1 to parse entire parquet file
