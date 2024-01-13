from os.path import join, isdir
from os import mkdir

import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium

from shapely.geometry import shape
from shapely.ops import transform

from numpy import uint32
from pandas import DataFrame

from functions.initiate_reprojection import project
from functions.raster_values import GetRasterValues
from functions.download_dataset import download_drive

# Preparation
if not isdir(join('dataset')):
    mkdir(join('dataset'))
    mkdir(join('dataset', 'forest_loss'))
    download_drive('1-pnnuh2MFTNJ-RINvCAKyS0xCbw8Pvk3', join('dataset', 'forest_loss'))

st.session_state.valid_poly = None
st.session_state.n_poly = None

m = folium.Map(location = [-3.18, 117.76], zoom_start=5)
Draw(
    export=False,
    draw_options={
        'polyline': False,
        'polygon': False,
        'circle': False,
        'marker': False,
        'circlemarker': False,
        'rectangle': True
    }
    ).add_to(m)

st.title('Yearly Deforested Dashboard')

output = st_folium(m, width=700, height=500)
st.session_state.n_poly = len(output['all_drawings']) if output['all_drawings'] else None
st.session_state.valid_poly = output['all_drawings'][0] if output['all_drawings'] else None

if st.session_state.valid_poly:
    try:
        assert st.session_state.n_poly <=1
        rectangle_info = shape(st.session_state.valid_poly['geometry'])
        rectangle_psm = transform(project, rectangle_info)
        rectangle_area = uint32(rectangle_psm.area * 0.0001)
        st.write(f'{rectangle_area} hectare')

        try:
            assert rectangle_area < 300000

            if st.button('Download Laporan'):
                result = GetRasterValues('forest_loss', [rectangle_info])
                result_df = DataFrame(
                    result.items(),
                    columns = ['Year', 'Deforested area (ha)']
                    )
                result_df['Cummulative Deforested area (ha)'] = result_df['Deforested area (ha)'].cumsum()
                st.bar_chart(
                    data = result_df, 
                    x = 'Year',
                    y = 'Deforested area (ha)'
                    )
                st.line_chart(
                    data = result_df,
                    x = 'Year',
                    y = 'Kumulatif Deforested area (ha)'
                )
        except AssertionError:
            st.error('You defined an area of more than 300 thousands hectare')

    except AssertionError:
        st.error('You defined more than one area!')
else:
    st.error('You have not defined an area!')