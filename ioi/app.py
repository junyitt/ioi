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

prop_num = st.sidebar.slider(label='Number of comparison', min_value=1, max_value=5, value=2, step=1)
radius = st.sidebar.slider(label='Proximity radius', min_value=1, max_value=20, value=3, step=1)

# st.text_input()
suggestions = ["PJ Midtown", "121 Residences", "Ryan & Miho", "Lumi Tropicana"]
prop_name={}
for i in range(prop_num):
    if i < 1:
        prop_name[i] = st.sidebar.text_input(value="",label=f'Property {i+1}', key=i)
    else:
        print(suggestions[i-1])
        prop_name[i] = st.sidebar.text_input(value=suggestions[i-1], label=f'Property {i+1}', key=i)

if st.sidebar.button('Show Facts Comparison'):
    #DO SOMETHING
    pass

##################### MAIN FRAME #####################
search_term = []
for i in range(prop_num):
    if prop_name[i]:
        search_term.append(prop_name[i])
        
if len(search_term) > 0:
    st.write("Searching for: {}".format(", ".join(search_term)))
        
try:
    g = gLandmark(search_term = [s for s in search_term], r = radius)   
    fig = g.plot2()
    st.plotly_chart(fig)
except Exception as err:
    if len(search_term) > 0:
        st.write("Error searching for: {}".format(", ".join(search_term)))
    print(err)
    ""
###############################################



