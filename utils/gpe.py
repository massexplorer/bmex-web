import numpy as np
from numpy.lib.index_tricks import fill_diagonal
import plotly.graph_objs as go
import pandas as pd
import time

Data=np.loadtxt("utils/TwoNSEDeltaFRDM2003.txt")

DataExtrapolar=np.loadtxt("utils/FRDMTwoNSE.txt")

DataExp=np.loadtxt("utils/TwoNSE2016Full.txt")

default_model = [0.9, 1.529, 0.2533]

gp_output = np.load("utils/default_gp.npy")

def Ker(X1,X2,model):
    eta = model[0]
    rhoN = model[1]
    rhoZ = model[2]
    return eta**2*np.exp(-1.0/(2*rhoN**2)*(X1[0]-X2[0])**2-1.0/(2*rhoZ**2)*(X1[1]-X2[1])**2)

def GP_l(x,KXXInv1,Data1,model=default_model):
    KxX=np.zeros(len(Data1))
    for i in range(len(Data1)):
        KxX[i]=Ker(Data1[i],x,model)
        
    YmX=np.zeros(len(Data1))
    for i in range(len(Data1)):
        YmX[i]=Data1[i][2]
    return np.dot(KxX,np.dot(KXXInv1,YmX))

def GPBand(x,KXXInv1,Data1,model=default_model):
    KxX=np.zeros(len(Data1))
    for i in range(len(Data1)):
        KxX[i]=Ker(Data1[i],x,model)
    
    return np.sqrt(abs(Ker(x,x,model)-np.dot(KxX,np.dot(KXXInv1,KxX))))

def update_GP(model=default_model):
    t_start = time.time()

    KXX=np.zeros((len(Data),len(Data)))

    for i in range(len(Data)):
        for j in range(i+1):
            #print([i,j])
            KXX[i][j]=Ker(Data[i],Data[j],model)
            KXX[j][i]=KXX[i][j]

    KXX1= np.linalg.inv(KXX)
    results = np.zeros((len(DataExtrapolar),5))

    for i in range(len(DataExtrapolar)):
        results[i] = [DataExtrapolar[i][0],DataExtrapolar[i][1],DataExtrapolar[i][2],DataExtrapolar[i][2]+GP_l(DataExtrapolar[i],KXX1,Data,model),GPBand(DataExtrapolar[i],KXX1,Data,model)]
    ''' 
    plotExp=[]
    plotFRDM=[]
    plotFRDMGP=[]
    plotFRDMGPBandplus=[]
    plotFRDMGPBandminus=[]

    for i in range(len(DataExp)):
        if DataExp[i][1]==ZPlot:
            plotExp.append([DataExp[i][0],DataExp[i][2]])
    plotExp=np.array(plotExp)        
            
    for i in range(len(DataExtrapolar)):
        if DataExtrapolar[i][1]==ZPlot:
            plotFRDM.append([DataExtrapolar[i][0],DataExtrapolar[i][2]])
    plotFRDM=np.array(plotFRDM)
    for i in range(len(results)):
        if results[i][1]==ZPlot:
            plotFRDMGP.append([results[i][0],results[i][3]])
            plotFRDMGPBandplus.append([results[i][0],results[i][3]+results[i][4]])
            plotFRDMGPBandminus.append([results[i][0],results[i][3]-results[i][4]])
            
    plotFRDMGP=np.array(plotFRDMGP)        
    plotFRDMGPBandplus=np.array(plotFRDMGPBandplus)
    plotFRDMGPBandminus=np.array(plotFRDMGPBandminus)
    '''
    t_stop = time.time()

    return results

def gp_figure_isotopic(Z,axis_label,gp_out):
    plotGP = []
    for i in range(len(gp_output)):
        if gp_out[i][1]==Z:
            plotGP.append([gp_out[i][0],gp_out[i][3],gp_out[i][4]])
    if not plotGP:
        return "No data for that chain!"
    plotGP = np.array(plotGP)
    layout = go.Layout(
        #title=f"ROC Curve (AUC = {auc_score:.3f})",
        title=f"Isotopic Chain",
        xaxis=dict(title="Neutrons", gridcolor="#2f3445",title_font_size=14),
        yaxis=dict(title=axis_label, gridcolor="#2f3445",title_font_size=14),
        #legend=dict(x=0, y=1.05, orientation="h"),
        #margin=dict(l=100, r=10, t=25, b=40),
        plot_bgcolor="#282b38",
        paper_bgcolor="#282b38",
        font={"color": "#a5b1cd", "size": 14},
    )

    #figure = px.line(x=Z, y=output, markers=True)
    figure = go.Figure([
        go.Scatter(
            name='Mean',
            x=plotGP.T[0],
            y=plotGP.T[1],
            mode='lines',
            line=dict(color='#e76f51'),#'rgb(100, 100, 80)'),
        ),
        go.Scatter(
            name='Upper Bound',
            x=plotGP.T[0],
            y=plotGP.T[1]+plotGP.T[2],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=plotGP.T[0],
            y=plotGP.T[1]-plotGP.T[2],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(233, 196, 106, 0.4)',
            fill='tonexty',
            showlegend=False
        )
    ], layout=layout)
    figure.update_layout(
    #    yaxis_title='Wind speed (m/s)',
    #    title='Continuous, variable value error bars',
        hovermode="x"
    )
    figure.update_xaxes(title_font_size=20)
    figure.update_yaxes(title_font_size=20)
    figure.update_layout(title_font_size=24)

    return figure

def gp_figure_isotonic():

    return 4

def gp_single(N, Z, gp_out):
    out = []
    for i in range(gp_out.shape[0]):
        if (N == gp_out[i,0] and Z == gp_out[i,1]):
            out = [gp_out[i,3], gp_out[i,4]]
            break
    if not out:
        out = "Value not found for N="+str(N)+", Z="+str(Z)
    return out