# converts a parquet file of UFOKN building information into a set of RDF triples (in turtle syntax)
# consistent with the UFOKN ontology
# authors V1 (Feb. 23, 2022) Sean McWillie, Torsten Hahmann, Urban Flooding
# developed in collaboration with other members of the Open Knowledge Network (UFOKN) team

# usage:
# python3 monoparser.py input_file.pqt output_file.ttl limit postcode

import sys
import time
import numpy as np
import pandas as pd


# this routes each row of the incoming data stream
# 
def router(df, lim: int) -> None:
    total_rows = 0
    no_build_ID = 0

    for index, row in df.iterrows():

        #print(row['units'])
        if row['buildID'] == None:
            # TODO there is a problem here: we have no buildID to identify the building
            no_build_ID += 1
    
        else:
            #if row['unit_count'] < 1.0:
            if isinstance(row['units'], np.ndarray) and len(row['units']) == 0:
                print("Skipping row with no units entry.")
            
            #elif row['unit_count'] == 1.0:
            elif isinstance(row['units'], np.ndarray) and len(row['units']) <= 1:
                #print("mono found")
                new_feature = monoProc(total_rows)
                writeFeature(new_feature)

            #elif row['unit_count'] > 1.0:
            elif isinstance(row['units'], np.ndarray) and len(row['units']) > 1:
                #print("poly")
                new_feature = polyProc(total_rows)
                writeFeature(new_feature)


            # elif row['units'] is empty but row['geometry'] is not:
            elif row['geometry'] is not None:
                # print("mono found")
                new_feature = monoProc(total_rows)
                writeFeature(new_feature)

            else:
                ...

            total_rows += 1

            if total_rows == lim:
                break

    print(total_rows + no_build_ID, "rows in parquet file.")
    print(total_rows, "rows processed with a buildID.")
    print(no_build_ID, "rows ignored with no buildID.")

def loadParquet(pqt_file: str) -> None:
    return pd.read_parquet(pqt_file, engine='pyarrow')

def exportCSV(target_df, csv_file = r'parquet_output.csv') -> None:
    target_df.to_csv(csv_file, index = False) 

def writeFeature(sometext: str, filename = sys.argv[2]) -> None:
    with open(filename, 'a+') as f:
        f.write(sometext) 
        f.seek(0)
        f.write('\n')

# this handles the sources, which are in a oa-ms-osm format
# more formats can be added if the source data changes
# this just reformats the string
def sourceHarness(sometext: str) -> None:

    if sometext:
        return "ufokn:fromDataSource " + ",".join(
            (
                sometext.replace(
                "oa", "ufokn:OAdataSource",1).replace(
                "ms", "ufokn:MSdataSource",1).replace(
                "osm", "ufokn:OSMdataSource",1)
                ).split("-")
            ) + ";"

# for single unit Features, the contents of each row are distributed according to the graph schema
# the target graph schema consists of three separate RDF statements (FeatureAtRisk, Address, RiskPoint)
# this takes a row (from the source data frame) and translates it into RDF statements

def monoProc(temp_pointer: int) -> str:

    ftAtRisk1_1 = '''### http://schema.ufokn.org/ufokn-data/v2/FeatureAtRisk/''' + str(df.loc[temp_pointer]['buildID']) + '''
    <ufokn-data:FeatureAtRisk/''' + str(df.loc[temp_pointer]['buildID']) + '''> rdf:type owl:NamedIndividual ,
                                                         ufokn:StandaloneFeatureAtRisk ;
                                                ufokn:hasAddress <ufokn-data:Address/''' + str(df.loc[temp_pointer]['buildID']) + '''> ;
                                                ufokn:hasRiskPoint <ufokn-data:RiskPoint/''' + str(df.loc[temp_pointer]['buildID']) + '''> ;
                                                ufokn:ms_id "''' + str(df.loc[temp_pointer]['ms_id']) + '''" ;
                                                ufokn:key "''' + str(df.loc[temp_pointer]['KEY']) + '''" ;
                                                ufokn:oa_id "''' + (str(df.loc[temp_pointer]['oa_id'][0]) if isinstance(df.loc[temp_pointer]['oa_id'], np.ndarray) else '') + '''" ;
                                                ''' + sourceHarness(df.loc[temp_pointer].loc['source']) + ''' 
                                                ufokn:value "''' + str(df.loc[temp_pointer]['VALUE']).lower() + '''" .''' + '\n'
    
    # For a feature with a single unit (or no unit information), the address is a streetAddress (as opposed to a UnitAddress)
    ftAtRisk1_2 = '''###  http://schema.ufokn.org/ufokn-data/v2/Address/''' + str(df.loc[temp_pointer]['buildID']) + '''
    <ufokn-data:Address/''' + str(df.loc[temp_pointer]['buildID'])+'''> rdf:type owl:NamedIndividual ,
                                                   ufokn:StreetAddress ;
                                          ufokn:street "''' + str(df.loc[temp_pointer]['street']) + '''" ;
                                          ufokn:streetNumber "''' + (str(df.loc[temp_pointer]['number'][0]) if isinstance(df.loc[temp_pointer]['number'], np.ndarray) else '') + '''";
                                          ufokn:city "''' + str(df.loc[temp_pointer]['city']) + '''" ; 
                                          ufokn:region "" ; 
                                          ufokn:state "";
                                          ufokn:postcode "''' + str(df.loc[temp_pointer]['postcode']) + '''".''' + '\n'

    ftAtRisk1_3 = '''###  http://schema.ufokn.org/ufokn-data/v2/RiskPoint/''' + str(df.loc[temp_pointer]['buildID']) + '''
    <ufokn-data:RiskPoint/''' + str(df.loc[temp_pointer]['buildID']) + '''> rdf:type owl:NamedIndividual ,
                                                     ufokn:RiskPoint ;
                                            geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/5070> ''' + str(df.loc[temp_pointer]['geometry']) + '''"^^geo:wktLiteral .'''+'\n'

    return ftAtRisk1_1 + '\n' + ftAtRisk1_2 + '\n' + ftAtRisk1_3 + '\n'


# Collections (of Features) consist of a RiskPoint and associated Units
# each Unit's information is a subnode in the graph
# using map() and lambda is closer to C++ for when this needs to be re-written
# basically when this line is parsed, its associated Units are created

def polyProc(temp_pointer) -> str:

    subLink2 = map( lambda subunitnumber:
               "<ufokn-data:FeatureAtRisk/" + str(df.loc[temp_pointer].loc['buildID']) + "/" + str(subunitnumber+1) + ">" ,
               range(int(len(df.loc[temp_pointer].loc['units'])) )
               )

    subUnit = map( lambda subunitnumber:
    '''
    ###  http://schema.ufokn.org/ufokn-data/v2/FeatureAtRisk/''' + str(df.loc[temp_pointer].loc['buildID']) + '''/''' + str(subunitnumber+1) + '''
    <ufokn-data:FeatureAtRisk/''' + str(df.loc[temp_pointer].loc['buildID']) + '''/''' + str(subunitnumber+1) + '''> rdf:type owl:NamedIndividual ,
                                                           ufokn:IndividualFeatureAtRiskInCollection ;
                                                  ufokn:hasAddress <ufokn-data:Address/''' + str(df.loc[temp_pointer].loc['buildID']) + '''/''' + str(subunitnumber+1)  + '''> ;
                                                  ufokn:hasRiskPoint <ufokn-data:RiskPoint/''' + str(df.loc[temp_pointer].loc['buildID']) + '''> ; 
                                                  ufokn:ms_id "''' + str(df.loc[temp_pointer]['ms_id']) + '''" ;
                                                  ufokn:key "''' + str(df.loc[temp_pointer]['KEY']) + '''" ;
                                                  ufokn:oa_id "''' + str(df.loc[temp_pointer]['oa_id'][0]) + '''" ;
                                                  ''' + sourceHarness(df.loc[temp_pointer].loc['source']) + ''' 
                                                  ufokn:value "''' + str(df.loc[temp_pointer]['VALUE']).lower() + '''" .''' + '\n' +


    '''
    ###  http://schema.ufokn.org/ufokn-data/v2/Address/''' + str(df.loc[temp_pointer].loc['buildID']) + '''/'''+ str(subunitnumber+1) +'''
    <ufokn-data:Address/''' + str(df.loc[temp_pointer].loc['buildID']) + '''/'''+ str(subunitnumber+1) +'''> rdf:type owl:NamedIndividual ,
                                                     ufokn:UnitAddress ;  
                                            ufokn:hasStreetAddress <ufokn-data:Address/''' + str(df.loc[temp_pointer].loc['buildID']) + '''> ; 
                                            ufokn:unitNumber "''' + df.loc[temp_pointer].loc['units'][subunitnumber] + '''".''',
                                            range(int(len(df.loc[temp_pointer].loc['units'])))
             )

    ftAtRisk2_1 = '''
    ###  http://schema.ufokn.org/ufokn-data/v2/CollectionOfFeatures/''' + str(df.loc[temp_pointer]['buildID']) + '''
    <ufokn-data:CollectionOfFeatures/''' + str(df.loc[temp_pointer]['buildID']) + '''> rdf:type owl:NamedIndividual ,
                                                                ufokn:CollectionOfFeatures ;
                                                       ufokn:hasMember ''' + ",\n".join(subLink2) + ";" + ''' 
                                                       ufokn:hasRiskPoint <ufokn-data:RiskPoint/''' + str(df.loc[temp_pointer].loc['buildID']) + '''> ;
                                                       ufokn:hasAddress <ufokn-data:Address/''' + str(df.loc[temp_pointer].loc['buildID']) + '''> .'''

    ftAtRisk2_2 = '''
    ###  http://schema.ufokn.org/ufokn-data/v2/Address/''' + str(df.loc[temp_pointer]['buildID']) + '''
    <ufokn-data:Address/''' + str(df.loc[temp_pointer]['buildID']) + '''> rdf:type owl:NamedIndividual ,
                                                   ufokn:StreetAddress ; 
                                          ufokn:street "''' + str(df.loc[temp_pointer]['street']) + '''" ;
                                          ufokn:streetNumber "''' + str(df.loc[temp_pointer]['number'][0]) + '''";
                                          ufokn:city "''' + str(df.loc[temp_pointer]['city']) + '''" ;
                                          ufokn:region "" ; 
                                          ufokn:state "";
                                          ufokn:postcode "''' + str(df.loc[temp_pointer]['postcode']) + '''".'''

    ftAtRisk2_3 = '''    
    ###  http://schema.ufokn.org/ufokn-data/v2/FeatureAtRisk/RiskPoint/''' + str(df.loc[temp_pointer]['buildID']) + '''
    <ufokn-data:RiskPoint/''' + str(df.loc[temp_pointer]['buildID']) + '''> rdf:type owl:NamedIndividual ,
                                                     ufokn:RiskPoint ;
                                            geo:asWKT "<http://www.opengis.net/def/crs/EPSG/0/5070> ''' + str(df.loc[temp_pointer]['geometry']) + '''"^^geo:wktLiteral .'''+'\n'
                                            
    ftAtRisk2_4 = '''                           
    ###  http://schema.ufokn.org/ufokn-data/v2/FeatureAtRisk/''' + str(df.loc[temp_pointer]['buildID']) + '''
    <ufokn-data:FeatureAtRisk/''' + str(df.loc[temp_pointer]['buildID']) + '''> rdf:type owl:NamedIndividual .'''
    

    return ftAtRisk2_1 + '\n' + ftAtRisk2_2 + '\n' + ftAtRisk2_3 + '\n' + "\n".join(subUnit) + '\n' 



if __name__ == '__main__':

# basic header for well-formed ttl file format
    namespaces = '''
    @prefix : <http://schema.ufokn.org/data/v2/> .
    @prefix ufokn-data: <http://schema.ufokn.org/data/v2/> .
    @prefix ufokn: <http://schema.ufokn.org/core/v2/> .
    @prefix ufokn-geo: <http://schema.ufokn.org/geo/v2/> .
    
    @prefix geo: <http://www.opengis.net/ont/geosparql#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix dcterms: <http://purl.org/dc/terms/> .
    
    @base <http://schema.ufokn.org/data/v2/> .

    
    '''

    dataProps = '''
    #################################################################
    #    Data properties
    #################################################################
    
    
    ###  http://schema.ufokn.org/geo/v2/hasWktGeometry
    ufokn-geo:hasWktGeometry rdf:type owl:DatatypeProperty ;
                             rdfs:domain geo:Feature ;
                             rdfs:range geo:wktLiteral .
    
    
    ### datatype properties for addresses
    
    ###  http://schema.ufokn.org/core/v2/unitNumber
    ufokn:unitNumber rdf:type owl:DatatypeProperty ;
                     rdf:type owl:FunctionalProperty ;
                     rdfs:domain ufokn:UnitAddress ;
                     rdfs:range xsd:string . 
                    
    ###  http://schema.ufokn.org/core/v2/unitCount
    ufokn:unitCount rdf:type owl:DatatypeProperty ;
                    rdf:type owl:FunctionalProperty ;
                    rdfs:domain ufokn:Address ;
                    rdfs:range xsd:positiveInteger . 
                    
    ###  http://schema.ufokn.org/core/v2/areaSize
    ufokn:areaSize rdf:type owl:DatatypeProperty ;
                   rdf:type owl:FunctionalProperty ;
                   rdfs:domain ufokn:Address ;
                   rdfs:range xsd:nonNegativeInteger . 
                    
    ###  http://schema.ufokn.org/core/v2/street
    ufokn:street rdf:type owl:DatatypeProperty ;
                 rdf:type owl:FunctionalProperty ;
                 rdfs:domain ufokn:Address ;
                 rdfs:range xsd:string . 
                    
    ###  http://schema.ufokn.org/core/v2/streetNumber
    ufokn:streetNumber rdf:type owl:DatatypeProperty ;
                       rdf:type owl:FunctionalProperty ;
                       rdfs:domain ufokn:Address ;
                       rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2/secondAddressLine
    ufokn:secondAddressLine rdf:type owl:DatatypeProperty ;
                            rdf:type owl:FunctionalProperty ;
                            rdfs:domain ufokn:Address ;
                            rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2/region
    ufokn:region rdf:type owl:DatatypeProperty ;
                 rdf:type owl:FunctionalProperty ;
                 rdfs:domain ufokn:Address ;
                 rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2/city
    ufokn:city rdf:type owl:DatatypeProperty ;
               rdf:type owl:FunctionalProperty ;
               rdfs:domain ufokn:Address ;
               rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2/state
    ufokn:state rdf:type owl:DatatypeProperty ;
                rdf:type owl:FunctionalProperty ;
                rdfs:domain ufokn:Address ;
                rdfs:range xsd:string . 
                    
    ###  http://schema.ufokn.org/core/v2/country
    ufokn:country rdf:type owl:DatatypeProperty ;
                  rdf:type owl:FunctionalProperty ;
                  rdfs:domain ufokn:Address ;
                  rdfs:range xsd:string . 
                    
    ###  http://schema.ufokn.org/core/v2/district
    ufokn:district rdf:type owl:DatatypeProperty ;
                   rdf:type owl:FunctionalProperty ;
                   rdfs:domain ufokn:Address ;
                   rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2/postcode
    ufokn:postcode rdf:type owl:DatatypeProperty ;
                   rdf:type owl:FunctionalProperty ;
                   rdfs:domain ufokn:Address ;
                   rdfs:range xsd:string . 
                    
    ### Data Properties for Features-at-risk
                    
    ###  http://schema.ufokn.org/core/v2/key
    ufokn:key rdf:type owl:DatatypeProperty ;
              rdfs:domain ufokn:FeatureAtRisk ;
              rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2/value
    ufokn:value rdf:type owl:DatatypeProperty ;
                rdfs:domain ufokn:FeatureAtRisk ;
                rdfs:range xsd:string . 
    
    ###  http://schema.ufokn.org/core/v2/id
    ufokn:id rdf:type owl:DatatypeProperty ;
             rdfs:range xsd:string .
    
    ###  http://schema.ufokn.org/core/v2/osm_id
    ufokn:osm_id rdf:type owl:DatatypeProperty ;
                 rdfs:subPropertyOf ufokn:id ;
                 rdfs:domain ufokn:FeatureAtRisk ;
				 rdfs:range xsd:string .
    
    ###  http://schema.ufokn.org/core/v2/ms_id
    ufokn:ms_id rdf:type owl:DatatypeProperty ;
                rdfs:subPropertyOf ufokn:id ;
                rdfs:domain ufokn:FeatureAtRisk ;
				rdfs:range xsd:string .
    
    ###  http://schema.ufokn.org/core/v2/oa_id
    ufokn:oa_id rdf:type owl:DatatypeProperty ;
                rdfs:subPropertyOf ufokn:id ;
                rdfs:domain ufokn:FeatureAtRisk ;
				rdfs:range xsd:string .
                       
    ### other datatype properties 
                       
    ###  http://schema.ufokn.org/core/v2/criticalDepth
    ufokn:criticalDepth rdf:type owl:DatatypeProperty ;
                        rdfs:domain ufokn:RiskPoint ;
                        rdfs:range ufokn:depth .
    
    
    ###  http://schema.ufokn.org/core/v2/dataSourceUri
    ufokn:dataSourceUri rdf:type owl:DatatypeProperty ;
                        rdfs:range xsd:anyURI .

'''

    writeFeature(namespaces)

    writeFeature(dataProps)

    parquet_file = sys.argv[1]

    df = loadParquet(parquet_file) 

    router(df, -1)  #set limit to -1 to parse entire parquet file
