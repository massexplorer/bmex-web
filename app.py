import time
import importlib

import dash
from dash import dcc
from dash import html
import numpy as np
from dash.dependencies import Input, Output, State
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import datasets
from sklearn.svm import SVC

import utils.dash_reusable_components as drc
import utils.figures as figs
import utils.bmex as bmex


app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

app.title = "Bayesian Mass Explorer"

server = app.server

app.layout = html.Div(
    children=[
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
                )
            ],
        ),
        html.Div(
            id="body",
            className="container scalable",
            children=[
                html.Div(
                    id="app-container",
                    # className="row",
                    children=[
                        html.Div(
                            # className="three columns",
                            id="left-column",
                            children=[
                                drc.Card(
                                    id="first-card",
                                    children=[
                                        drc.NamedDropdown(
                                            name="Compute For",
                                            id="dropdown-iso-chain",
                                            options=[
                                                {"label": "Single Nucleus", "value": "single"},
                                                {"label": "Isotopic Chain", "value": "isotopic"},
                                                {"label": "Isotonic Chain", "value": "isotonic"},
                                            ],
                                            clearable=False,
                                            searchable=False,
                                            value="single",
                                        ),
                                    ]
                                ),
                                drc.Card(
                                    id="quantity-single",
                                    children=[
                                        drc.NamedDropdown(
                                            name="Select Quantity",
                                            id="dropdown-select-quantity",
                                            options=[
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
                                            clearable=False,
                                            searchable=False,
                                            value="All",
                                        ),
                                    ]
                                ),
                                drc.Card(
                                    id="data-card",
                                    children=[
                                        drc.NamedDropdown(
                                            name="Select Dataset",
                                            id="dropdown-select-dataset",
                                            options=[
                                                {"label": "Experiment", "value": "Exp"},
                                                {"label": "SkMs", "value": "SkMs"},
                                            ],
                                            clearable=False,
                                            searchable=False,
                                            value="Exp",
                                        ),
                                    ],
                                ),
                                drc.Card(
                                    id="protons-card",
                                    children=[
                                        drc.NamedInput(
                                            name="Protons",
                                            id="protons",
                                            type="number",
                                            min=0,
                                            max=200,
                                            step=1,
                                            placeholder="Proton #",
                                            style={'width':'100%'},
                                        ),
                                    ],
                                ),
                                drc.Card(
                                    id="neutrons-card",
                                    children=[
                                        drc.NamedInput(
                                            name="Neutrons",
                                            id="neutrons",
                                            type="number",
                                            min=0,
                                            max=200,
                                            step=1,
                                            placeholder="Neutron #",
                                            style={'width':'100%'},
                                        ),
                                    ],
                                ),
                                drc.Card(
                                    id="zmin-card",
                                    children=[
                                        drc.NamedInput(
                                            name="Minimum Z",
                                            id="zmin",
                                            type="number",
                                            min=0,
                                            max=200,
                                            step=1,
                                            placeholder="Z Min",
                                            style={'width':'100%'},
                                        ),
                                    ],
                                ),
                                drc.Card(
                                    id="zmax-card",
                                    children=[
                                        drc.NamedInput(
                                            name="Maximum Z",
                                            id="zmax",
                                            type="number",
                                            min=0,
                                            max=200,
                                            step=1,
                                            placeholder="Z Max",
                                            style={'width':'100%'},
                                        ),
                                    ],
                                ),
                                drc.Card(
                                    id="nmin-card",
                                    children=[
                                        drc.NamedInput(
                                            name="Minimum N",
                                            id="nmin",
                                            type="number",
                                            min=0,
                                            max=200,
                                            step=1,
                                            placeholder="N Min",
                                            style={'width':'100%'},
                                        ),
                                    ],
                                ),
                                drc.Card(
                                    id="nmax-card",
                                    children=[
                                        drc.NamedInput(
                                            name="Maximum N",
                                            id="nmax",
                                            type="number",
                                            min=0,
                                            max=200,
                                            step=1,
                                            placeholder="N Max",
                                            style={'width':'100%'},
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            id="div-graphs",
                            children=[
                                dcc.Graph(
                                    id="graph-sklearn-svm",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor="#282b38", paper_bgcolor="#282b38"
                                        )
                                    ),
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
    ]
)


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
                        html.P("Welcome to BMEX! Please input a value for N and Z."),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]
        elif(quantity == "All"):
            all_eval = []
            for name, val in  bmex.__dict__.items():
                if (callable(val) and name != "OutputString"):
                    out_str = bmex.OutputString(name)
                    result = val(N,Z,dataset)
                    if isinstance(result,str):
                        all_eval.append(html.P(result))
                    else: 
                        all_eval.append(html.P(dataset+" "+out_str+"{:.4f}".format(result)+" MeV"))

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
                            html.P(dataset+" "+out_str+"{:.4f}".format(result)+" MeV"),
                        ],
                        style={'font-size':'3rem'},
                    ),
                ]
    elif chain=="isotopic":
        #add figure here
        func = getattr(bmex, quantity)
        isotope_chain = figs.isotope_chain(Z, NRange, dataset, func)
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
        print("Hello")
# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
