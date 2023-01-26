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
    def __init__(self, my_dict=dict(graphstyle='landscape', quantity='BE', dataset='EXP', colorbar='linear', wigner=0, id=rand.randint(0,999999), ZRange={"zmin": 0, "zmax": 60, "protons": 40}, NRange={"nmin": 0, "nmax": 60, "neutrons": 40})):
        for key in my_dict:
            setattr(self, key, my_dict[key])

    # def change_attr(self, attribute, value):
    #     self.attribute = value

    def plot(self):
        if self.graphstyle == 'single':
            return figs.single(self.quantity, self.dataset, self.ZRange["protons"], self.NRange["neutrons"], self.wigner)
        return dcc.Graph(id='graph-chains'+str(self.id), figure=getattr(figs, self.graphstyle)(self.quantity, self.dataset, self.colorbar, self.wigner, self.ZRange, self.NRange))