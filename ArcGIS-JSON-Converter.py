import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
import json

st.set_page_config(page_title="ArcGIS to GeoJSON Converter", layout="wide")

st.title("ArcGIS JSON to GeoJSON Converter")

uploaded_file = st.file_uploader("Upload ArcGIS JSON file", type=['json'])

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        
        if 'features' in data:
            features_list = []
            
            for feat in data['features']:
                attributes = feat.get('attributes', {})
                geometry_dict = feat.get('geometry', {})
                
                geometry = None
                if 'paths' in geometry_dict:
                    geometry = LineString(geometry_dict['paths'][0])
                elif 'x' in geometry_dict and 'y' in geometry_dict:
                    geometry = Point(geometry_dict['x'], geometry_dict['y'])
                
                if geometry:
                    attributes['geometry'] = geometry
                    features_list.append(attributes)

            if features_list:
                df = pd.DataFrame(features_list)
                # Input CRS: UTM Zone 38N (EPSG:32638)
                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:32638")
                
                # Transform to WGS84 (EPSG:4326)
                gdf = gdf.to_crs(epsg=4326)

                st.info(f"Total features processed: {len(gdf)}")
                st.subheader("Data Preview")
                st.dataframe(gdf.drop(columns='geometry').head())

                geojson_data = gdf.to_json()
                st.download_button(
                    label="Download GeoJSON",
                    data=geojson_data,
                    file_name="output.geojson",
                    mime="application/json"
                )
            else:
                st.warning("No valid geometry found in the provided file.")
        else:
            st.error("Invalid format: 'features' key not found.")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")