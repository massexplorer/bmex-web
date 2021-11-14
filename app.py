import time

import dash
from dash import dcc
from dash import html
import numpy as np
from dash.dependencies import Input, Output, State

import utils.dash_reusable_components as drc
import utils.figures as figs
import utils.bmex as bmex
from utils.bmex_views import *


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
    ]
)
def quantity_options(is_chain):
    show = {'display': 'block'}
    hide = {'display': 'none'}
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
    Output("div-graphs-gpe", "children"),
    [
        Input("dropdown-select-quantity-gpe", "value"),
        Input("dropdown-select-dataset-gpe", "value"),
        Input("neutrons-gpe", "value"),
        Input("protons-gpe", "value"),
        Input("dropdown-iso-chain-gpe","value"),
        [Input("nmin-gpe","value"),Input("nmax-gpe","value")],
        [Input("zmin-gpe","value"),Input("zmax-gpe","value")],
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
        func = bmex.GP
        #& (bmex.df["Z"]==Z1)
        out_str = "2NSE"
        model = [0.9, 1.529, 0.2533]
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
            isotope_chain = figs.isotope_chain_gp(Z, NRange, model, out_str, func)
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


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
