import numpy as np
import pandas as pd

#df=pd.read_csv("utils/BEAllFull.csv")
modelNames = ['EXP', 'ME2', 'MEdelta', 'PC1', 'NL3S', 'SKMS', 'SKP', 'SLY4', 'SV', 'UNEDF0', 'UNEDF1']
models = [pd.read_hdf('utils/models.h5', n) for n in modelNames]
data_dict = {modelNames[i]: models[i] for i in range(len(modelNames))}

qinput = ['BE', 'OneNSE', 'OnePSE', 'TwoNSE', 'TwoPSE', 'AlphaSE', 'TwoNSGap', 'TwoPSGap', 'DoubleMDiff', 'N3PointOED', 'P3PointOED', 'SNESplitting', 'SPESplitting', 'WignerEC', 'QDB2t']
qnames = ['Binding_Energy_(MeV)', 'One Neutron Separation Energy', 'One Proton Separation Energy', 'Two Neutron Separation Energy', 
'Two Proton Separation Energy', 'Alpha Separation Energy', 'Two Proton Shell Gap', 'Two Neutron Shell Gap', 
'Double Mass Difference', 'Neutron 3-Point Odd-Even Binding Energy Difference', 'Proton 3-Point Odd-Even Binding Energy Difference',
'Single-Neutron Energy Splitting', 'Single-Proton Energy Splitting', 'Wigner Energy Coeffiency', 'Quad_Def_Beta2_total']
q_dict = {qinput[j]: qnames[j] for j in range(len(qinput))}

def QuanValue(N1,Z1,model,quan,w=0):
    df = data_dict[model]
    try:
        if w==3 and N1==Z1:
            return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)][q_dict[quan]])*float(df[(df["N"]==N1) & (df["Z"]==Z1)][q_dict['WignerEC']]),6)
        else:
            return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)][q_dict[quan]]),6)*-1.0
    except:
        return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def BE(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Binding_Energy_(MeV)"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def OneNSE(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["One Neutron Separation Energy"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def OnePSE(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["One Proton Separation Energy"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def TwoNSE(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Two Neutron Separation Energy"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def TwoPSE(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Two Proton Separation Energy"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def AlphaSE(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Alpha Separation Energy"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def TwoPSGap(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Two Proton Shell Gap"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def TwoNSGap(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Two Neutron Shell Gap"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def DoubleMDiff(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Double Mass Difference"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def N3PointOED(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Neutron 3-Point Odd-Even Binding Energy Difference"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def P3PointOED(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Proton 3-Point Odd-Even Binding Energy Difference"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

# def SNESplitting(N1,Z1,model,w=0):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Single-Neutron Energy Splitting"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)
#     # wig = [0, Wig(N1,Z1)-Wig(N1-1,Z1), Wig2(N1,Z1)-Wig2(N1-1,Z1)]
#     # wig2 = [0, Wig(N1+2,Z1)-Wig(N1+1,Z1), Wig2(N1+2,Z1)-Wig2(N1+1,Z1)]
#     # res1=OneNSE(N1,Z1,model)
#     # res2=OneNSE(N1+2,Z1,model)
    
#     # if isinstance(res1, str):
#     #     return res1  
#     # if isinstance(res2, str):
#     #     return res2  
#     # return (-1)**N1*((res1-wig[w])-(res2-wig2[w]))

# def SPESplitting(N1,Z1,model,w=0):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Single-Proton Energy Splitting"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)
#     # wig = [0, Wig(N1,Z1)-Wig(N1,Z1-1), Wig2(N1,Z1)-Wig2(N1,Z1-1)]
#     # wig2 = [0, Wig(N1,Z1+2)-Wig(N1,Z1+1), Wig2(N1,Z1+2)-Wig2(N1,Z1+1)]
#     # res1=OnePSE(N1,Z1,model)
#     # res2=OnePSE(N1,Z1+2,model)
    
#     # if isinstance(res1, str):
#     #     return res1
#     # if isinstance(res2, str):
#     #     return res2
#     # return (-1)**Z1*((res1-wig[w])-(res2-wig2[w]))

# def WignerEC(N1,Z1,model):
#     df = data_dict[model]
#     try:
#         return np.round(float(df[(df["N"]==N1) & (df["Z"]==Z1)]["Wigner Energy Coeffiency"]),6)
#     except:
#         return "Error: "+str(model)+" data does not have this quantity available for Nuclei with N="+str(N1)+" and Z="+str(Z1)

def Wig(n, z):
    return (1.8*np.exp(-380*((n-z)/(n+z))**2))-(.84*abs(n-z)*np.exp(-(((n+z)/26)**2)))

def Wig2(n, z):
    return -47*(abs(n-z)/(n+z))

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
    return out_str

