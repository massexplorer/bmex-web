import time
import numpy as np
import math
from datetime import date, datetime

import dash
from dash import dcc, MATCH, ALL, html
from dash.dependencies import Input, Output, State
import json
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import utils.dash_reusable_components as drc
import utils.figures as figs
import utils.bmex as bmex
from utils.bmex_views import *
import utils.gpe as gpe
import utils.rbm as rbm
from utils.views_class import View
from utils.sidebar_class import Sidebar

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import random as rand
import h5py
import base64, io
import re
import zipfile
import plotly.io as pio
import sqlite3 as sl
import string


default = {"dimension": 'landscape', "chain": 'isotopic', "quantity": 'BE', "dataset": ['EXP'], 
           "colorbar": 'linear', "wigner": 0, "proton": [None], "neutron": [None], "nucleon": [None], 
           "range": {"x": [None, None], "y": [None, None]}, "colorbar_range": [None, None]}


app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

app.config.suppress_callback_exceptions=True

app.title = "Bayesian Mass Explorer"

server = app.server

app.layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        # .container class is fixed, .container.scalable is scalable
        html.Div(
            className="banner",
            children=[
                # Change App Name here
                html.Div(
                    className="container scalable",
                    children=[
                        # Change App Name here
                        html.H2(
                            id="banner-title",
                            children=[
                                html.A(
                            id="banner-logo",
                            children=[
                                html.Img(src=app.get_asset_url("BMEX-logo-beta.png"))
                            ],
                            href="https://bmex.dev",
                        )
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="issues-report",
                    children=[
                        # html.P("Report Issues", className="issues-title"),
                        html.A(
                            id="issues-logo",
                            children=[
                                html.Img(src=app.get_asset_url("Submit-Issues.png"),className="issues-img")
                            ],
                            href="https://github.com/massexplorer/bmex-web/issues/new", 
                            className="issues-img-div"                 
                        )   
                    ],
                ),
            ]
        ),
        html.Div(id='page-content'),
        dcc.Store(id='intermediate-value'),
        dcc.Store(id='intermediate-colorbar-range'),
        html.P(id='placeholder', hidden=True),
        dcc.Store(id='url-store'),
        #dcc.Store(id="linkmemory", storage_type='memory', data=json.dumps("")),
        dcc.Store(id='viewsmemory', storage_type='memory',
            data=json.dumps([default]),
        ),
        dcc.Store(id='triggerGraph', data=json.dumps("update")),
        dcc.ConfirmDialog(id='confirm', message='Warning! Are you sure you want to delete this view?'),
        dcc.Download(id="download-figs"),
    ]
)

@app.callback(
    Output('url-store','data'),
    Output('page-content','children'),
    [Input('url','pathname')]
    )
def display_page(pathname):
    if(pathname[:7] == "/masses"):
        out = masses_view()
    elif(pathname == "/gpe"):
        out = gpe_view()
    elif(pathname == "/pesnet"):
        out = pesnet_view()
    elif(pathname == "/emulator"):
        out = emu_view()
    else:
        out = html.Div(
            id="body",
            className="container scalable",
            children=[html.P("How did you get here? Click the banner to make it back to safety!")])
    return pathname, out

@app.callback(
    Output("clipboard", "content"),
    Input("viewsmemory", "data")
)
def link_update(views):   
    hash = ''.join(rand.choices(string.ascii_letters, k=6))
    # return "https://beta.bmex.dev/masses/"+base64.urlsafe_b64encode(views.encode()).decode()
    return "https://beta.bmex.dev/masses/"+hash

@app.callback(
    Output("placeholder", "hidden"),
    State("clipboard", "content"),
    State("viewsmemory", "data"),
    Input("clipboard", "n_clicks"),  
    prevent_initial_call=True, 
)
def hash_store(link, views, clicks):
    try:
        hash = link.split("masses/")[1]
    except:
        raise PreventUpdate
    con = sl.connect('view_hashes.db')
    with con:
        try:
            con.execute("""INSERT INTO hashes (hash, info) VALUES (?,?);""", (hash, views))
        except:
            con.execute("""
                CREATE TABLE hashes (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    hash TEXT,
                    info TEXT
                );
            """)
            con.execute("""INSERT INTO hashes (hash, info) VALUES (?,?);""", (hash, views))


@app.callback(
    Output('confirm', 'displayed'),
    Input({"type": 'delete-button', "index": ALL}, "n_clicks"),
    State("viewsmemory", "data")
)
def display_confirm(delete, json_cur_views):
    try:
        if delete[0] > 0:
            l = len(json.loads(json_cur_views))
            if l < 2:
                pass
            else:
                return True
    except:
        pass


@app.callback(
    Output("download-figs", "data"),
    Input("download-button", "n_clicks"),
    State("viewsmemory", "data"),
    prevent_initial_call=True,
)
def download(n_clicks, json_cur_views):
    try:
        n_clicks>0
    except:
        raise PreventUpdate
    cur_views = json.loads(json_cur_views)
    zip_file_name = "BMEX-"+str(date.today().strftime("%b-%d-%Y"))+"_"+str(datetime.now().strftime("%H-%M-%S"))+".zip"
    def write_zip(bytes_io):
        with zipfile.ZipFile(bytes_io, mode="w") as zf:
            for i in range(len(cur_views)):
                filename = "Fig_"+str(i+1)+".pdf"
                buf = io.BytesIO()
                fig = View(cur_views[i]).plot().figure
                pio.full_figure_for_development(fig, warn=False)

                fig.update_layout(
                    font={"color": "#000000"}, title=None,
                    xaxis=dict(linecolor='black', showgrid=False,  minor=dict(showgrid=False), mirror="ticks", range=cur_views[i]['range']['x']),
                    yaxis=dict(linecolor='black', showgrid=False, minor=dict(showgrid=False), mirror="ticks", range=cur_views[i]['range']['y']),
                    plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
                
                fig.update_traces(dict(marker=dict(color='#000000')), dict(marker=dict(color='#ffffff')))

                fig.write_image(buf, format='pdf', engine="kaleido")
                zf.writestr(filename, buf.getvalue())
    return dcc.send_bytes(write_zip, zip_file_name)


@app.callback(
    Output({'type': 'graph','index': ALL}, "figure"),
    Output('intermediate-colorbar-range', 'data'),
    State({'type': 'graph','index': ALL}, "figure"),
    State("tabs", "value"),
    State("viewsmemory", "data"),
    Input("link-colorbar-button", "n_clicks"),
    Input({'type': 'rescale-colorbar-button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def figure_update(figures, tab_n, json_cur_views, link_colorbar, rescale_colorbar):
    new_figures = figures
    cur_views = json.loads(json_cur_views)

    # write a function that inputs an array of different data types and only keeps the floats
    def float_array(array):
        return np.array( [array[i] for i in range(len(array)) if type(array[i])==type(1.0)] )
    
    if "link-colorbar-button" == dash.callback_context.triggered_id:
        mins = np.array( [figures[i]['data'][0]['zmin'] for i in range(len(figures)) if cur_views[i]['dimension']=='landscape'] )
        maxes = np.array( [figures[i]['data'][0]['zmax'] for i in range(len(figures)) if cur_views[i]['dimension']=='landscape'] )
        print(mins, maxes)
        try:
            minz, maxz = min(mins), max(maxes)
        except:
            raise PreventUpdate
        for i in range(len(figures)):
            new_figures[i]['data'][0]['zmin'] = minz
            new_figures[i]['data'][0]['zmax'] = maxz

        return new_figures, {"index": 'ALL', "range": [minz, maxz]}
    
    try:
        dash.callback_context.triggered_id['type']
    except:
        print('ERROR_1')
        raise PreventUpdate
    
    if "rescale-colorbar-button" == dash.callback_context.triggered_id['type']:
        if type(rescale_colorbar[0])==type(1):
            n = int(tab_n[3])
            new_figures = figures
            x_range, y_range = cur_views[n-1]['range']['x'], cur_views[n-1]['range']['y']
            print(x_range, y_range)
            if x_range[0] == None:
                x_range[0] = -9999
            if x_range[1] == None:
                x_range[1] = 9999
            if y_range[0] == None:
                y_range[0] = -9999
            if y_range[1] == None:
                y_range[1] = 9999
            xmin, xmax = math.floor(x_range[0])+math.floor(x_range[0])%2, math.ceil(x_range[1])-math.ceil(x_range[1])%2
            ymin, ymax = math.floor(y_range[0])+math.floor(y_range[0])%2, math.ceil(y_range[1])-math.ceil(y_range[1])%2
            x, y = np.array(figures[n-1]['data'][0]['x']), np.array(figures[n-1]['data'][0]['y'])
            xmin_i, xmax_i = int(np.where(x>=xmin)[0][0]), int(np.where(x<=xmax)[0][-1])+1
            ymin_i, ymax_i = int(np.where(y>=ymin)[0][0]), int(np.where(y<=ymax)[0][-1])+1
            values = float_array(np.array(figures[n-1]['data'][0]['z'])[ymin_i:ymax_i, xmin_i:xmax_i].flatten())
            val_min, val_max = np.min(values), np.max(values)
            new_figures[n-1]['data'][0]['zmin'] = val_min
            new_figures[n-1]['data'][0]['zmax'] = val_max

            return new_figures, {"index": n-1, "range": [val_min, val_max]}

        raise PreventUpdate


@app.callback(
    [
        Output("viewsmemory", "data"),
        Output("tabs", "children"),
        Output("triggerGraph", "data"),
        Output("tabs", "value"),
        Output("tabs_output", "children"),
    ],
    [
        State("viewsmemory", "data"),
        State("tabs", "children"),
        State("tabs_output", "children"),
        #url
        Input("url-store", "data"),
        #tabs_output
        Input("tabs", "value"),
        #colorbar_range
        Input('intermediate-colorbar-range', 'data'),
        #relayout_data
        Input({'type': 'graph','index': ALL}, "relayoutData"),
        #new_plot
        Input({'type': 'new-button','index': ALL},"n_clicks"),
        #new_series
        Input({"type": 'series-button', "index": ALL}, "n_clicks"),
        #series_tabs
        Input({'type': 'series_tabs','index': ALL}, "value"),
        #delete_series
        Input({'type': 'delete-series-button','index': ALL}, "n_clicks"),
        #delete_plot
        Input('confirm', 'submit_n_clicks'),
        #reset_page
        Input({"type": 'reset-button', "index": ALL}, "n_clicks"),
        #dropdowns
        Input({'type': 'dropdown-dimension', 'index': ALL}, 'value'),
        Input({'type': 'dropdown-1D', 'index': ALL}, 'value'),
        Input({'type': 'dropdown-quantity', 'index': ALL}, 'value'),
        Input({'type': 'dropdown-dataset', 'index': ALL}, 'value'),
        Input({'type': 'input-protons', 'index': ALL}, 'value'),
        Input({'type': 'input-neutrons', 'index': ALL}, 'value'),
        Input({'type': 'input-nucleons', 'index': ALL}, 'value'),
        Input({'type': 'dropdown-colorbar', 'index': ALL}, 'value'),
        Input({'type': 'radio-wigner', 'index': ALL}, 'value'),
    ]
)
def main_update(
    json_cur_views, cur_tabs, cur_sidebar, url, tab_n, colorbar_range, relayout_data, new_button, series_button, series_tab, delete_series, delete_button, 
    reset_button, dimension, oneD, quantity, dataset, protons, neutrons, nucleons, colorbar, wigner):

    cur_views = json.loads(json_cur_views)
    n = int(tab_n[3])
    if len(series_tab) == 0:
        series_n = 1
    else:
        series_n = int(series_tab[0][3])

    #print(dash.callback_context.triggered_id)

    #url
    if "url-store" == dash.callback_context.triggered_id:
        # if(len(url)>10):
        #     loaded_views = json.loads(base64.urlsafe_b64decode(url[8:].encode()).decode())
        #     new_tabs = [dcc.Tab(label=str(i+1),value='tab'+str(i+1),className='custom-tab', selected_className='custom-tab--selected') for i in range(len(loaded_views))]
        #     return  [
        #         json.dumps(loaded_views), 
        #         new_tabs,
        #         json.dumps('update'),
        #         tab_n,
        #         Sidebar(loaded_views[n-1]).show(),
        #     ]
        if(len(url)>10):
            con = sl.connect('view_hashes.db')
            hash = url[8:]
            with con:
                loaded_views = json.loads(list(con.execute("SELECT info FROM hashes WHERE hash == (?)", (hash,)))[0][0])
            new_tabs = [dcc.Tab(label=str(i+1),value='tab'+str(i+1),className='custom-tab', selected_className='custom-tab--selected') for i in range(len(loaded_views))]
            return  [
                json.dumps(loaded_views), 
                new_tabs,
                json.dumps('update'),
                tab_n,
                Sidebar(loaded_views[n-1]).show(), 
            ]
        else:
            new_tabs = [dcc.Tab(label=str(i+1),value='tab'+str(i+1),className='custom-tab', selected_className='custom-tab--selected') for i in range(len(cur_views))]
            return  [
                json_cur_views, 
                new_tabs,
                json.dumps("update"),
                tab_n,
                Sidebar(cur_views[n-1], 1, len(new_tabs)).show(),
            ]

    #tabs_change
    if "tabs" == dash.callback_context.triggered_id:
        return  [
            json_cur_views, 
            cur_tabs,
            json.dumps("dontupdate"),
            tab_n, 
            Sidebar(cur_views[n-1], 1, len(cur_tabs)).show(),
        ]

    #delete_plot
    if 'confirm' == dash.callback_context.triggered_id:
        if  len(cur_views)>1:
            new_views = cur_views
            new_views.pop(n-1)
            new_tabs = cur_tabs
            new_tabs.pop(-1)
            return [
                json.dumps(new_views), 
                new_tabs,
                json.dumps("update"), #graph
                "tab"+str(len(new_views)),
                Sidebar(new_views[-1], 1, len(new_tabs)).show(),
            ]
        else:
            raise PreventUpdate

    #colorbar_range
    if 'intermediate-colorbar-range' == dash.callback_context.triggered_id:
        if colorbar_range == None:
            raise PreventUpdate
        new_views = cur_views
        if colorbar_range['index'] == 'ALL':
            for i in range(len(new_views)):
                new_views[i]['colorbar_range'] = colorbar_range['range']
        else:
            new_views[colorbar_range['index']]['colorbar_range'] = colorbar_range['range']
        return [
            json.dumps(new_views),
            cur_tabs,
            json.dumps("update"), #graph
            tab_n,
            Sidebar(new_views[n-1], series_n, len(cur_tabs)).show()
        ]


    try:
        dash.callback_context.triggered_id['type']
    except:
        print('ERROR')
        raise PreventUpdate


    #relayout_data
    if 'graph' == dash.callback_context.triggered_id['type']:
        new_views = cur_views
        for i in range(len(new_views)):
            if relayout_data[i] == None:
                continue
            try:
                new_views[i]['range']['x'][0], new_views[i]['range']['x'][1] = relayout_data[i]['xaxis.range[0]'], relayout_data[i]['xaxis.range[1]']
                new_views[i]['range']['y'][0], new_views[i]['range']['y'][1] = relayout_data[i]['yaxis.range[0]'], relayout_data[i]['yaxis.range[1]']
            except:
                if relayout_data[i] == {'dragmode': 'pan'} or relayout_data[i] == {'dragmode': 'zoom'}:
                    raise PreventUpdate
                new_views[i]['range']['x'][0], new_views[i]['range']['x'][1] = None, None
                new_views[i]['range']['y'][0], new_views[i]['range']['y'][1] = None, None
        return [
            json.dumps(new_views),
            cur_tabs,
            json.dumps("noupdate"), #graph
            tab_n,
            Sidebar(new_views[n-1], series_n, len(cur_tabs)).show()
        ]

    #new_plot
    if 'new-button' == dash.callback_context.triggered_id['type']:
        if len(cur_tabs)>3 or type(new_button) != type([1]):
            raise PreventUpdate
        new_views = cur_views
        new_views.append(default)
        new_tabs = cur_tabs
        new_tabs.append(dcc.Tab(label=str(len(cur_tabs)+1), value='tab'+str(len(cur_tabs)+1), className='custom-tab', selected_className='custom-tab--selected'))

        return [
            json.dumps(new_views),
            new_tabs,
            json.dumps("update"), #graph
            "tab"+str(len(new_tabs)),
            Sidebar(new_views[-1], 1, len(new_tabs)).show(),
        ]
    
    #delete_series
    if 'delete-series-button' == dash.callback_context.triggered_id['type']:
        l = len(cur_views[n-1]['proton'])
        if  l>1:
            new_views = cur_views
            new_views[n-1]['proton'].pop(series_n-1)
            new_views[n-1]['neutron'].pop(series_n-1)
            new_views[n-1]['nucleon'].pop(series_n-1)
            new_views[n-1]['dataset'].pop(series_n-1)
            return [
                json.dumps(new_views), 
                cur_tabs,
                json.dumps("update"), #graph
                tab_n,
                Sidebar(new_views[n-1], series_n-1+math.ceil(abs(series_n-l)/10), len(cur_tabs)).show(),
            ]
        else:
            raise PreventUpdate
    
    #series_tabs
    if "series_tabs" == dash.callback_context.triggered_id['type']:
        if series_n==0:
            new_views = cur_views
            new_views[n-1]['proton'].append(default['proton'][0])
            new_views[n-1]['neutron'].append(default['neutron'][0])
            new_views[n-1]['nucleon'].append(default['nucleon'][0])
            new_views[n-1]['dataset'].append(default['dataset'][0])
            return [
                json.dumps(new_views), 
                cur_tabs,
                json.dumps("update"),
                tab_n,
                Sidebar(new_views[n-1], "new", len(cur_tabs)).show(),
            ]
        return [
            json.dumps(cur_views), 
            cur_tabs,
            json.dumps("noupdate"),
            tab_n,
            Sidebar(cur_views[n-1], series_n, len(cur_tabs)).show(),
        ]
    
    #reset_page
    if "reset-button" == dash.callback_context.triggered_id['type']:
        return [
            json.dumps([default]), 
            [dcc.Tab(label="1", value='tab1', className='custom-tab', selected_className='custom-tab--selected')],
            json.dumps("update"),
            'tab1',
            Sidebar().show()
        ]

    #dropdown_input
    new_views = cur_views
    if "dropdown-dimension" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['dimension'] = dimension[0]
    if "dropdown-1D" == dash.callback_context.triggered_id['type']:   
        new_views[n-1]['chain'] = oneD[0]
    if "dropdown-colorbar" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['colorbar'] = colorbar[0]
    if "radio-wigner" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['wigner'] = wigner[0]
    if "input-protons" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['proton'][series_n-1] = protons[0]
    if "input-neutrons" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['neutron'][series_n-1] = neutrons[0]
    if "input-nucleons" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['nucleon'][series_n-1] = nucleons[0]
    if "dropdown-quantity" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['quantity'] = quantity[0]
    if "dropdown-dataset" == dash.callback_context.triggered_id['type']:
        new_views[n-1]['dataset'][series_n-1] = dataset[0]
    return [
        json.dumps(new_views),
        cur_tabs, 
        json.dumps("update"),
        tab_n,
        Sidebar(new_views[n-1], series_n, len(cur_tabs)).show()
    ]



@app.callback(
    Output("div-graphs", "children"),
    [
        Input("triggerGraph", "data"),
        State("viewsmemory", "data"),
        Input("zmin", "value"),
        Input("zmax", "value"),
        Input("nmin", "value"),
        Input("nmax", "value"),
    ],
)
def main_output(
    trigger,
    json_views,
    zmin,
    zmax,
    nmin,
    nmax,
):  
    if "triggerGraph" == dash.callback_context.triggered_id:
        zview, nview = None, None
    else:
        zview, nview = [zmin,zmax], [nmin,nmax]
    if(json.loads(trigger)=="update"):
        output = []
        views_list = json.loads(json_views) # list of dicts
        graphindex = 1
        for view_dict in views_list: # iterate through dicts in list
            zview, nview = view_dict["range"]["y"], view_dict["range"]["x"]
            view = View(view_dict, graphindex, zview, nview) # create a view
            output.append(view.plot())
            graphindex += 1
        output.append(html.Button('New Plot', id={'type': 'new-button','index': 1}, value=None, className='new-button'))
        return output
    raise PreventUpdate








# @app.callback(
#     
#         Output({'type': 'dynamic-dropdown-select-quantity', 'index': ALL}, 'options'),
#     ],
#     [
#         Input(component_id='dropdown-1D', component_property='value'),
#         Input(component_id='dropdown-iso-chain', component_property='value'),
#         Input('url-store','data'),
#         State({'type': 'dynamic-dropdown-select-quantity', 'index': ALL}, 'options'),
#     ]
# )
# def quantity_options(oneD,is_chain,url,old_options):
#     # show = {'display': 'block'}
#     # hide = {'display': 'none'}
#     if url[:7] == "/masses":
#         if "dropdown-iso-chain" == dash.callback_context.triggered_id:
#             if is_chain == 'single':
#                 return [[[
#                     # Options for Dropdown
#                     {"label": "All", "value": "All"},
#                     {"label": "Binding Energy", "value": "BE"},
#                     {"label": "One Neutron Separation Energy", "value": "OneNSE",},
#                     {"label": "One Proton Separation Energy", "value": "OnePSE",},
#                     {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
#                     {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
#                     {"label": "Alpha Separation Energy", "value": "AlphaSE",},
#                     {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
#                     {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
#                     {"label": "Double Mass Difference", "value": "DoubleMDiff",},
#                     {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
#                     {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
#                     {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
#                     {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
#                     {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
#                 ] for i in range(len(old_options))],
#                 ]
#             elif is_chain == 'landscape':
#                 return [[[
#                     {"label": "Binding Energy", "value": "BE"},
#                     {"label": "One Neutron Separation Energy", "value": "OneNSE",},
#                     {"label": "One Proton Separation Energy", "value": "OnePSE",},
#                     {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
#                     {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
#                     {"label": "Alpha Separation Energy", "value": "AlphaSE",},
#                     {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
#                     {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
#                     {"label": "Double Mass Difference", "value": "DoubleMDiff",},
#                     {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
#                     {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
#                     {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
#                     {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
#                     {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
#                     {"label": "Quad Def Beta2", "value": "QDB2t",},
#                 ] for i in range(len(old_options))],
#                 ]
#             elif is_chain == "1D":
#                 return [[[
#                         {"label": "Binding Energy", "value": "BE"},
#                         {"label": "One Neutron Separation Energy", "value": "OneNSE",},
#                         {"label": "One Proton Separation Energy", "value": "OnePSE",},
#                         {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
#                         {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
#                         {"label": "Alpha Separation Energy", "value": "AlphaSE",},
#                         {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
#                         {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
#                         {"label": "Double Mass Difference", "value": "DoubleMDiff",},
#                         {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
#                         {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
#                         {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
#                         {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
#                         {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
#                 ]for i in range(len(old_options))],
#                 ]


# @app.callback(
#     [
#         Output("viewsmemory", "data"),
#         Output("tabs", "children"),
#         Output("triggerGraph", "data"),
#         Output("tabs", "value"),
#         Output("dropdown-iso-chain", "value"),
#         Output("dropdown-1D", "value"),
#         Output({'type': 'dynamic-dropdown-select-quantity', 'index': ALL}, 'value'),
#         Output({'type': 'dynamic-dropdown-select-dataset', 'index': ALL}, 'value'),
#         Output("dropdown-colorbar", "value"),
#         Output("protons", "value"),
#         Output("neutrons", "value"),
#         Output("nucleons", "value"),
#         Output("div-series", "children"),
#     ],
#     [
#         State("viewsmemory", "data"),
#         State("tabs", "children"),
#         State("div-series", "children"),
#         #url
#         Input("url-store", "data"),
#         #tabs_output
#         Input("tabs", "value"),
#         #new_plot
#         Input("new-button","n_clicks"),
#         #new_series
#         Input("series-button","n_clicks"),
#         #delete_plot
#         Input("delete-button","n_clicks"),
#         #reset_page
#         Input("reset-button","n_clicks"),
#         #dropdowns
#         Input("dropdown-iso-chain","value"),
#         Input("dropdown-1D","value"),
#         Input({'type': 'dynamic-dropdown-select-quantity', 'index': ALL}, 'value'),
#         Input({'type': 'dynamic-dropdown-select-dataset', 'index': ALL}, 'value'),
#         Input("zmin", "value"),
#         Input("zmax", "value"),
#         Input("nmin", "value"),
#         Input("nmax", "value"),
#         Input("protons", "value"),
#         Input("neutrons", "value"),
#         Input("nucleons", "value"),
#         Input("dropdown-colorbar","value"),
#         Input("radio-wigner","value"),
#     ]
# )
# def main_update(
#     json_cur_views, cur_tabs, div_series, url, tab_n, new_button, series_button, delete_button, 
#     reset_button, graphstyle, oneD, quantity, dataset, zmin, zmax, 
#     nmin, nmax, protons, neutrons, nucleons, colorbar, wigner):

#     print(quantity)
#     print(type(dash.callback_context.triggered_id))
#     cur_views = json.loads(json_cur_views)
#     n = int(tab_n[3])

#     def graphtype(graph):
#         oneD = 'isotopic'
#         if graph[:3]=='iso':
#             oneD = graph
#             graph = '1D'
#         return graph, oneD

#     #url
#     if "url-store" == dash.callback_context.triggered_id:
#         if(len(url)>10):
#             view = json.loads(base64.urlsafe_b64decode(url[8:].encode()).decode())
#             dimension, new_oneD = graphtype(view[n-1]['graphstyle'])
#             new_tabs = []
#             for i in range(len(view)):
#                 new_tabs.append(dcc.Tab(label=str(i+1),value='tab'+str(i+1),className='custom-tab', selected_className='custom-tab--selected'))
#             return  [
#                 json.dumps(view), 
#                 new_tabs,
#                 json.dumps('update'),
#                 tab_n, 
#                 dimension, new_oneD,
#                 view[n-1]['quantity'],
#                 view[n-1]['dataset'],
#                 view[n-1]['colorbar'],
#                 view[n-1]['proton'],
#                 view[n-1]['neutron'],
#                 view[n-1]['nucleon'],
#                 div_series,
#             ]
#         else:
#             dimension, new_oneD = graphtype(cur_views[n-1]['graphstyle'])
#             return  [
#                 json.dumps(cur_views), 
#                 cur_tabs,
#                 json.dumps("update"),
#                 tab_n, 
#                 dimension, new_oneD,
#                 cur_views[n-1]['quantity'],
#                 cur_views[n-1]['dataset'],
#                 cur_views[n-1]['colorbar'],
#                 cur_views[n-1]['proton'],
#                 cur_views[n-1]['neutron'],
#                 cur_views[n-1]['nucleon'],
#                 div_series,
#             ]

#     #tabs_change
#     if "tabs" == dash.callback_context.triggered_id:
#         dimension, new_oneD = graphtype(cur_views[n-1]['graphstyle'])
#         return  [
#             json_cur_views, 
#             cur_tabs,
#             json.dumps("dontupdate"),
#             tab_n, 
#             dimension, new_oneD,
#             cur_views[n-1]['quantity'],
#             cur_views[n-1]['dataset'],
#             cur_views[n-1]['colorbar'],
#             cur_views[n-1]['proton'],
#             cur_views[n-1]['neutron'],
#             cur_views[n-1]['nucleon'],
#             div_series,
#         ]

#     #new_plot
#     if "new-button" == dash.callback_context.triggered_id:
#         if len(cur_tabs)>3 or type(new_button) != type(1):
#             raise PreventUpdate
#         new_views = cur_views
#         default = {"graphstyle": 'landscape', "quantity": ['BE'], "dataset": ['EXP'], "colorbar": 'linear',
#                    "wigner": 0, "proton": None, "neutron": None, "nucleon": None}
#         new_views.append(default)
#         new_tabs = cur_tabs
#         new_tabs.append(dcc.Tab(label=str(len(cur_tabs)+1), value='tab'+str(len(cur_tabs)+1), className='custom-tab', selected_className='custom-tab--selected'))
#         l = len(new_tabs)
#         dimension, new_oneD = graphtype(new_views[-1]['graphstyle'])
#         return [
#             json.dumps(new_views),
#             new_tabs,
#             json.dumps("update"), #graph
#             "tab"+str(l),
#             dimension, new_oneD,
#             new_views[-1]['quantity'],
#             new_views[-1]['dataset'],
#             new_views[-1]['colorbar'],
#             new_views[-1]['proton'],
#             new_views[-1]['neutron'],
#             new_views[-1]['nucleon'],
#             div_series,
#         ]
#     #series_button
#     if "series-button" == dash.callback_context.triggered_id:
#         dimension, new_oneD = graphtype(cur_views[n-1]['graphstyle'])
#         print("IMPORT", div_series)
#         return [
#             json.dumps(cur_views), 
#             cur_tabs,
#             json.dumps("update"),
#             tab_n, 
#             dimension, new_oneD,
#             cur_views[n-1]['quantity'],
#             cur_views[n-1]['dataset'],
#             cur_views[n-1]['colorbar'],
#             cur_views[n-1]['proton'],
#             cur_views[n-1]['neutron'],
#             cur_views[n-1]['nucleon'],
#             div_series.append(series_card(series_button+1)),
#         ]

#     #delete_plot
#     if "delete-button" == dash.callback_context.triggered_id:
#         if  type(delete_button)==type(1) and len(cur_views)>1:
#             new_views = cur_views
#             new_views.pop(n-1)
#             new_tabs = cur_tabs
#             new_tabs.pop(-1)
#             dimension, new_oneD = graphtype(new_views[-1]['graphstyle'])
#             return [
#                 json.dumps(new_views), 
#                 new_tabs,
#                 json.dumps("update"), #graph
#                 "tab"+str(len(new_views)),
#                 dimension, new_oneD,
#                 new_views[-1]['quantity'],
#                 new_views[-1]['dataset'],
#                 new_views[-1]['colorbar'],
#                 new_views[-1]['proton'],
#                 new_views[-1]['neutron'],
#                 new_views[-1]['nucleon'],
#                 div_series,
#             ]
#         else:
#             raise PreventUpdate
    
#     #reset_page
#     if "reset-button" == dash.callback_context.triggered_id:
#         new_views = [{"graphstyle": 'landscape', "quantity": 'BE', "dataset": 'EXP', "colorbar": 'linear',
#                       "wigner": 0, "proton": None, "neutron": None, "nucleon": None}]
#         return [
#             json.dumps(new_views), 
#             [dcc.Tab(label="1", value='tab1', className='custom-tab', selected_className='custom-tab--selected')],
#             json.dumps("update"),
#             'tab1',
#             'landscape',
#             'isotopic',
#             'BE',
#             'EXP',
#             'linear',
#             None,
#             None,
#             None,
#             div_series,
#         ]

#     #dropdown_input
#     new_views = cur_views
#     if ("dropdown-iso-chain" == dash.callback_context.triggered_id) or ("dropdown-1D" == dash.callback_context.triggered_id):
#         if graphstyle == "1D":      
#             new_views[n-1]['graphstyle'] = oneD
#         else:
#             new_views[n-1]['graphstyle'] = graphstyle
#     if "dropdown-colorbar" == dash.callback_context.triggered_id:
#         new_views[n-1]['colorbar'] = colorbar
#     if "radio-wigner" == dash.callback_context.triggered_id:
#         new_views[n-1]['wigner'] = wigner
#     if "protons" == dash.callback_context.triggered_id:
#         new_views[n-1]['proton'] = protons
#     if "neutrons" == dash.callback_context.triggered_id:
#         new_views[n-1]['neutron'] = neutrons
#     if "nucleons" == dash.callback_context.triggered_id:
#         new_views[n-1]['nucleon'] = nucleons
#     try:
#         dash.callback_context.triggered_id['type']
#     except:
#         pass
#     else:
#         if 'dynamic-dropdown-select-quantity' == dash.callback_context.triggered_id['type']:
#             new_views[n-1]['quantity'] = quantity
#             print(quantity, 'FFFF')
#         if "dynamic-dropdown-select-dataset" == dash.callback_context.triggered_id['type']:
#             new_views[n-1]['dataset'] = dataset
#     return [
#         json.dumps(new_views), 
#         cur_tabs, 
#         json.dumps("update"), 
#         tab_n, 
#         graphstyle,
#         oneD,
#         quantity, 
#         dataset,
#         colorbar,
#         protons, 
#         neutrons,
#         nucleons,
#         div_series,
#     ]


# OLD WEBSITE CODE

    # t_start = time.time()
    #
    # NRange, ZRange, N, Z = [None, None, None, None]
    # 
    # np.set_printoptions(precision=5)
    # if(chain=='single'):
    #     if(N==None or Z==None):
    #         return [
    #             html.Div(
    #                 #id="svm-graph-container",
    #                 children=[
    #                     html.P("Welcome to Landon's BMEX! Please input your requested nuclei on the left."),
    #                 ],
    #                 style={'font-size':'3rem'},
    #             ),
    #         ]
    #     elif(quantity == "All"):
    #         all_eval = []
    #         for name, val in  bmex.__dict__.items():
    #             if (callable(val) and name != "OutputString" and name != "GP"):
    #                 out_str = bmex.OutputString(name)
    #                 result = val(N,Z,dataset)
    #                 if isinstance(result,str):
    #                     all_eval.append(html.P(result))
    #                 else: 
    #                     all_eval.append(html.P(dataset+" "+out_str+": {:.4f}".format(result)+" MeV"))

    #         return [
    #             html.Div(
    #                 #id="svm-graph-container",
    #                 children=all_eval,
    #                 style={'font-size':'3rem'},
    #             ),
    #         ]
    #     else:
    #         result = getattr(bmex, quantity)(N,Z,dataset)
    #         if isinstance(result, str):
    #             return [
    #                 html.Div(
    #                     #id="svm-graph-container",
    #                     children=[
    #                         html.P(result),
    #                     ],
    #                     style={'font-size':'3rem'},
    #                 ),
    #             ]
    #         else:
    #             out_str = bmex.OutputString(quantity)
    #             return [
    #                 html.Div(
    #                     #id="svm-graph-container",
    #                     children=[
    #                         html.P(dataset+" "+out_str+": {:.4f}".format(result)+" MeV"),
    #                     ],
    #                     style={'font-size':'3rem'},
    #                 ),
    #             ]
    # elif chain=="isotopic":
    #     if(NRange[0]==None or NRange[1]==None):
    #         return [
    #             html.Div(
    #                 #id="svm-graph-container",
    #                 children=[
    #                     html.P("Welcome to BMEX! Please input your requested nuclei on the left."),
    #                 ],
    #                 style={'font-size':'3rem'},
    #             ),
    #         ]
    #     func = getattr(bmex, quantity)
    #     out_str = bmex.OutputString(quantity)
    #     #& (bmex.df["Z"]==Z1)
    #     nmin = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].min()
    #     nmax = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].max()
    #     if NRange[0] < nmin:
    #         return [
    #             html.Div(
    #                 id="graph-container",
    #                 children=[
    #                     html.P("Input value for N Min, "+str(NRange[0])+\
    #                         ", is smaller than the minimum N from the data, "+str(nmin)),
    #                 ],
    #                 style={'font-size':'3rem'},
    #             )
    #         ]
    #     if NRange[1] > nmax:
    #         return [
    #             html.Div(
    #                 id="graph-container",
    #                 children=[
    #                     html.P("Input value for N Max, "+str(NRange[1])+\
    #                         ", is smaller than the maximum N from the data, "+str(nmax)),
    #                 ],
    #                 style={'font-size':'3rem'},
    #             )
    #         ]
    #     if (NRange[0] >= nmin) and (NRange[1] <= nmax):
    #         isotope_chain = figs.isotope_chain(Z, NRange, dataset, out_str, func)
    #         return [
    #             html.Div(
    #                 id="graph-container",
    #                 children=dcc.Loading(
    #                     className="graph-wrapper",
    #                     children=dcc.Graph(id="graph-chains", figure=isotope_chain),
    #                 )
    #             )
    #         ]
    # elif chain=="isotonic":
    #     if(ZRange[0]==None or ZRange[1]==None):
    #         return [
    #             html.Div(
    #                 #id="svm-graph-container",
    #                 children=[
    #                     html.P("Welcome to BMEX! Please input your requested nuclei on the left."),
    #                 ],
    #                 style={'font-size':'3rem'},
    #             ),
    #         ]
    #     func = getattr(bmex, quantity)
    #     out_str = bmex.OutputString(quantity)
    #     #& (bmex.df["Z"]==Z1)
    #     zmin = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].min()
    #     zmax = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].max()
    #     if ZRange[0] < zmin:
    #         return [
    #             html.Div(
    #                 id="graph-container",
    #                 children=[
    #                     html.P("Input value for Z Min, "+str(ZRange[0])+\
    #                         ", is smaller than the minimum Z from the data, "+str(zmin)),
    #                 ],
    #                 style={'font-size':'3rem'},
    #             )
    #         ]
    #     if ZRange[1] > zmax:
    #         return [
    #             html.Div(
    #                 id="graph-container",
    #                 children=[
    #                     html.P("Input value for Z Max, "+str(ZRange[1])+\
    #                         ", is smaller than the maximum Z from the data, "+str(zmax)),
    #                 ],
    #                 style={'font-size':'3rem'},
    #             )
    #         ]
    #     if (ZRange[0] >= zmin) and (ZRange[1] <= zmax):
    #         isotone_chain = figs.isotone_chain(N, ZRange, dataset, out_str, func)
    #         return [
    #             html.Div(
    #                 id="graph-container",
    #                 children=dcc.Loading(
    #                     className="graph-wrapper",
    #                     children=dcc.Graph(id="graph-chains", figure=isotone_chain),
    #                 )
    #             )
    #         ]
    # elif chain=="landscape":
        # l = len(graphstyle_arr)
        # output = []
        # for i in range(l):
        #     if i == int(tab_n[3])-1:
        #         layout = go.Layout(
        #             font={"color": "#a5b1cd"},
        #             title=dict(text=bmex.OutputString(quantity_arr[i]), font=dict(size=20)),
        #             xaxis=dict(title=dict(text="Neutrons", font=dict(size=20)), gridcolor="#646464", tick0=0, dtick=25, showline=True, #gridcolor="#2f3445",
        #             showgrid=True, gridwidth=1, minor=dict(tick0=0, dtick=5, showgrid=True, gridcolor="#3C3C3C",), mirror='ticks', zeroline=False, range=[0,156]),
        #             yaxis=dict(title=dict(text="Protons", font=dict(size=20)), gridcolor="#646464", tick0=0, dtick=25, showline=True,
        #             showgrid=True, gridwidth=1, minor=dict(tick0=0, dtick=5, showgrid=True, gridcolor="#3C3C3C",), mirror='ticks', zeroline=False, range=[0,104]),
        #             #legend=dict(x=0, y=1.05, orientation="h"),
        #             #margin=dict(l=100, r=10, t=25, b=40),
        #             plot_bgcolor="#282b38",
        #             paper_bgcolor="#282b38",
        #             #uirevision=model,
        #             width=600,
        #             height=440,
        #         )
        #         fig = dcc.Graph(id='graph-chains'+str(i), figure=figs.landscape_plot(dataset_arr[i], layout, quantity_arr[i], colorbar, wigner),
        #                 )   
        #         plots_memory[i] = fig
        #         output.append(fig)
        #     else:
        #         output.append(plots_memory[i])
        # output.append(html.Button('New Plot', id='new-plot', value=None))
        # #output.append(html.Button('Clone Plot', id='clone-plot', value=None))
        # return output

        #(1+2*(l-i))/(2*l)-1
        # subplots = make_subplots(rows=l, cols=1, subplot_titles=([bmex.OutputString(quantity_arr[k]) for k in range (l)]) )
        # for i in range(l):
        #     if i == int(tab_n[3])-1:
        #         fig = figs.landscape_plot(dataset_arr[i], 1/l, quantity_arr[i], colorbar, wigner)
        #         subplots.add_trace(fig, row=i+1, col=1)
        #         plots_memory[i] = fig
        #     else:
        #         subplots.add_trace(plots_memory[i], row=i+1, col=1)
        # layout = go.Layout(
        #     font={"color": "#a5b1cd"},
        #     title=dict(font=dict(size=50)),
        #     xaxis=dict(title=dict(text="Neutrons", font=dict(size=50)), gridcolor="#646464", tick0=0, dtick=25, showline=True, #gridcolor="#2f3445",
        #     showgrid=True, gridwidth=1, minor=dict(tick0=0, dtick=5, showgrid=True, gridcolor="#3C3C3C",), mirror='ticks', zeroline=False, range=[0,156]),
        #     yaxis=dict(title=dict(text="Protons", font=dict(size=50)), gridcolor="#646464", title_font_size=30, tick0=0, dtick=25, showline=True,
        #     showgrid=True, gridwidth=1, minor=dict(tick0=0, dtick=5, showgrid=True, gridcolor="#3C3C3C",), mirror='ticks', zeroline=False, range=[0,104]),
        #     #legend=dict(x=0, y=1.05, orientation="h"),
        #     #margin=dict(l=100, r=10, t=25, b=40),
        #     plot_bgcolor="#282b38",
        #     paper_bgcolor="#282b38",
        #     #uirevision=model,
        #     width=600,
        #     height=440*l,
        #     colorbar=dict(title="", len= 1/l)
        # )
        # subplots.update_layout(layout)
        # output = [dcc.Graph(id="graph-chains", figure=subplots), html.Button('New Plot', id='new-plot', value=None), html.Button('Clone Plot', id='clone-plot', value=None)] 
        # return output
        # return  html.Div(
        #             id="graph-container",
        #             children=dcc.Loading(
        #                 className="graph-wrapper",
        #                 children=[dcc.Graph(id="graph-chains"+str(j), figure=land_plot[j]) for j in range(len(graphstyle_arr))].append(html.Button('New Plot', id='new-plot')),
        #             )
        #         ), html.P("How did you get here? Click the banner to make it back to safety!")
        
        # else:
        #     return  [
        #         html.Div(
        #             id="graph-container",
        #             children=dcc.Loading(
        #                 className="graph-wrapper",
        #                 children=[dcc.Graph(id="graph-chains", figure=land_plot[0]), html.Button('New Plot', id='new-plot')],
        #             )
        #         )
        #     ]

# @app.callback(
#     Output('intermediate-value', 'data'),
#     Output('div-graphs-loading', 'children'),
#     Input('submit-gpe', 'n_clicks'),
#     [
#         State("eta","value"),
#         State("rhon","value"),
#         State("rhoz","value"),
#         State('div-graphs-loading','children'),
#     ],
#     prevent_initial_call=True
# )
# def update_GP_json(n_clicks, eta, rhon, rhoz, old_out):
#     t_start = time.time()
#     model = [eta, rhon, rhoz]
#     if(model == gpe.default_model):
#         return json.dumps(gpe.gp_output.tolist()), [old_out[0]]
#     gp_out = gpe.update_GP(model)
#     gp_json = json.dumps(gp_out.tolist())
#     t_stop = time.time()
#     train_out = [html.P("Trained! Took {:.4f} seconds!".format(t_stop-t_start))]
#     return gp_json, [old_out[0]]+train_out

# # @app.callback(
# #     Output('div-graphs-loading', 'children'),
# #     Input('submit-gpe', 'n_clicks'),
# #     [
# #         State("eta","value"),
# #         State("rhon","value"),
# #         State("rhoz","value"),
# #         State('div-graphs-loading','children'),
# #     ],
# #     prevent_initial_call=True
# # )
# # def update_GP(n_clicks, eta, rhon, rhoz, old_out):
# #     t_start = time.time()

# #     model = [eta, rhon, rhoz]
# #     gpe.gp_output = gpe.update_GP(model)
# #     #gp_json = json.dumps(gp_out.tolist())
# #     t_stop = time.time()
# #     train_out = [html.P("Trained! Took {:.4f} seconds!".format(t_stop-t_start))]
# #     return [old_out[0]] + train_out


# @app.callback(
#     Output("div-graphs-gpe", "children"),
#     [
#         Input("dropdown-select-quantity", "value"),
#         Input("dropdown-select-dataset", "value"),
#         Input("neutrons", "value"),
#         Input("protons", "value"),
#         Input("dropdown-iso-chain", "value"),
#         [Input("nmin","value"),Input("nmax","value")],
#         [Input("zmin","value"),Input("zmax","value")],
#         Input("intermediate-value","data"),
#     ],
# )
# def main_output_gpe(
#     quantity,
#     dataset,
#     N,
#     Z,
#     chain,
#     NRange,
#     ZRange,
#     gp_json,
# ):
#     t_start = time.time()
#     gp_out = np.array(json.loads(gp_json))
#     np.set_printoptions(precision=5)
#     if(chain=='single'):
#         if(N==None or Z==None):
#             return [
#                 html.Div(
#                     #id="svm-graph-container",
#                     children=[
#                         html.P("Welcome to the BMEX Gaussian Process Playground! Please input your requested nuclei on the left."),
#                     ],
#                     style={'font-size':'3rem'},
#                 ),
#             ]
#         elif(quantity == "All"):
#             all_eval = []
#             for name, val in  bmex.__dict__.items():
#                 if (callable(val) and name != "OutputString" and name != "GP"):
#                     out_str = bmex.OutputString(name)
#                     result = val(N,Z,dataset)
#                     if isinstance(result,str):
#                         all_eval.append(html.P(result))
#                     else: 
#                         all_eval.append(html.P(dataset+" "+out_str+": {:.4f}".format(result)+" MeV"))

#             return [
#                 html.Div(
#                     #id="svm-graph-container",
#                     children=all_eval,
#                     style={'font-size':'3rem'},
#                 ),
#             ]
#         else:
#             result = gpe.gp_single(N,Z,gp_out)
#             if isinstance(result, str):
#                 return [
#                     html.Div(
#                         #id="svm-graph-container",
#                         children=[
#                             html.P(result),
#                         ],
#                         style={'font-size':'3rem'},
#                     ),
#                 ]
#             else:
#                 out_str = bmex.OutputString(quantity)
#                 return [
#                     html.Div(
#                         #id="svm-graph-container",
#                         children=[
#                             html.P(dataset+" "+out_str+": {:.4f}".format(result[0])+"±"+"{:.4f}".format(result[1])+" MeV"),
#                         ],
#                         style={'font-size':'3rem'},
#                     ),
#                 ]
#     elif chain=="isotopic":
#         '''
#         if(NRange[0]==None or NRange[1]==None and False):
#             return [
#                 html.Div(
#                     #id="svm-graph-container",
#                     children=[
#                         html.P("Welcome to the BMEX Gaussian Process Playground! Please input your requested nuclei on the left."),
#                     ],
#                     style={'font-size':'3rem'},
#                 ),
#             ]
#         '''
#         if(Z==None):
#             return [
#                 html.Div(
#                     #id="svm-graph-container",
#                     children=[
#                         html.P("Welcome to the BMEX Gaussian Process Playground! Please input your requested nuclei on the left."),
#                     ],
#                     style={'font-size':'3rem'},
#                 ),
#             ]
#         #& (bmex.df["Z"]==Z1)
#         out_str = "Two Neutron Separation Energy"
#         #model = [0.9, 1.529, 0.2533]
#         #nmin = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].min()
#         #nmax = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].max()
#         '''
#         if NRange[0] < nmin:
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=[
#                         html.P("Input value for N Min, "+str(NRange[0])+\
#                             ", is smaller than the minimum N from the data, "+str(nmin)),
#                     ],
#                     style={'font-size':'3rem'},
#                 )
#             ]
#         if NRange[1] > nmax:
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=[
#                         html.P("Input value for N Max, "+str(NRange[1])+\
#                             ", is smaller than the maximum N from the data, "+str(nmax)),
#                     ],
#                     style={'font-size':'3rem'},
#                 )
#             ]
#         '''
#         #if (NRange[0] >= nmin) and (NRange[1] <= nmax):
#         isotope_chain = gpe.gp_figure_isotopic(Z,out_str,gp_out)
#         if isinstance(isotope_chain, str):
#             return [
#                 html.Div(
#                     #id="svm-graph-container",
#                     children=[
#                         html.P(isotope_chain),
#                     ],
#                     style={'font-size':'3rem'},
#                 ),
#             ]
#         else:
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=dcc.Loading(
#                         className="graph-wrapper",
#                         children=dcc.Graph(id="graph-chains", figure=isotope_chain),
#                     )
#                 )
#             ]
#     elif chain=="isotonic":
#         if(ZRange[0]==None or ZRange[1]==None):
#             return [
#                 html.Div(
#                     #id="svm-graph-container",
#                     children=[
#                         html.P("Welcome to BMEX! Please input your requested nuclei on the left."),
#                     ],
#                     style={'font-size':'3rem'},
#                 ),
#             ]
#         func = getattr(bmex, quantity)
#         out_str = bmex.OutputString(quantity)
#         #& (bmex.df["Z"]==Z1)
#         zmin = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].min()
#         zmax = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].max()
#         if ZRange[0] < zmin:
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=[
#                         html.P("Input value for Z Min, "+str(ZRange[0])+\
#                             ", is smaller than the minimum Z from the data, "+str(zmin)),
#                     ],
#                     style={'font-size':'3rem'},
#                 )
#             ]
#         if ZRange[1] > zmax:
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=[
#                         html.P("Input value for Z Max, "+str(ZRange[1])+\
#                             ", is smaller than the maximum Z from the data, "+str(zmax)),
#                     ],
#                     style={'font-size':'3rem'},
#                 )
#             ]
#         if (ZRange[0] >= zmin) and (ZRange[1] <= zmax):
#             isotone_chain = figs.isotone_chain(N, ZRange, dataset, out_str, func)
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=dcc.Loading(
#                         className="graph-wrapper",
#                         children=dcc.Graph(id="graph-chains", figure=isotone_chain),
#                     )
#                 )
#             ]

# @app.callback(
#     Output("div-graphs-pesnet", "children"),
#     [
#         Input("dropdown-select-quantity", "value"),
#         Input("dropdown-select-dataset", "value"),
#         Input("neutrons", "value"),
#         Input("protons", "value"),
#     ],
# )
# def main_output_pesnet(
#     quantity,
#     dataset,
#     N,
#     Z,
# ):
#     t_start = time.time()
#     np.set_printoptions(precision=5)

#     infile = "utils/All.dat"

#     PESfull = pd.read_csv(infile,delim_whitespace=True,low_memory=False)

#     if(N==None or Z==None):
#         return [
#             html.Div(
#                 #id="svm-graph-container",
#                 children=[
#                     html.P("Welcome to the BMEX Potential Energy Surface Generator! Please input your requested nuclei on the left."),
#                 ],
#                 style={'font-size':'3rem'},
#             ),
#         ] 
#     else:
#         pesnet_result = figs.pesnet_surface(N, Z)
#         #if(PESfull['A'].isin([N+Z]) and PESfull['Z'].isin([Z])):
#         if(not PESfull[(PESfull['A'] == N+Z) & (PESfull['Z'] == Z)].empty):
#             true_pes = figs.true_surface(PESfull,N,Z)
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=dcc.Loading(
#                         className="graph-wrapper",
#                         children=[dcc.Graph(id="graph-chains", figure=pesnet_result),
#                         dcc.Graph(id="graph-chains", figure=true_pes)],
#                     )
#                 )
#             ]
#         else:
#             return [
#                 html.Div(
#                     id="graph-container",
#                     children=dcc.Loading(
#                         className="graph-wrapper",
#                         children=dcc.Graph(id="graph-chains", figure=pesnet_result),
#                     )
#                 )
#             ]


# @app.callback(
#     Output("div-emu", "children"),
#     [
#         Input("dropdown-select-dataset", "value"),
#         Input("dropdown-nuc","value"),
#         [Input("Msigma","value"),Input("Rho","value"),Input("BE","value"),\
#          Input("Mstar","value"),Input("K","value"),Input("zeta","value"),\
#          Input("J","value"),Input("L","value"),],
#     ],
# )
# def main_output_emu(
#     dataset,
#     nuc,
#     NMP,
# ):
#     np.set_printoptions(precision=5)
#     nuc_dict={'16O':0,'40Ca':1,'48Ca':2,'68Ni':3,'90Zr':4,'100Sn':5,'116Sn':6,'132Sn':7,'144Sm':8,'208Pb':9}
#     if(None in NMP):
#         return [
#             html.Div(
#                 #id="svm-graph-container",
#                 children=[
#                     html.P("Welcome to BMEX! Please input your requested nuclear matter properties on the left!"),
#                 ],
#                 style={'font-size':'3rem'},
#             ),
#         ]
#     elif(dataset == "rmf"):
#         all_eval = []
#         energy, protrad, timing = rbm.rbm_emulator(nuc_dict[nuc],NMP)

#         all_eval.append(html.P(nuc+" Emulator Results:"))
#         all_eval.append(html.P("Binding Energy: {:.2f} MeV".format(energy)))
#         all_eval.append(html.P("Charge Radius:  {:.2f} fm".format(protrad)))
#         all_eval.append(html.P("Emulation time: {:.3f} s".format(timing)))

#         return [
#             html.Div(
#                 #id="svm-graph-container",
#                 children=all_eval,
#                 style={'font-size':'3rem'},
#             ),
#         ]


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
