import plotly
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import math
import geocoder
from googleplaces import GooglePlaces, types, lang 


def PointsInCircum(r,n=100):
    pi = math.pi
    return [(math.cos(2*pi/n*x)*r,math.sin(2*pi/n*x)*r) for x in range(0,n+1)]


def generate_circle(centre_latlng, r, color = "#050e6e"):
    deg = r/110.574
    pts = PointsInCircum(deg)
    new_pts = [{"color": color, "address_short": "", "size": 0.3, "category": "radi", "lat": j[1] + centre_latlng[0], "lng": j[0] + centre_latlng[1]} for j in pts]
    df2 = pd.DataFrame(new_pts)
    return df2

def get_bbox(centre_latlng, r):
    lat, lng = centre_latlng[0], centre_latlng[1]
    dlat = r/110.574
    dlong = r/(111.32*math.cos(lat/180*math.pi))
    x = [lng-dlong, lat-dlat, lng+dlong, lat+dlat]
    return x

class Landmark():
    POI_SEARCH_TERMS = ["mall", "lrt", "park", "coffee", "restaurant"]
    
    def __init__(self, search_term, r, initial_latlng = [3.1390, 101.6869]):
        #         search_term = '3 two square' # condominium/properties name
        #         r = 2 # search radius in km
        # initial_laglng # initial search area as KL
        
        key = self.read_key()
        mb_key = self.read_mapbox_token()
        
        if not isinstance(search_term, list):
            search_term = [search_term]
            
        fdf_list = [] 
        for st in search_term:
            x, latlng = self.get_search_data(st, key, initial_latlng, size = 10, color = "#ff0011") # get landmark data for search_term

            bbox = get_bbox(latlng, r)
            circle_df = generate_circle(latlng, r+0.5)

            df_list = []
            for s in self.POI_SEARCH_TERMS: # get landmark data for all POI
                landmarks = self.search(s, latlng, r, key, size = 1, color = "#001111")
                df = pd.DataFrame(landmarks)
                df_list.append(df)
            df_list.append(pd.DataFrame(x))
            fdf = pd.concat(df_list)
            fdf = fdf.append(circle_df)
            fdf_list.append(fdf)
        fdf = pd.concat(fdf_list)
        self.fdf = fdf
        self.latlng = latlng
        self.key = key
        self.mb_key = mb_key
        
    def read_key(self):
        key = open(".mapbox_token").read()
        return key
    
    def read_mapbox_token(self):
        mb_key = open(".mapbox_token").read()
        return mb_key
    
    def search(self, search_term, latlng, r, key, size, color):
        bbox = get_bbox(latlng, r)
        g = geocoder.mapbox(search_term, bbox=bbox, key=key)
        res = [{"category": search_term, "category2": j.json.get("raw").get("properties").get("category"), 
                "address": j.address, "lat": j.latlng[0], "lng":  j.latlng[1], 
                "address_short": j.address.split(",")[0], "size": size, "color": color} for j in g]
        return res

    def get_search_data(self, search_term, key, initial_latlng, size, color):
        g = geocoder.mapbox(search_term, proximity=initial_latlng, key=key)
        
        res = [{"category": search_term, "category2": j.json.get("raw").get("properties").get("category"), 
                "address": j.address, "lat": j.latlng[0], "lng":  j.latlng[1], 
                "address_short": j.address.split(",")[0], "size": size, "color": color} for j in g]
        latlng = [res[0]["lat"], res[0]["lng"]]
        return res[0:1], latlng
    
    def plot(self):
#         cm = {}
#         cg1 = ["mall", "lrt", "park", "coffee", "restaurant"]
#         cc1 = ["#f9ed69", "#355c7d", "#b83b5e", "#a8e6cf", "#d4a5a5", "#b8b0b0"]
#         for i in range(5):
#            cm[cg1[i]]=cc1[i]
        
       
#         cc2 = ["#071a52", "#086972", "#17b978", "#a7ff83"]
#         cc = cc[:n]
#         color_discrete_map = {j:k  for j,k in zip(cats, cc)}
        fig = px.scatter_mapbox(self.fdf, lat="lat", lon="lng", 
                                color="category", size="size",
                                symbol = "aquarium",
#                                 color_discrete_map = color_discrete_map,
                                size_max=25, zoom=20, 
                                text="address_short")
        fig.update_layout(
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken=self.mb_key,
                bearing=0,
                center=dict(
                    lat=self.latlng[0],
                    lon=self.latlng[1]
                ),
                pitch=0,
                zoom=12
            ),
        )
        
        return fig

        ## SAVE
        #  plotly.offline.plot(fig, filename = 'filename_2.html', auto_open=True)
    
    
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
                "address": j.name, "lat": float(j.geo_location['lat']), "lng": float(j.geo_location['lng']), 
                "address_short": j.name, "size": size, "color": color} for j in query_result.places]
        return res
    
    def get_search_data(self, search_term, key, initial_latlng, size, color):
        res = self.search(search_term, initial_latlng, 200, key, size, color)
        latlng = [res[0]["lat"], res[0]["lng"]]
        return res[0:1], latlng
    
    
