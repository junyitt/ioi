import streamlit as st
from search.landmark import *
import math
import difflib
import plotly
import plotly.graph_objects as go
import pandas as pd



################### INITIALIZATION ###################

mapbox_access_token = open("mapbox_token.txt").read()
google_token = open("google_token.txt").read()


def read_data(csv):
    df = pd.read_csv(csv)
    return df

def match_input(text):
    lookup = difflib.get_close_matches(text.lower(), df['PropName'].str.lower(), n=1, cutoff=0.6)
    if len(lookup)>0:
        return lookup[0].title()
    else:
        st.write(f'No match found for {text}. Print provide more concise property name')
        return None

df = read_data('condo.csv')
df['region'] = df['Address'].apply(lambda x: x.split(',')[-1])

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

prop_num = st.sidebar.slider(label='Number of comparison', min_value=1, max_value=3, value=2, step=1)
radius = st.sidebar.slider(label='Proximity radius', min_value=1, max_value=20, value=3, step=1)

# st.text_input()
suggestions = ["162 residency", "Selayang Makmur Apartment", "", "", ""]
prop_name={}
user_input={}
for i in range(prop_num):
    user_input[i] = st.sidebar.text_input(value=suggestions[i], label=f'Property {i+1}', key=i)
    prop_name[i]=None
    if user_input[i]:
        match = match_input(user_input[i])
        if match:
            region = df['region'][df['PropName']==match].iloc[0]
            prop_name[i] = ' '.join([match, region])
if st.sidebar.button('Show Facts Comparison'):
    #DO SOMETHING
    pass

##################### MAIN FRAME #####################
@st.cache(suppress_st_warning=True)
def plot_map(search_term):
    try:
        g = gLandmark(search_term = [s for s in search_term], r = radius)   
        fig = g.plot2()
        return fig
    except:
        return None

search_term = []
for i in range(prop_num):
    if prop_name[i]:
        search_term.append(prop_name[i])
        
if len(search_term) > 0:
    st.write("Searching for: {}".format(", ".join(search_term)))

fig = plot_map(search_term)
if fig:
    st.plotly_chart(fig)
else:
    st.write("Error searching for: {}".format(", ".join(search_term)))
###############################################
