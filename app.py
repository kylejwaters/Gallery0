# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 22:23:36 2021

@author: kylej
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import requests

def get_assets_from_address(eth_address):    
    #initialize
    ds = []
    
    #Get maximum 50 tokens each call
    offset=0
    while True:

        url = "https://api.opensea.io/api/v1/assets"
        querystring = {"owner":eth_address,
                       "order_direction":"asc","offset":str(offset),"limit":"50"}
        
        #Call API
        response = requests.request("GET", url, params=querystring)
        
        #Turn into dictionary
        dictionary = dict(response.json())
        
        #If no more assets, stop
        if len(dictionary['assets']) == 0:
            break
        else:
            ds.append(dictionary)
            offset+=50
            
    return ds

def make_cards(eth_address):

    "Get Assets for that address"    
    
    ds = get_assets_from_address(eth_address)
    
    #create dash bootstrap component cards 
    cards = []
    creators = {}
    #create list of cards 
    for asset_dict in ds:
        
        #Loop over assets
        for asset in asset_dict["assets"]:
            
            name = asset["name"]
            if name == None:
                name = asset["asset_contract"]["name"] + " " + asset["token_id"] 
            
            creator = asset["creator"]
            if creator:
                creators[name] = creator
            
            opensea_link = asset["permalink"]
      
            if asset["animation_url"]==None or asset["animation_url"].endswith("html"):
                img = asset["image_url"]
            else:    
                img = asset["animation_url"]
                
                #no mp4s
                if img.endswith(".mp4"):
                    if asset["image_original_url"]==None:
                        img = asset["image_url"]
                    else:
                        img = asset["image_original_url"]
            
            if asset["collection"]["featured_image_url"]:
                
                if asset["collection"]["name"]=="SuperRare":
                    collection_img=asset["collection"]["featured_image_url"]
                else:
                    collection_img=asset["collection"]["large_image_url"]
                    
            else:
                if asset["collection"]["name"]=="Rarible":
                    collection_img ="https://lh3.googleusercontent.com/FG0QJ00fN3c_FWuPeUr9-T__iQl63j9hn5d6svW8UqOmia5zp3lKHPkJuHcvhZ0f_Pd6P2COo9tt9zVUvdPxG_9BBw=w128"
                else:            
                    collection_img="https://storage.googleapis.com/opensea-static/opensea-profile/33.png"
            
            card = dbc.Card(
               [
                   dbc.CardImg(src="{}".format(img), className = 'align-self-center'),
                   dbc.Button(
                       color="grey",
                       
                       children=[html.Img(src=collection_img,style={"max-width":"30px","max-height":"30px"}),
                        html.A("{}".format(name), href="{}".format(opensea_link),style={"font-size":"14px","color":"black"})],
                       
                       ),
               ]#,
               #style={"width": "10rem"}
               #,outline=False, className="col-md-3"
               )
            ##append
            cards.append(card)
    
    return cards
            
########### Initiate the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server
app.title="FORM"

########### Set up the layout
app.layout = html.Div(
    [
     html.H1("FORM",style={"font-family": "Consolas","text-align":"center","font-size":"80px"}),         
     html.H4("Enter Ethereum Address",style={"font-family": "Consolas","font-size":"20px","text-align":"center"}),
     
     html.Div([
        html.Div([dcc.Input(id='input-on-submit', type='text')],style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
        html.Div([html.Button('Submit', id='submit-val')],style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
        html.Br(),
        dbc.Spinner(html.Div(id="loading-output2")),
    html.Br(),
    html.Br(),
  
    dbc.CardColumns(id="cards", style={'padding': '25px'})]),
     
    html.A(''),
    html.Br(),
    html.A('© 2021 -- FORM',style={"font-family": "Consolas"})
    ]
)   

@app.callback(
    Output("cards", "children"),
    [Input("submit-val","n_clicks")],
    [State('input-on-submit', 'value')]
)

def load_output(n,value):
    if value:
        return make_cards(eth_address=value)
    return ""

if __name__ == '__main__':
    app.run_server()            
      

