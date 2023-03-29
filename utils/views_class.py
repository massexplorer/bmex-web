import dash
from dash import dcc
from dash import html
import numpy as np
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

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import random as rand

class View:
    def __init__(self, my_dict=dict(dimension='landscape', chain=None, quantity='BE', dataset=['EXP'], colorbar='linear', wigner=0, proton=[40], neutron=[40], nucleon=[40]), graphindex=0, zview=None, nview=None):
        for key in my_dict:
            setattr(self, key, my_dict[key])
        self.index = graphindex
        self.ZView = zview
        self.NView = nview

    def plot(self):
        if self.dimension == 'single':
            return figs.single(self.quantity, self.dataset, self.proton, self.neutron, self.wigner)
        elif self.dimension == 'landscape':
            return dcc.Graph(id={'type': 'dynamic-output','index': self.index}, figure=figs.landscape(self.quantity, self.dataset, self.colorbar, self.wigner, self.proton, self.neutron, self.nucleon, self.ZView, self.NView))
        elif self.dimension == '1D':
            if {'isotopic': self.proton,'isotonic': self.neutron,'isobaric': self.nucleon}[self.chain] == None:
                return html.P('Please Enter a Valid Chain', style={'padding-left': '180px', 'padding-right': '180px'})
            return dcc.Graph(id={'type': 'dynamic-output','index': self.index}, figure=getattr(figs, self.chain)(self.quantity, self.dataset, self.colorbar, self.wigner, self.proton, self.neutron, self.nucleon, self.ZView, self.NView))
