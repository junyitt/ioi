import plotly
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math
import geocoder
from googleplaces import GooglePlaces, types, lang 

def hex_to_rgb(hex_color: str, opacity) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = hex_color * 2
    x = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    fillcolor=f"rgba{(*x, opacity)}"
    return fillcolor

def PointsInCircum(r,n=100):
    pi = math.pi
    return [(math.cos(2*pi/n*x)*r,math.sin(2*pi/n*x)*r) for x in range(0,n+1)]


def generate_circle(centre_latlng, r, color = "#050e6e", category = "area", name = "name"):
    deg = r/110.574
    pts = PointsInCircum(deg)
    new_pts = [{"color": color, "address_short": "", "size": 0.3, 
                "category": category, "legendgroup": name, "name": name, 
                "lat": j[1] + centre_latlng[0], "lng": j[0] + centre_latlng[1]} for j in pts]
    df2 = pd.DataFrame(new_pts)
    return df2

def get_bbox(centre_latlng, r):
    lat, lng = centre_latlng[0], centre_latlng[1]
    dlat = r/110.574
    dlong = r/(111.32*math.cos(lat/180*math.pi))
    x = [lng-dlong, lat-dlat, lng+dlong, lat+dlat]
    return x

class Landmark():
    ST_COLORS = ["#FC1520", "#FFC414", "#37ED00", "#4089FC", "#E028EF"]*100
    POI_SEARCH_TERMS = ["mrt", "lrt", "park", "mall", "coffee", "restaurant"]
    POI_COLORS = ["#EF6B5F", "#FC864B", "#2ABF86", "#08B8DB", "#7E6A52", "#BC7756"]
    
    def __init__(self, search_term, r, initial_latlng = [3.1390, 101.6869]):
        #         search_term = '3 two square' # condominium/properties name
        #         r = 2 # search radius in km
        # initial_laglng # initial search area as KL
        
        key = self.read_key()
        mb_key = self.read_mapbox_token()
        
        if not isinstance(search_term, list):
            search_term = [search_term]
        
        N = len(search_term)
        st_colors = self.ST_COLORS[:N]
        fdf_list = [] 
        for st, st_cl in zip(search_term, st_colors):
            x, latlng = self.get_search_data(st, key, initial_latlng, size = 10, color = st_cl) # get landmark data for search_term
            bbox = get_bbox(latlng, r)
            circle_df = generate_circle(latlng, r+0.5, st_cl, "area: "+st, st)

            df_list = []
            for s, cl in zip(self.POI_SEARCH_TERMS, self.POI_COLORS): # get landmark data for all POI
                landmarks = self.search(s, latlng, r, key, size = 1, color = cl)
                df = pd.DataFrame(landmarks)
                df_list.append(df)
            df_list.append(pd.DataFrame(x))
            fdf = pd.concat(df_list)
            fdf = fdf.append(circle_df)
            fdf_list.append(fdf)
        fdf = pd.concat(fdf_list)
        self.fdf = fdf
        self.st = search_term
        self.latlng = latlng
        self.key = key
        self.mb_key = mb_key
        
    def read_key(self):
        key = open("mapbox_token.txt").read()
        return key
    
    def read_mapbox_token(self):
        mb_key = open("mapbox_token.txt").read()
        return mb_key
    
    def search(self, search_term, latlng, r, key, size, color, name):
        bbox = get_bbox(latlng, r)
        g = geocoder.mapbox(search_term, bbox=bbox, key=key)
        res = [{"category": search_term, "category2": j.json.get("raw").get("properties").get("category"), 
                "address": j.address, "lat": j.latlng[0], "lng":  j.latlng[1], 
                "address_short": j.address.split(",")[0], "size": size, "color": color,
                "legendgroup": j.address.split(",")[0], "name": j.address.split(",")[0]} for j in g]
        return res

    def get_search_data(self, search_term, key, initial_latlng, size, color):
        g = geocoder.mapbox(search_term, proximity=initial_latlng, key=key)
        
        res = [{"category": search_term, "category2": j.json.get("raw").get("properties").get("category"), 
                "address": j.address, "lat": j.latlng[0], "lng":  j.latlng[1], 
                "address_short": j.address.split(",")[0], "size": size, "color": color,
                "legendgroup": j.address.split(",")[0], "name": j.address.split(",")[0]} for j in g]
        latlng = [res[0]["lat"], res[0]["lng"]]
        return res[0:1], latlng
    
    def plot(self):
        fdf = self.fdf
        mapbox_access_token = self.mb_key
        latlng = self.latlng
        
        fig = px.scatter_mapbox(fdf, lat="lat", lon="lng", 
                                color="category", size = "size",
                                size_max=25, zoom=20, 
                                text="address_short")
        fig.update_layout(
            autosize=True,
            width=1200,
            height=800,
            hovermode='closest',
            showlegend=True,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=latlng[0],
                    lon=latlng[1]
                ),
                pitch=0,
                zoom=12
            ),
        )
        return fig
    
    def plot2(self):
        df2 = self.fdf.copy()
        mapbox_access_token = self.mb_key
        latlng = self.latlng
        st = self.st
        
        u1 = df2["category"].str.contains('|'.join(st))
        st_df0 = df2.loc[u1]
        area_df = df2.loc[df2["category"].str.contains("area:")]
        st_df = df2.loc[df2["category"].isin(st)]
        POI_SEARCH_TERMS = ["mrt", "lrt", "park", "mall", "coffee", "restaurant"]
        poi_df = df2.loc[df2["category"].isin(POI_SEARCH_TERMS)]

        fig = go.Figure()

        ## SEARCH TERM
        for add_j in st_df.address_short.unique():
            u1 = st_df.address_short == add_j
            st_df_sub = st_df.loc[u1]
            fig.add_trace(go.Scattermapbox(
                    lat=st_df_sub["lat"],
                    lon=st_df_sub["lng"],
                    legendgroup=st_df_sub["legendgroup"].values[0],
                    name=st_df_sub["legendgroup"].values[0],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        symbol="star",
                        size=st_df_sub["size"],
                        color=st_df_sub["color"],
                        opacity=0.8
                    ),
                    text = st_df_sub["address"]
                ))

        for area_j in area_df.category.unique():
            u1 = area_df.category == area_j
            area_df_sub = area_df.loc[u1]
            fig.add_trace(
                go.Scattermapbox(
                    mode = "lines", 
                    line = dict(width=1),
                    fill = "toself",
                    fillcolor = area_df_sub["color"].apply(lambda x: hex_to_rgb(x, 0.1)).tolist()[0],
                    opacity=0.05,
                    legendgroup=area_df_sub["legendgroup"].values[0],
                    name=area_df_sub["legendgroup"].values[0],
        #             marker = dict(
        #                 color = area_df_sub["color"].apply(lambda x: hex_to_rgb(x, 0.1)).tolist(),
        #             ),
                    lat = area_df_sub["lat"].tolist(),
                    lon = area_df_sub["lng"].tolist(),
                )
            )

        ## POI
        for cat_j in poi_df.category.unique():
            if cat_j == "mall":
                visible = True
            else:
                visible = "legendonly"
            u1 = poi_df.category == cat_j
            poi_df_sub = poi_df.loc[u1]
            fig.add_trace(go.Scattermapbox(
                    lat=poi_df_sub["lat"],
                    lon=poi_df_sub["lng"],
                    legendgroup=poi_df_sub["category"].values[0],
                    name=poi_df_sub["category"].values[0],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        symbol="circle",
                        size=poi_df_sub["size"]+7,
                        color=poi_df_sub["color"],
                        opacity=0.8
                    ),
                    visible=visible,
                    text = poi_df_sub["address"]
                ))
            
        fig.update_layout(
#             title='Nuclear Waste Sites on Campus',
            autosize=True,
            width=1200,
            height=800,
            hovermode='closest',
            showlegend=True,

            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=latlng[0],
                    lon=latlng[1]
                ),
                pitch=0,
                zoom=12,
            ),
        )
        return fig
    
    
class gLandmark(Landmark):
    def read_key(self):
        key = open("google_token.txt").read()
        return key
        
    def search(self, search_term, latlng, r, key, size, color):
        bbox = get_bbox(latlng, r)
        google_places = GooglePlaces(key) 
        query_result = google_places.nearby_search( 
            lat_lng ={'lat': latlng[0], 'lng': latlng[1]}, 
            radius = r*1000, 
            name=search_term,
            types =[types.TYPE_POINT_OF_INTEREST])
        category = search_term
        category2 = search_term
        res = [{"category": category, "category2": category2, 
                "address": j.name, 
                "lat": float(j.geo_location['lat']), "lng": float(j.geo_location['lng']), 
                "legendgroup": category, "name": category, 
                "address_short": j.name, "size": size, "color": color} for j in query_result.places]
        return res
    
    def get_search_data(self, search_term, key, initial_latlng, size, color):
        res = self.search(search_term, initial_latlng, 200, key, size, color)
        latlng = [res[0]["lat"], res[0]["lng"]]
        return res[0:1], latlng
    
    
