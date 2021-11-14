from dash import dcc
from dash import html

import utils.dash_reusable_components as drc

def masses_view():
    return html.Div(
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
    )

def gpe_view():
    return html.Div(
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
                                        id="dropdown-iso-chain-gpe",
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
                                        id="dropdown-select-quantity-gpe",
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
                                        id="dropdown-select-dataset-gpe",
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
                                        id="protons-gpe",
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
                                        id="neutrons-gpe",
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
                                        id="zmin-gpe",
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
                                        id="zmax-gpe",
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
                                        id="nmin-gpe",
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
                                        id="nmax-gpe",
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
                        id="div-graphs-gpe",
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
    )
