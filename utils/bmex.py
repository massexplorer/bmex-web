import numpy as np
import pandas as pd

df=pd.read_csv("utils/BEAllFull.csv")

def BE(N1,Z1,model):
    try:
        return np.round(df[(df["N"]==N1) & (df["Z"]==Z1) & (df["Model"]==model)]["BE"].to_numpy(),6)[0]
    except IndexError:
        return "Error: Nuclei wtih N="+str(N1)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"

def OneNSE(N1,Z1,model):
    try:
        res1=0.0+BE(N1,Z1,model)
        try:
            res2=0.0+BE(N1-1,Z1,model)
            return res1-res2
        except TypeError:
            return "Error: Nuclei with N="+str(N1-1)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"   
    
    except TypeError:
        return "Error: Nuclei with N="+str(N1)+" andZ="+str(Z1)+" not available from "+str(model)+ " data"

def OnePSE(N1,Z1,model):
    try:
        res1=0+BE(N1,Z1,model)
        try:
            res2=0+BE(N1,Z1-1,model)
            return res1-res2
        except TypeError:
            return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1-1)+" not available from "+str(model)+ " data"   
    
    except TypeError:
        return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"

def TwoNSE(N1,Z1,model):
    try:
        res1=0+BE(N1,Z1,model)
        try:
            res2=0+BE(N1-2,Z1,model)
            return res1-res2
        except TypeError:
            return "Error: Nuclei with N="+str(N1-2)+" and Z="+str(Z1)+"not available from "+str(model)+ " data"   
    
    except TypeError:
        return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"

def TwoPSE(N1,Z1,model):
    try:
        res1=0+BE(N1,Z1,model)
        try:
            res2=0+BE(N1,Z1-2,model)
            return res1-res2
        except TypeError:
            return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1-2)+"not available from "+str(model)+ " data"   
    
    except TypeError:
        return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"

def AlphaSE(N1,Z1,model):
    try:
        res1=0+BE(N1,Z1,model)
        try:
            res2=0+BE(N1-2,Z1-2,model)
            return res1-res2-28.3
        except TypeError:
            return "Error: Nuclei with N="+str(N1-2)+" and Z="+str(Z1-2)+" not available from "+str(model)+ " data"   
    
    except TypeError:
        return "Error: Nuclei with N="+str(N1)+"and Z="+str(Z1)+" not available from "+str(model)+ " data"

def TwoPSGap(N1,Z1,model):
    try:
        res1=0+2*BE(N1,Z1,model)
        try:
            res2=0+BE(N1,Z1+2,model)
            try:
                res3=0+BE(N1,Z1-2,model)         
                return res1-res2-res3
            except TypeError:
                return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1-2)+" not available from "+str(model)+ " data"   
        except TypeError:
            return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1+2)+" not available from "+str(model)+ " data"
    except TypeError:
        return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"

def TwoNSGap(N1,Z1,model):
    try:
        res1=0+2*BE(N1,Z1,model)
        try:
            res2=0+BE(N1+2,Z1,model)
            try:
                res3=0+BE(N1-2,Z1,model)         
                return res1-res2-res3
            except TypeError:
                return "Error: Nuclei with N="+str(N1-2)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"   
        except TypeError:
            return "Error: Nuclei with N="+str(N1+2)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"
    except TypeError:
        return "Error: Nuclei with N="+str(N1)+" and Z="+str(Z1)+" not available from "+str(model)+ " data"

def DoubleMDiff(N1,Z1,model):
    res1=TwoPSE(N1,Z1,model)
    res2=TwoPSE(N1-2,Z1,model)
    
    if isinstance(res1, str):
        return res1
    if isinstance(res2, str):
        return res2
    return 1.0/4.0*(res1-res2)

def N3PointOED(N1,Z1,model):
    res1=OneNSE(N1,Z1,model)
    res2=OneNSE(N1+1,Z1,model)
    
    if isinstance(res1, str):
        return res1
    if isinstance(res2, str):
        return res2
    return 1.0/2.0*(-1)**N1*(res1-res2)

def P3PointOED(N1,Z1,model):
    res1=OnePSE(N1,Z1,model)
    res2=OnePSE(N1,Z1+1,model)
    
    if isinstance(res1, str):
        return res1
    if isinstance(res2, str):
        return res2
    return 1.0/2.0*(-1)**Z1*(res1-res2)

def SNESplitting(N1,Z1,model):
    res1=OneNSE(N1,Z1,model)
    res2=OneNSE(N1+2,Z1,model)
    
    if isinstance(res1, str):
        return res1
    if isinstance(res2, str):
        return res2
    return (-1)**N1*(res1-res2)

def SPESplitting(N1,Z1,model):
    res1=OnePSE(N1,Z1,model)
    res2=OnePSE(N1,Z1+2,model)
    
    if isinstance(res1, str):
        return res1
    if isinstance(res2, str):
        return res2
    return (-1)**Z1*(res1-res2)

def WignerEC(N1,Z1,model):
    if N1!=Z1 or (N1%2!=0) or (Z1%2!=0):
        return "Error: Nuclei must be even-even and with N=Z"
    res1=DoubleMDiff(N1,Z1,model)
    res2=DoubleMDiff(N1,Z1-2,model)
    res3=DoubleMDiff(N1+2,Z1,model)
    if isinstance(res1, str):
        return res1
    if isinstance(res2, str):
        return res2
    if isinstance(res3, str):
        return res3
    return res1-1.0/2.0*(res2+res3)

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
    return out_str
