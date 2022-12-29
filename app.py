import time

import dash
from dash import dcc
from dash import html
import numpy as np
from dash.dependencies import Input, Output, State
import json
import dash_bootstrap_components as dbc


import utils.dash_reusable_components as drc
import utils.figures as figs
import utils.bmex as bmex
from utils.bmex_views import *
import utils.gpe as gpe
import utils.rbm as rbm

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import h5py
import base64, io
import re


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
                                html.Img(src=app.get_asset_url("BMEX-logo-3.png"))
                            ],
                            href="https://bmex.dev",
                        )
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(id='page-content'),
        dcc.Store(id='intermediate-value'),
    ]
)

@app.callback(
    Output('page-content','children'),
    [Input('url','pathname')]
    )
def display_page(pathname):
    if(pathname == "/masses"):
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
    return out



@app.callback(
    [
        Output(component_id='dropdown-select-quantity', component_property='options'),
        Output(component_id='dropdown-select-quantity', component_property='value'),
        Output(component_id='protons-card', component_property='style'),
        Output(component_id='neutrons-card', component_property='style'),
        Output(component_id='zmin-card', component_property='style'),
        Output(component_id='zmax-card', component_property='style'),
        Output(component_id='nmin-card', component_property='style'),
        Output(component_id='nmax-card', component_property='style'),
    ],
    [
        Input(component_id='dropdown-iso-chain', component_property='value'),
        Input('url','pathname'),
    ]
)
def quantity_options(is_chain,url):
    show = {'display': 'block'}
    hide = {'display': 'none'}
    if url == "/masses":
        if is_chain == 'single':
            return [[
                # Options for Dropdown
                {"label": "All", "value": "All"},
                {"label": "Binding Energy", "value": "BE"},
                {"label": "One Neutron Separation Energy", "value": "OneNSE",},
                {"label": "One Proton Separation Energy", "value": "OnePSE",},
                {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
                {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
                {"label": "Alpha Separation Energy", "value": "AlphaSE",},
                {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
                {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
                {"label": "Double Mass Difference", "value": "DoubleMDiff",},
                {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
                {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
                {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
                {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
                {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
            ],
            # Default Value
            "All",
            # Proton Box Visibility
            show,
            # Neutron Box Visibility
            show,
            # Zmin Visibility
            hide,
            # Zmax Visibility
            hide,
            # Nmin Visibility
            hide,
            # Nmax Visibility
            hide,
            ]
        elif is_chain == 'isotopic':
            return [[
                    {"label": "Binding Energy", "value": "BE"},
                    {"label": "One Neutron Separation Energy", "value": "OneNSE",},
                    {"label": "One Proton Separation Energy", "value": "OnePSE",},
                    {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
                    {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
                    {"label": "Alpha Separation Energy", "value": "AlphaSE",},
                    {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
                    {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
                    {"label": "Double Mass Difference", "value": "DoubleMDiff",},
                    {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
                    {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
                    {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
                    {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
                    {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
            ],
            # Default Value
            "BE",
            # Proton Box Visibility
            show,
            # Neutron Box Visibility
            hide,
            # Zmin Visibility
            hide,
            # Zmax Visibility
            hide,
            # Nmin Visibility
            show,
            # Nmax Visibility
            show,
            ]
        elif is_chain == 'isotonic':
            return [[
                    {"label": "Binding Energy", "value": "BE"},
                    {"label": "One Neutron Separation Energy", "value": "OneNSE",},
                    {"label": "One Proton Separation Energy", "value": "OnePSE",},
                    {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
                    {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
                    {"label": "Alpha Separation Energy", "value": "AlphaSE",},
                    {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
                    {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
                    {"label": "Double Mass Difference", "value": "DoubleMDiff",},
                    {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
                    {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
                    {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
                    {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
                    {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
            ],
            # Default Value
            "BE",
            # Proton Box Visibility
            hide,
            # Neutron Box Visibility
            show,
            # Zmin Visibility
            show,
            # Zmax Visibility
            show,
            # Nmin Visibility
            hide,
            # Nmax Visibility
            hide,
            ]
    elif url == "/gpe":
        if is_chain == 'single':
            return [[
                # Options for Dropdown
                #{"label": "All", "value": "All"},
                #{"label": "Binding Energy", "value": "BE"},
                #{"label": "One Neutron Separation Energy", "value": "OneNSE",},
                #{"label": "One Proton Separation Energy", "value": "OnePSE",},
                {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
                # {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
                # {"label": "Alpha Separation Energy", "value": "AlphaSE",},
                # {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
                # {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
                # {"label": "Double Mass Difference", "value": "DoubleMDiff",},
                # {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
                # {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
                # {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
                # {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
                # {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
            ],
            # Default Value
            "TwoNSE",
            # Proton Box Visibility
            show,
            # Neutron Box Visibility
            show,
            # Zmin Visibility
            hide,
            # Zmax Visibility
            hide,
            # Nmin Visibility
            hide,
            # Nmax Visibility
            hide,
            ]
        elif is_chain == 'isotopic':
            return [[
                    # {"label": "Binding Energy", "value": "BE"},
                    # {"label": "One Neutron Separation Energy", "value": "OneNSE",},
                    # {"label": "One Proton Separation Energy", "value": "OnePSE",},
                    {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
                    # {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
                    # {"label": "Alpha Separation Energy", "value": "AlphaSE",},
                    # {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
                    # {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
                    # {"label": "Double Mass Difference", "value": "DoubleMDiff",},
                    # {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
                    # {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
                    # {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
                    # {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
                    # {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
            ],
            # Default Value
            "TwoNSE",
            # Proton Box Visibility
            show,
            # Neutron Box Visibility
            hide,
            # Zmin Visibility
            hide,
            # Zmax Visibility
            hide,
            # Nmin Visibility
            hide,
            # Nmax Visibility
            hide,
            ]
        elif is_chain == 'isotonic':
            return [[
                    # {"label": "Binding Energy", "value": "BE"},
                    # {"label": "One Neutron Separation Energy", "value": "OneNSE",},
                    # {"label": "One Proton Separation Energy", "value": "OnePSE",},
                    {"label": "Two Neutron Separation Energy", "value": "TwoNSE",},
                    # {"label": "Two Proton Separation Energy", "value": "TwoPSE",},
                    # {"label": "Alpha Separation Energy", "value": "AlphaSE",},
                    # {"label": "Two Proton Shell Gap", "value": "TwoNSGap",},
                    # {"label": "Two Neutron Shell Gap", "value": "TwoPSGap",},
                    # {"label": "Double Mass Difference", "value": "DoubleMDiff",},
                    # {"label": "Neutron 3-Point Odd-Even Binding Energy Difference", "value": "N3PointOED",},
                    # {"label": "Proton 3-Point Odd-Even Binding Energy Difference", "value": "P3PointOED",},
                    # {"label": "Single-Neutron Energy Splitting", "value": "SNESplitting",},
                    # {"label": "Single-Proton Energy Splitting", "value": "SPESplitting",},
                    # {"label": "Wigner Energy Coefficient", "value": "WignerEC",},
            ],
            # Default Value
            "TwoNSE",
            # Proton Box Visibility
            hide,
            # Neutron Box Visibility
            show,
            # Zmin Visibility
            show,
            # Zmax Visibility
            show,
            # Nmin Visibility
            hide,
            # Nmax Visibility
            hide,
            ]




@app.callback(
    Output("div-graphs", "children"),
    [
        Input("dropdown-select-quantity", "value"),
        Input("dropdown-select-dataset", "value"),
        Input("neutrons", "value"),
        Input("protons", "value"),
        Input("dropdown-iso-chain","value"),
        [Input("nmin","value"),Input("nmax","value")],
        [Input("zmin","value"),Input("zmax","value")],
    ],
)
def main_output(
    quantity,
    dataset,
    N,
    Z,
    chain,
    NRange,
    ZRange,
):
    t_start = time.time()
    np.set_printoptions(precision=5)
    if(chain=='single'):
        if(N==None or Z==None):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P("Welcome to BMEX! Please input your requested nuclei on the left."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        elif(quantity == "All"):
            all_eval = []
            for name, val in  bmex.__dict__.items():
                if (callable(val) and name != "OutputString" and name != "GP"):
                    out_str = bmex.OutputString(name)
                    result = val(N,Z,dataset)
                    if isinstance(result,str):
                        all_eval.append(html.P(result))
                    else: 
                        all_eval.append(html.P(dataset+" "+out_str+": {:.4f}".format(result)+" MeV"))

            return [
                html.Div(
                    #id="svm-graph-container",
                    children=all_eval,
                    style={'font-size':'3rem'},
                ),
            ]
        else:
            result = getattr(bmex, quantity)(N,Z,dataset)
            if isinstance(result, str):
                return [
                    html.Div(
                        #id="svm-graph-container",
                        children=[
                            html.P(result),
                        ],
                        style={'font-size':'3rem'},
                    ),
                ]
            else:
                out_str = bmex.OutputString(quantity)
                return [
                    html.Div(
                        #id="svm-graph-container",
                        children=[
                            html.P(dataset+" "+out_str+": {:.4f}".format(result)+" MeV"),
                        ],
                        style={'font-size':'3rem'},
                    ),
                ]
    elif chain=="isotopic":
        if(NRange[0]==None or NRange[1]==None):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P("Welcome to BMEX! Please input your requested nuclei on the left."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        func = getattr(bmex, quantity)
        out_str = bmex.OutputString(quantity)
        #& (bmex.df["Z"]==Z1)
        nmin = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].min()
        nmax = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].max()
        if NRange[0] < nmin:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for N Min, "+str(NRange[0])+\
                            ", is smaller than the minimum N from the data, "+str(nmin)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        if NRange[1] > nmax:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for N Max, "+str(NRange[1])+\
                            ", is smaller than the maximum N from the data, "+str(nmax)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        if (NRange[0] >= nmin) and (NRange[1] <= nmax):
            isotope_chain = figs.isotope_chain(Z, NRange, dataset, out_str, func)
            return [
                html.Div(
                    id="graph-container",
                    children=dcc.Loading(
                        className="graph-wrapper",
                        children=dcc.Graph(id="graph-chains", figure=isotope_chain),
                    )
                )
            ]
    elif chain=="isotonic":
        if(ZRange[0]==None or ZRange[1]==None):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P("Welcome to BMEX! Please input your requested nuclei on the left."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        func = getattr(bmex, quantity)
        out_str = bmex.OutputString(quantity)
        #& (bmex.df["Z"]==Z1)
        zmin = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].min()
        zmax = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].max()
        if ZRange[0] < zmin:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for Z Min, "+str(ZRange[0])+\
                            ", is smaller than the minimum Z from the data, "+str(zmin)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        if ZRange[1] > zmax:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for Z Max, "+str(ZRange[1])+\
                            ", is smaller than the maximum Z from the data, "+str(zmax)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        if (ZRange[0] >= zmin) and (ZRange[1] <= zmax):
            isotone_chain = figs.isotone_chain(N, ZRange, dataset, out_str, func)
            return [
                html.Div(
                    id="graph-container",
                    children=dcc.Loading(
                        className="graph-wrapper",
                        children=dcc.Graph(id="graph-chains", figure=isotone_chain),
                    )
                )
            ]

@app.callback(
    Output('intermediate-value', 'data'),
    Output('div-graphs-loading', 'children'),
    Input('submit-gpe', 'n_clicks'),
    [
        State("eta","value"),
        State("rhon","value"),
        State("rhoz","value"),
        State('div-graphs-loading','children'),
    ],
    prevent_initial_call=True
)
def update_GP_json(n_clicks, eta, rhon, rhoz, old_out):
    t_start = time.time()
    model = [eta, rhon, rhoz]
    if(model == gpe.default_model):
        return json.dumps(gpe.gp_output.tolist()), [old_out[0]]
    gp_out = gpe.update_GP(model)
    gp_json = json.dumps(gp_out.tolist())
    t_stop = time.time()
    train_out = [html.P("Trained! Took {:.4f} seconds!".format(t_stop-t_start))]
    return gp_json, [old_out[0]]+train_out

# @app.callback(
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
# def update_GP(n_clicks, eta, rhon, rhoz, old_out):
#     t_start = time.time()

#     model = [eta, rhon, rhoz]
#     gpe.gp_output = gpe.update_GP(model)
#     #gp_json = json.dumps(gp_out.tolist())
#     t_stop = time.time()
#     train_out = [html.P("Trained! Took {:.4f} seconds!".format(t_stop-t_start))]
#     return [old_out[0]] + train_out


@app.callback(
    Output("div-graphs-gpe", "children"),
    [
        Input("dropdown-select-quantity", "value"),
        Input("dropdown-select-dataset", "value"),
        Input("neutrons", "value"),
        Input("protons", "value"),
        Input("dropdown-iso-chain","value"),
        [Input("nmin","value"),Input("nmax","value")],
        [Input("zmin","value"),Input("zmax","value")],
        Input("intermediate-value","data"),
    ],
)
def main_output_gpe(
    quantity,
    dataset,
    N,
    Z,
    chain,
    NRange,
    ZRange,
    gp_json,
):
    t_start = time.time()
    gp_out = np.array(json.loads(gp_json))
    np.set_printoptions(precision=5)
    if(chain=='single'):
        if(N==None or Z==None):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P("Welcome to the BMEX Gaussian Process Playground! Please input your requested nuclei on the left."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        elif(quantity == "All"):
            all_eval = []
            for name, val in  bmex.__dict__.items():
                if (callable(val) and name != "OutputString" and name != "GP"):
                    out_str = bmex.OutputString(name)
                    result = val(N,Z,dataset)
                    if isinstance(result,str):
                        all_eval.append(html.P(result))
                    else: 
                        all_eval.append(html.P(dataset+" "+out_str+": {:.4f}".format(result)+" MeV"))

            return [
                html.Div(
                    #id="svm-graph-container",
                    children=all_eval,
                    style={'font-size':'3rem'},
                ),
            ]
        else:
            result = gpe.gp_single(N,Z,gp_out)
            if isinstance(result, str):
                return [
                    html.Div(
                        #id="svm-graph-container",
                        children=[
                            html.P(result),
                        ],
                        style={'font-size':'3rem'},
                    ),
                ]
            else:
                out_str = bmex.OutputString(quantity)
                return [
                    html.Div(
                        #id="svm-graph-container",
                        children=[
                            html.P(dataset+" "+out_str+": {:.4f}".format(result[0])+"±"+"{:.4f}".format(result[1])+" MeV"),
                        ],
                        style={'font-size':'3rem'},
                    ),
                ]
    elif chain=="isotopic":
        '''
        if(NRange[0]==None or NRange[1]==None and False):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P("Welcome to the BMEX Gaussian Process Playground! Please input your requested nuclei on the left."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        '''
        if(Z==None):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P("Welcome to the BMEX Gaussian Process Playground! Please input your requested nuclei on the left."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        #& (bmex.df["Z"]==Z1)
        out_str = "Two Neutron Separation Energy"
        #model = [0.9, 1.529, 0.2533]
        #nmin = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].min()
        #nmax = bmex.df[(bmex.df["Z"]==Z) & (bmex.df["Model"]==dataset)]['N'].max()
        '''
        if NRange[0] < nmin:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for N Min, "+str(NRange[0])+\
                            ", is smaller than the minimum N from the data, "+str(nmin)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        if NRange[1] > nmax:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for N Max, "+str(NRange[1])+\
                            ", is smaller than the maximum N from the data, "+str(nmax)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        '''
        #if (NRange[0] >= nmin) and (NRange[1] <= nmax):
        isotope_chain = gpe.gp_figure_isotopic(Z,out_str,gp_out)
        if isinstance(isotope_chain, str):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P(isotope_chain),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        else:
            return [
                html.Div(
                    id="graph-container",
                    children=dcc.Loading(
                        className="graph-wrapper",
                        children=dcc.Graph(id="graph-chains", figure=isotope_chain),
                    )
                )
            ]
    elif chain=="isotonic":
        if(ZRange[0]==None or ZRange[1]==None):
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P("Welcome to BMEX! Please input your requested nuclei on the left."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        func = getattr(bmex, quantity)
        out_str = bmex.OutputString(quantity)
        #& (bmex.df["Z"]==Z1)
        zmin = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].min()
        zmax = bmex.df[(bmex.df["N"]==N) & (bmex.df["Model"]==dataset)]["Z"].max()
        if ZRange[0] < zmin:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for Z Min, "+str(ZRange[0])+\
                            ", is smaller than the minimum Z from the data, "+str(zmin)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        if ZRange[1] > zmax:
            return [
                html.Div(
                    id="graph-container",
                    children=[
                        html.P("Input value for Z Max, "+str(ZRange[1])+\
                            ", is smaller than the maximum Z from the data, "+str(zmax)),
                    ],
                    style={'font-size':'3rem'},
                )
            ]
        if (ZRange[0] >= zmin) and (ZRange[1] <= zmax):
            isotone_chain = figs.isotone_chain(N, ZRange, dataset, out_str, func)
            return [
                html.Div(
                    id="graph-container",
                    children=dcc.Loading(
                        className="graph-wrapper",
                        children=dcc.Graph(id="graph-chains", figure=isotone_chain),
                    )
                )
            ]

@app.callback(
    Output("div-graphs-pesnet", "children"),
    [
        Input("dropdown-select-quantity", "value"),
        Input("dropdown-select-dataset", "value"),
        Input("neutrons", "value"),
        Input("protons", "value"),
    ],
)
def main_output_pesnet(
    quantity,
    dataset,
    N,
    Z,
):
    t_start = time.time()
    np.set_printoptions(precision=5)

    infile = "utils/All.dat"

    PESfull = pd.read_csv(infile,delim_whitespace=True,low_memory=False)

    if(N==None or Z==None):
        return [
            html.Div(
                #id="svm-graph-container",
                children=[
                    html.P("Welcome to the BMEX Potential Energy Surface Generator! Please input your requested nuclei on the left."),
                ],
                style={'font-size':'3rem'},
            ),
        ] 
    else:
        pesnet_result = figs.pesnet_surface(N, Z)
        #if(PESfull['A'].isin([N+Z]) and PESfull['Z'].isin([Z])):
        if(not PESfull[(PESfull['A'] == N+Z) & (PESfull['Z'] == Z)].empty):
            true_pes = figs.true_surface(PESfull,N,Z)
            return [
                html.Div(
                    id="graph-container",
                    children=dcc.Loading(
                        className="graph-wrapper",
                        children=[dcc.Graph(id="graph-chains", figure=pesnet_result),
                        dcc.Graph(id="graph-chains", figure=true_pes)],
                    )
                )
            ]
        else:
            return [
                html.Div(
                    id="graph-container",
                    children=dcc.Loading(
                        className="graph-wrapper",
                        children=dcc.Graph(id="graph-chains", figure=pesnet_result),
                    )
                )
            ]


@app.callback(
    Output("div-emu", "children"),
    [
        Input("dropdown-select-dataset", "value"),
        Input("dropdown-nuc","value"),
        [Input("Msigma","value"),Input("Rho","value"),Input("BE","value"),\
         Input("Mstar","value"),Input("K","value"),Input("zeta","value"),\
         Input("J","value"),Input("L","value"),],
    ],
)
def main_output_emu(
    dataset,
    nuc,
    NMP,
):
    np.set_printoptions(precision=5)
    nuc_dict={'16O':0,'40Ca':1,'48Ca':2,'68Ni':3,'90Zr':4,'100Sn':5,'116Sn':6,'132Sn':7,'144Sm':8,'208Pb':9}
    if(None in NMP):
        return [
            html.Div(
                #id="svm-graph-container",
                children=[
                    html.P("Welcome to BMEX! Please input your requested nuclear matter properties on the left!"),
                ],
                style={'font-size':'3rem'},
            ),
        ]
    elif(dataset == "rmf"):
        all_eval = []
        energy, protrad, timing = rbm.rbm_emulator(nuc_dict[nuc],NMP)

        all_eval.append(html.P(nuc+" Emulator Results:"))
        all_eval.append(html.P("Binding Energy: {:.2f} MeV".format(energy)))
        all_eval.append(html.P("Charge Radius:  {:.2f} fm".format(protrad)))
        all_eval.append(html.P("Emulation time: {:.3f} s".format(timing)))

        return [
            html.Div(
                #id="svm-graph-container",
                children=all_eval,
                style={'font-size':'3rem'},
            ),
        ]


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
