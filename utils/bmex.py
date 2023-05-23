import numpy as np
import pandas as pd

# # Make dictionary of models and corresponding pandas dataframes
# modelNames = ['EXP', 'ME2', 'MEdelta', 'PC1', 'NL3S', 'SKMS', 'SKP', 'SLY4', 'SV', 'UNEDF0', 'UNEDF1']
# models = [pd.read_hdf('utils/models.h5', n) for n in modelNames]
# data_dict = {modelNames[i]: models[i] for i in range(len(modelNames))}

# # Make dictionary to convert quantity code to full quantity name
# qinput = ['BE', 'OneNSE', 'OnePSE', 'TwoNSE', 'TwoPSE', 'AlphaSE', 'TwoNSGap', 'TwoPSGap', 'DoubleMDiff', 'N3PointOED', 'P3PointOED', 'SNESplitting', 'SPESplitting', 'WignerEC', 'QDB2t']
# qnames = ['Binding_Energy', 'One Neutron Separation Energy', 'One Proton Separation Energy', 'Two Neutron Separation Energy', 
# 'Two Proton Separation Energy', 'Alpha Separation Energy',  'Two Neutron Shell Gap', 'Two Proton Shell Gap',
# 'Double Mass Difference', 'Neutron 3-Point Odd-Even Binding Energy Difference', 'Proton 3-Point Odd-Even Binding Energy Difference',
# 'Single-Neutron Energy Splitting', 'Single-Proton Energy Splitting', 'Wigner Energy Coeffienct', 'Quad_Def_Beta2_total']
# q_dict = {qinput[j]: qnames[j] for j in range(len(qinput))}

# Retrieves single value
def QuanValue(Z,N,model,quan,W=0):
    df = pd.read_hdf('utils/May23.h5', model)
    try:
        return np.round(float(df[(df["N"]==N) & (df["Z"]==Z) & (df["Wigner"]==W)][quan]),6)
    except:
        return "Error: "+str(model)+" data does not have "+OutputString(quan)+" available for Nuclei with N="+str(N)+" and Z="+str(Z)

def IsotopicChain(Z,model,quan,W=0):
    df = pd.read_hdf('utils/May23.h5', model)
    df = df[df["Wigner"]==W]
    df = df[df["Z"]==Z]
    return df.loc[:, [quan, "N"]]


def IsotonicChain(N,model,quan,W=0):
    df = pd.read_hdf('utils/May23.h5', model)
    df = df[df["Wigner"]==W]
    df = df[df["N"]==N]
    return df.loc[:, [quan, "Z"]]

def IsobaricChain(A,model,quan,W=0):
    df = pd.read_hdf('utils/May23.h5', model)
    df = df[df["Wigner"]==W]
    df = df[df["N"]+df["Z"]==A]
    return df.loc[:, [quan, "Z"]]

def OutputString(quantity):
    out_str = "Quantity not found!"
    if (quantity == "BE"):
        out_str = "Binding Energy"
    elif (quantity == "OneNSE"):
        out_str = "One Neutron Separation Energy"
    elif (quantity == "OnePSE"):
        out_str = "One Proton Separation Energy"
    elif (quantity == "TwoNSE"):
        out_str = "Two Neutron Separation Energy"
    elif (quantity == "TwoPSE"):
        out_str = "Two Proton Separation Energy"
    elif (quantity == "AlphaSE"):
        out_str = "Alpha Separation Energy"
    elif (quantity == "TwoPSGap"):
        out_str = "Two Proton Shell Gap"
    elif (quantity == "TwoNSGap"):
        out_str = "Two Neutron Shell Gap"
    elif (quantity == "DoubleMDiff"):
        out_str = "Double Mass Difference"
    elif (quantity == "N3PointOED"):
        out_str = "Neutron 3-Point Odd-Even Binding Energy Difference"
    elif (quantity == "P3PointOED"):
        out_str = "Proton 3-Point Odd-Even Binding Energy Difference"
    elif (quantity == "SNESplitting"):
        out_str = "Single-Neutron Energy Splitting"
    elif (quantity == "SPESplitting"):
        out_str = "Single-Proton Energy Splitting"
    elif (quantity == "WignerEC"):
        out_str = "Wigner Energy Coefficient"
    elif (quantity == "QDB2t"):
        out_str = "Quad Def Beta2"
    elif (quantity == "BE/A"):
        out_str = "Binding Energy per Nucleon"
    return out_str

