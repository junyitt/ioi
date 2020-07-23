import streamlit as st
from search.landmark import *
import math
import plotly
import plotly.graph_objects as go
import pandas as pd



################### INITIALIZATION ###################

mapbox_access_token = open("mapbox_token.txt").read()
google_token = open("google_token.txt").read()

################### CUSTOM STYLE #####################
max_width = 1400
padding_top = 2
padding_right = 2
padding_left = 2
padding_bottom = 5
# COLOR
# BACKGROUND_COLOR
st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: {max_width}px;
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
</style>
""",
        unsafe_allow_html=True,
    )
#     .reportview-container .main {{
#         color: {COLOR};
#         background-color: {BACKGROUND_COLOR};
#     }}
###################### TITLE #########################

st.title('Property Search')

###################### SIDE BAR ######################

prop_num = st.sidebar.slider(label='Number of comparison', min_value=1, max_value=5, value=1, step=1)
# st.text_input()
prop_name={}
for i in range(prop_num):
    prop_name[i] = st.sidebar.text_input(label=f'Property {i+1}', key= i)

if st.sidebar.button('Show Facts Comparison'):
    #DO SOMETHING
    pass

##################### MAIN FRAME #####################
search_term = []
for i in range(prop_num):
    if prop_name[i]:
        st.write(prop_name[i])
        search_term.append(prop_name[i])
        
# g = gLandmark(search_term = [prop_name[i]+', malaysia'], r = 2)   
    
    

fig = go.Figure(
    go.Scattermapbox(
        mode = "lines", fill = "toself",
        lat = generate_circle((30,30),3)['lat'].to_list(),
        lon = generate_circle((30,30),3)['lng'].to_list(),
    )
)

fig.update_layout(
    title='Nuclear Waste Sites on Campus',
    autosize=True,
    width=1200,
    height=800,
    
    hovermode='closest',
    showlegend=True,
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=30,
            lon=30
        ),
        pitch=0,
        zoom=12,
    ),
)

st.plotly_chart(fig)

###############################################



