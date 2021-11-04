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


def generate_data(n_samples, dataset, noise):
    if dataset == "moons":
        return datasets.make_moons(n_samples=n_samples, noise=noise, random_state=0)

    elif dataset == "circles":
        return datasets.make_circles(
            n_samples=n_samples, noise=noise, factor=0.5, random_state=1
        )

    elif dataset == "linear":
        X, y = datasets.make_classification(
            n_samples=n_samples,
            n_features=2,
            n_redundant=0,
            n_informative=2,
            random_state=2,
            n_clusters_per_class=1,
        )

        rng = np.random.RandomState(2)
        X += noise * rng.uniform(size=X.shape)
        linearly_separable = (X, y)

        return linearly_separable

    else:
        raise ValueError(
            "Data type incorrectly specified. Please choose an existing dataset."
        )


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
                                            name="Select Quantity",
                                            id="dropdown-select-quantity",
                                            options=[
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
                                            value="BE",
                                        ),
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
                                    id="nuc-card",
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
    Output("div-graphs", "children"),
    [
        Input("dropdown-select-quantity", "value"),
        Input("dropdown-select-dataset", "value"),
        Input("neutrons", "value"),
        Input("protons", "value"),
    ],
)
def main_output(
    quantity,
    dataset,
    N,
    Z,
):
    t_start = time.time()
    if (quantity == "BE"):
        out_str = "Binding Energy: "
    elif (quantity == "OneNSE"):
        out_str = "One Neutron Separation Energy: "
    elif (quantity == "OnePSE"):
        out_str = "One Proton Separation Energy: "
    elif (quantity == "TwoNSE"):
        out_str = "Two Neutron Separation Energy: "
    elif (quantity == "TwoPSE"):
        out_str = "Two Proton Separation Energy: "
    elif (quantity == "AlphaSE"):
        out_str = "Alpha Separation Energy: "
    elif (quantity == "TwoPSGap"):
        out_str = "Two Proton Shell Gap: "
    elif (quantity == "TwoNSGap"):
        out_str = "Two Neutron Shell Gap: "
    elif (quantity == "DoubleMDiff"):
        out_str = "Double Mass Difference: "
    elif (quantity == "N3PointOED"):
        out_str = "Neutron 3-Point Odd-Even Binding Energy Difference: "
    elif (quantity == "P3PointOED"):
        out_str = "Proton 3-Point Odd-Even Binding Energy Difference: "
    elif (quantity == "SNESplitting"):
        out_str = "Single-Neutron Energy Splitting: "
    elif (quantity == "SPESplitting"):
        out_str = "Single-Proton Energy Splitting: "
    elif (quantity == "WignerEC"):
        out_str = "Wigner Energy Coefficient: "
    #result = func(N,Z)
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
        result = getattr(bmex, quantity)(N,Z,dataset)
        return [
            html.Div(
                #id="svm-graph-container",
                children=[
                    html.P("Output: "+str(result)+" MeV"),
                ],
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
            return [
                html.Div(
                    #id="svm-graph-container",
                    children=[
                        html.P(dataset+" "+out_str+str(result)+" MeV"),
                    ],
                    style={'font-size':'3rem'},
                ),
            ]


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
