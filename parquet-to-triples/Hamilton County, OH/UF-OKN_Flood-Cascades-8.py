from SPARQLWrapper import SPARQLWrapper, JSON, GET, POST
import sparql_dataframe
import pandas as pd
from shapely import wkt
import geopandas as gpd
import folium

pd.options.display.width = 240

# endpoint = 'http://DavidSurfacePro7:7200/repositories/UFOKN-CinciFlood'
endpoint = 'http://DavidSurfacePro7:7200/repositories/UFOKN-CinciFlood-Test'
# endpoint = 'http://DavidSurfacePro7:7200/repositories/UFOKN-CinciFlood-4326removed'

sparql = SPARQLWrapper(endpoint)
sparql.setReturnFormat(JSON)

flood_area_poly_file = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\FEMA_Floodway_0.5-mile_buffer_4326.shp"
power_poly_file = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\data_power-station_voronoi_clipped.shp"
cinci_hosp_poly_file = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\CSNA_dh_dissolved_4326_all.csv"
water_poly_file = r"C:\Users\david\OneDrive - University of Maine System\Documents\UMaine\UFOKN-ontologies\parquet to triples\data (Hamilton County, OH)\GIS - Hamilton County, OH\data_watertower_voronoi_clipped_4326.csv"

flood_area = gpd.read_file(flood_area_poly_file)
flood_area.set_crs(epsg=4326, inplace=True, allow_override=True)
power = gpd.read_file(power_poly_file)
power.set_crs(epsg=4326, inplace=True, allow_override=True)
cinci_hosp = gpd.read_file(cinci_hosp_poly_file)
cinci_hosp.set_crs(epsg=4326, inplace=True, allow_override=True)
water = gpd.read_file(water_poly_file)
water.set_crs(epsg=4326, inplace=True, allow_override=True)

sparql.setQuery("""ASK WHERE { GRAPH <http://schema.ufokn.org/example/UFOKN-Cincinnati_SERVES> { ?s ?p ?o } }""")
sparql.setMethod(GET)
result = sparql.queryAndConvert()
exists = result['boolean']
print(exists)

if exists is False:
    print('Converting servesArea to serves')
    sparql.setMethod(POST)
    sparql.setQuery("""
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX ufokn: <http://schema.ufokn.org/core/v2.1/>
        PREFIX ufokn_c: <http://schema.ufokn.org/utility-connection/v2.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        INSERT {
            GRAPH <http://schema.ufokn.org/example/UFOKN-Cincinnati_SERVES> {
                ?service ufokn_c:serves ?feature .
            }
        }
        WHERE {
            ?servicearea rdf:type ufokn_c:UtilityServiceArea .
            ?service ufokn_c:servesArea ?servicearea .
            ?servicearea geo:sfIntersects ?riskpoint .
            ?feature ufokn:hasRiskPoint ?riskpoint .
        }
        """)
    results = sparql.queryAndConvert()
    print(results)

sparql.setQuery("""ASK WHERE { GRAPH <http://schema.ufokn.org/example/UFOKN-Cincinnati_CritFloodObs> { ?s ?p ?o } }""")
sparql.setMethod(GET)
result = sparql.queryAndConvert()
exists = result['boolean']
print(exists)

if exists is False:
    print('Preprocessing CriticalFloodObservation')
    sparql.setMethod(POST)
    sparql.setQuery("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX ufokn: <http://schema.ufokn.org/core/v2.1/>
        PREFIX ufokn_c: <http://schema.ufokn.org/utility-connection/v2.1/>
        PREFIX ufokn_fl: <http://schema.ufokn.org/flood/v2.1/>

        INSERT {
            GRAPH <http://schema.ufokn.org/example/UFOKN-Cincinnati_CritFloodObs> {
                ?floodObs rdf:type ufokn_fl:CriticalFloodObservation .
            }
        }
        WHERE {
            ?utilityAsset rdf:type ufokn_c:UtilityAsset .
            ?utilityAsset ufokn:hasRiskPoint ?riskpoint .
            ?riskpoint ufokn_fl:hasFloodLevelObservation ?floodObs .
            ?floodObs ufokn_fl:minNonZero ?floodDepth .
            ?riskpoint ufokn:criticalDepth ?critDepth .
            FILTER(?floodDepth > ?critDepth)
        }
        """)
    results = sparql.queryAndConvert()
    print(results)

far_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX ufokn: <http://schema.ufokn.org/core/v2.1/>
    PREFIX ufokn_c: <http://schema.ufokn.org/utility-connection/v2.1/>
    PREFIX ufokn_fl: <http://schema.ufokn.org/flood/v2.1/>

    SELECT ?far ?uid ?key ?value ?uatype ?utilityAsset ?uawkt ?rootasset ?rootwkt ?streetnum ?street ?city ?state ?zip ?wkt ?minnonzero ?maxdepth ?firstfloodtime ?maxfloodtime WHERE
    { 
        { SELECT ?utilityAsset WHERE 
            {
                ?utilityAsset rdf:type ufokn_c:UtilityAsset .
                ?utilityAsset ufokn:hasRiskPoint ?riskpoint .
                ?riskpoint ufokn_fl:hasFloodLevelObservation ?floodObs .
                ?floodObs rdf:type ufokn_fl:CriticalFloodObservation .
            }
        }
        UNION
        { SELECT ?utilityAsset WHERE 
            {
                ?floodedAsset rdf:type ufokn_c:UtilityAsset .
                ?floodedAsset ufokn:hasRiskPoint ?riskpoint .
                ?riskpoint ufokn_fl:hasFloodLevelObservation ?floodObs .
                ?floodObs rdf:type ufokn_fl:CriticalFloodObservation .

                ?utilityAsset rdf:type ufokn_c:UtilityAsset .
                ?floodedAsset ufokn_c:assetCriticallyServesTC ?utilityAsset .
            }
        }

        ?utilityAsset ufokn_c:assetOfTypeRequiredBy ?far .
        ?utilityAsset ufokn_c:assetCriticallyServes ?far .
        ?utilityAsset ufokn_c:ofUtilityType ?uatype . 
        ?utilityAsset ufokn:hasRiskPoint ?uariskpoint .
        ?uariskpoint geo:asWKT ?uawkt .

        ?rootasset rdf:type ufokn_c:UtilityAsset .
        ?rootasset ufokn_c:assetCriticallyServesTC ?utilityAsset .

        ?rootasset ufokn:hasRiskPoint ?rootriskpoint .
        ?rootriskpoint geo:asWKT ?rootwkt .
        ?rootriskpoint ufokn_fl:hasFloodLevelObservation ?floodObs .

        ?far ufokn:id ?uid .
        ?far ufokn:key ?key .
        ?far ufokn:value ?value .
        ?far ufokn:hasAddress ?address .
        ?address ufokn:streetNumber ?streetnum .
        ?address ufokn:street ?street .
        ?address ufokn:city ?city .
        ?address ufokn:state ?state .
        ?address ufokn:postcode ?zip .
        ?far ufokn:hasRiskPoint ?rp .
        ?rp geo:asWKT ?wkt .
        OPTIONAL
        {
            ?rp ufokn_fl:hasFloodLevelObservation ?floodlevel .
            ?floodlevel ufokn_fl:firstFloodTime ?firstfloodtime .
            ?floodlevel ufokn_fl:minNonZero ?minnonzero .
            ?floodlevel ufokn_fl:maxFloodTime ?maxfloodtime .
            ?floodlevel ufokn_fl:maxDepth ?maxdepth .
        }
    } GROUP BY ?far ?uid ?key ?value ?uatype ?utilityAsset ?uawkt ?rootasset ?rootwkt ?streetnum ?street ?city ?state ?zip ?wkt ?minnonzero ?maxdepth ?firstfloodtime ?maxfloodtime
"""
df_far = sparql_dataframe.get(endpoint, far_query)
df_far['wkt'] = df_far['wkt'].str.replace('<http://www.opengis.net/def/crs/EPSG/0/4326> ', '')
df_far['rootwkt'] = df_far['rootwkt'].str.replace('<http://www.opengis.net/def/crs/EPSG/0/4326> ', '')
df_far['uawkt'] = df_far['uawkt'].str.replace('<http://www.opengis.net/def/crs/EPSG/0/4326> ', '')
df_far.to_csv('query_results.csv', index=False)

# df_far = df_far[df_far['far'].str.contains('FeatureAtRisk', regex=True)].copy()
df_far_root_elec = df_far[df_far['rootasset'].str.contains('ElectricAsset', regex=True)].copy()
df_far_root_watr = df_far[df_far['rootasset'].str.contains('WaterAsset', regex=True)].copy()
df_far_root_med = df_far[df_far['rootasset'].str.contains('MedicalAsset', regex=True)].copy()
df_far_locl_elec = df_far[df_far['utilityAsset'].str.contains('ElectricAsset', regex=True)].copy()
df_far_locl_watr = df_far[df_far['utilityAsset'].str.contains('WaterAsset', regex=True)].copy()
df_far_locl_med = df_far[df_far['utilityAsset'].str.contains('MedicalAsset', regex=True)].copy()

df_far.drop(columns=['uawkt', 'rootwkt'], inplace=True)
df_far['wkt'] = df_far['wkt'].apply(wkt.loads)

df_far_root_elec = df_far_root_elec[['rootasset','rootwkt']]
df_far_root_elec.drop_duplicates(inplace=True)
df_far_root_elec['rootwkt'] = df_far_root_elec['rootwkt'].apply(wkt.loads)

df_far_root_watr = df_far_root_watr[['rootasset','rootwkt']]
df_far_root_watr.drop_duplicates(inplace=True)
df_far_root_watr['rootwkt'] = df_far_root_watr['rootwkt'].apply(wkt.loads)

df_far_root_med = df_far_root_med[['rootasset','rootwkt']]
df_far_root_med.drop_duplicates(inplace=True)
df_far_root_med['rootwkt'] = df_far_root_med['rootwkt'].apply(wkt.loads)

df_far_locl_elec = df_far_locl_elec[['utilityAsset','uawkt']]
df_far_locl_elec.drop_duplicates(inplace=True)
df_far_locl_elec['uawkt'] = df_far_locl_elec['uawkt'].apply(wkt.loads)

df_far_locl_watr = df_far_locl_watr[['utilityAsset','uawkt']]
df_far_locl_watr.drop_duplicates(inplace=True)
df_far_locl_watr['uawkt'] = df_far_locl_watr['uawkt'].apply(wkt.loads)

df_far_locl_med = df_far_locl_med[['utilityAsset','uawkt']]
df_far_locl_med.drop_duplicates(inplace=True)
df_far_locl_med['uawkt'] = df_far_locl_med['uawkt'].apply(wkt.loads)

gdf_far = gpd.GeoDataFrame(df_far, geometry='wkt')
gdf_far.set_crs(epsg=4326, inplace=True, allow_override=True)
gdf_far_root_elec = gpd.GeoDataFrame(df_far_root_elec, geometry='rootwkt')
gdf_far_root_elec.set_crs(epsg=4326, inplace=True, allow_override=True)
gdf_far_root_watr = gpd.GeoDataFrame(df_far_root_watr, geometry='rootwkt')
gdf_far_root_watr.set_crs(epsg=4326, inplace=True, allow_override=True)
gdf_far_root_med = gpd.GeoDataFrame(df_far_root_med, geometry='rootwkt')
gdf_far_root_med.set_crs(epsg=4326, inplace=True, allow_override=True)
gdf_far_locl_elec = gpd.GeoDataFrame(df_far_locl_elec, geometry='uawkt')
gdf_far_locl_elec.set_crs(epsg=4326, inplace=True, allow_override=True)
gdf_far_locl_watr = gpd.GeoDataFrame(df_far_locl_watr, geometry='uawkt')
gdf_far_locl_watr.set_crs(epsg=4326, inplace=True, allow_override=True)
gdf_far_locl_med = gpd.GeoDataFrame(df_far_locl_med, geometry='uawkt')
gdf_far_locl_med.set_crs(epsg=4326, inplace=True, allow_override=True)

map = flood_area.explore(color='cyan',
                         style_kwds=dict(weight=5),
                         tooltip=False,
                         highlight=False,
                         name='Flood Area',
                         show=True)
gdf_far_root_elec.explore(m=map,
                          color='yellow',
                          marker_kwds=dict(radius=15),
                          tooltip=True,
                          name='Root Cause Electric Assets',
                          show=True)
gdf_far_root_watr.explore(m=map,
                          color='blue',
                          marker_kwds=dict(radius=15),
                          tooltip=True,
                          name='Root Cause Water Assets',
                          show=True)
gdf_far_root_med.explore(m=map,
                          color='red',
                          marker_kwds=dict(radius=15),
                          tooltip=True,
                          name='Root Cause Medical Assets',
                          show=True)
gdf_far_locl_elec.explore(m=map,
                          color='yellow',
                          marker_kwds=dict(radius=7),
                          tooltip=True,
                          name='Local Cause Electric Assets',
                          show=True)
gdf_far_locl_watr.explore(m=map,
                          color='blue',
                          marker_kwds=dict(radius=7),
                          tooltip=True,
                          name='Local Cause Water Assets',
                          show=True)
gdf_far_locl_med.explore(m=map,
                          color='red',
                          marker_kwds=dict(radius=7),
                          tooltip=True,
                          name='Local Cause Medical Assets',
                          show=True)
gdf_far.explore(m=map,
                color='black',
                marker_kwds=dict(radius=3),
                tooltip=True,
                name='Flooded / Affected Assets',
                show=True)
power.boundary.explore(m=map,
                       color='yellow',
                       style_kwds=dict(weight=5),
                       tooltip=False,
                       name='Electric Service Polygons',
                       show = False)
cinci_hosp.boundary.explore(m=map,
                            color='red',
                            style_kwds=dict(weight=5),
                            tooltip=False,
                            name='Medical Service Polygons',
                            show = False)
water.boundary.explore(m=map,
                       color='blue',
                       style_kwds=dict(weight=5),
                       tooltip=False,
                       name='Water Service Polygons',
                       show = False)

# folium.TileLayer("stamenterrain", show=False).add_to(map)
# folium.TileLayer("MapQuest Open Aerial", show=False).add_to(map)
folium.LayerControl().add_to(map)

print(f'{df_far.shape[0]} features found')
print(f'   {df_far_root_elec.shape[0]} electric root causes found')
print(f'   {df_far_locl_elec.shape[0]} electric local causes found')
print(f'   {df_far_root_watr.shape[0]} water root causes found')
print(f'   {df_far_locl_watr.shape[0]} water local causes found')
print(f'   {df_far_root_med.shape[0]} medical root causes found')
print(f'   {df_far_locl_med.shape[0]} medical local causes found')

map.save('cinci_map.html')

temp_types = df_far['uatype'].unique()
srvc_types = []
for t in temp_types:
    srvc_types.append(t.replace('http://schema.ufokn.org/utility-connection/v2.1/', ''))
# print(srvc_types)
# for t in srvc_types:
#     df_far.insert(4, t, '')
# print(list(df_far.columns))



df_nonasset = df_far[df_far['far'].str.contains('FeatureAtRisk', regex=True)].copy()
# print(len(df_nonasset))
df_nonasset = df_nonasset[['far']]
df_nonasset.drop_duplicates(inplace=True)
# print(len(df_nonasset))
for t in srvc_types:
    df_nonasset[t] = ''
# print(list(df_nonasset.columns))




far_unique = df_nonasset['far'].unique()
print(len((far_unique)))