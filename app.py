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
    
    #create list of cards 
    for asset_dict in ds:
        
        #Loop over assets
        for asset in asset_dict["assets"]:
            
            name = asset["name"]
            
            if name == None:
                name = asset["asset_contract"]["name"] + " " + asset["token_id"] 
            
            opensea_link = asset["permalink"]
            
            if asset["animation_url"]==None:
                img = asset["image_url"]
            else:    
                img = asset["animation_url"]
                
                #no mp4s
                if img.endswith(".mp4"):
                    img = asset["image_original_url"]
            
            card = dbc.Card(
               [
                   dbc.CardImg(src="{}".format(img), className = 'align-self-center'),
                   dbc.CardBody(
                       [
                           html.H5("{}".format(name),style={"font-family": "Consolas","font-size":"16px"})
                           ]
                       ),
                   dbc.Button("View on OpenSea", color="grey",href="{}".format(opensea_link),style={"font-size":"10px"}),
               ],
               style={"width": "18rem"}
               ,outline=True,color="dark",className="col-md-4"
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
        dbc.Spinner(html.Div(id="loading-output")),
    html.Br(),
    html.Br(),
  
    dbc.CardColumns(id="cards")]),
     
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
    if n:
        return make_cards(eth_address=value)
    return ""

if __name__ == '__main__':
    app.run_server()            
         


