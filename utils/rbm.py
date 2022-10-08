import glob
import numpy as np
from scipy import optimize
import plotly.graph_objs as go
import time
from utils.rmf_rbm_density import *

from utils import rmf_rbm_hybrid as rmf_rbm

def NM_to_RMF(params):

      #rmf_params = np.zeros(params.shape)

      hbarc = 197.32698
      mn = 939.0/hbarc
      ms = params[0]/hbarc
      mv = 782.500/hbarc
      mr = 763.00/hbarc
      kf = (params[1]*3.0*np.pi**2/2.0)**(1.0/3.0)
      eb = params[2]/hbarc
      mstar = params[3]*mn
      K = params[4]/hbarc
      zeta = params[5]
      J = params[6]/hbarc
      L = params[7]/hbarc   
      m=mstar                                         #simple notation
      ef=np.sqrt(kf**2+m**2)                             #Fermi energy
      logk=np.log((kf+ef)/m)                             #useful log.
      rhov=(2*kf**3)/(3*np.pi**2)                        #vector density
      rhos=(m*kf*ef-m**3*logk)/np.pi**2                  #scalar density
      rhosp=(kf*(ef**2+2*m**2)/ef-3*m**2*logk)/np.pi**2  #scalar density' 
      edens=(kf*ef*(kf**2+ef**2)-m**4*logk)/(4*np.pi**2) #energy density      
      ef=np.sqrt(kf**2+mstar**2)               #Fermi energy
      en=eb+mn                              #nucleon energy
      W0=en-ef                              #vector potential
      gv2=mv**2/(rhov/W0-zeta*W0**2/6)      #coupling constant    
      ef=np.sqrt(kf**2+mstar**2)                   #Fermi energy
      en=eb+mn                                  #nucleon energy
      W0=en-ef                                  #vector potential
      gv2=mv**2/(rhov/W0-zeta*W0**2/6)          #coupling constant
      mvs2=mv**2+0.5*zeta*gv2*W0**2        #effective omega mass
      #Solve for scalar couplings:
      P0=mn-mstar                               #scalar potential
      #Compute the A-matrix
      A11=P0**2/2                               #A(1,1)
      A12=P0**3/6                               #A(1,2)
      A13=P0**4/24                              #A(1,3)
      A21=P0                                    #A(2,1)
      A22=P0**2/2                               #A(2,2)
      A23=P0**3/6                               #A(2,3)
      A31=1.0                             #A(3,1)
      A32=P0                                    #A(3,2)
      A33=P0**2/2                               #A(3,3)
      #Compute the B-vector:
      B1f=+en*rhov-edens                        #B1nucleons
      B1m=-(mv*W0)**2/(2*gv2)-zeta*W0**4/8      #B1mesons
      B3n=(mstar/ef)**2                         #B3numerator
      B3d=kf**2/(3*ef*rhov)+gv2/mvs2-K/(9*rhov) #B3denominator
      B1=B1f+B1m                                #B(1)
      B2=rhos                                   #B(2)
      B3=B3n/B3d-rhosp                          #B(3)
      #Compute the Inverse of A (call it M):
      Determ=A11*(A22*A33-A23*A32) \
           -A21*(A12*A33-A13*A32) \
           +A31*(A12*A23-A13*A22)
      M11=+(A22*A33-A23*A32)/Determ             #M(1,1) 
      M12=-(A12*A33-A13*A32)/Determ             #M(1,2)
      M13=+(A12*A23-A13*A22)/Determ             #M(1,3)
      M21=-(A21*A33-A23*A31)/Determ             #M(2,1)
      M22=+(A11*A33-A13*A31)/Determ             #M(2,2) 
      M23=-(A11*A23-A13*A21)/Determ             #M(2,3) 
      M31=+(A21*A32-A22*A31)/Determ             #M(3,1) 
      M32=-(A11*A32-A12*A31)/Determ             #M(3,2) 
      M33=+(A11*A22-A12*A21)/Determ             #M(3,3) 
      #Compute coupling constants:
      C1=M11*B1+M12*B2+M13*B3                   #C(1)
      C2=M21*B1+M22*B2+M23*B3                   #C(2)
      C3=M31*B1+M32*B2+M33*B3                   #C(3)
      gs2=ms**2/C1                              #gs2
      gs=np.sqrt(gs2)                              #gs
      kappa=C2                                  #kappa (in fm^-1)
      lamb=C3                                 #lambda 
      P0=mn-mstar                                       #Phi0=M-M*
      mss2=ms**2+kappa*gs2*P0+lamb*gs2*P0**2/2        #(ms*)^2
      Css2=gs2/mss2                                     #(Cs*)^2
      #Compute (Cv*)^2:
      ef=np.sqrt(kf**2+mstar**2)                           #Fermi energy
      en=eb+mn                                          #E/N
      W0=en-ef                                          #W0=gv*V0
      mvs2=mv**2+zeta*gv2*W0**2/2                       #(mv*)^2
      Cvs2=gv2/mvs2                                     #(Cv*)^2  
      #Compute quantity "xi":
      xi=(3*rhov/ef)/((1/Css2)+rhosp)                   #useful quantity      
      #Extract isovector parameters:
      J1=kf**2/(6*ef)                                   #isoscalar contribution to J             
      L1=J1*(1+(mstar/ef)**2*(1+xi))                    #isoscalar contribution to L
      J2=J-J1
      L2=L-L1
      Crs2=8*J2/rhov                                #(Cr*)^2
      Lambdav=(3*J2-L2)/(96*J2**2*Cvs2*W0)
      gr2=(Crs2*mr**2)/(1-2*Lambdav*Crs2*W0**2)

      rmf_params = np.array([ms, np.sqrt(gs2), np.sqrt(gv2), np.sqrt(gr2), kappa, lamb, zeta, Lambdav])
    #   if(gs2<0.0 or gv2<0.0 or gr2<0.0):
    #     print("Negative! ",gs2,gv2,gr2,(1-2*Lambdav*Crs2*W0**2))
    #     print(params)
      return rmf_params

def rbm_emulator(nuc,theta):
    # ytrue = np.array([2.70,7.98,
    #           3.48,8.55,
    #           3.48,8.67,
    #           8.68,
    #           4.27,8.71,
    #           8.25,
    #           4.63,8.52,
    #           4.71,8.36,
    #           4.95,8.30,
    #           5.50,7.87,
    #           ])
    #print(theta.shape)

    A = [16, 40, 48, 68, 90, 100, 116, 132, 144, 208]
    nbasis = [74, 128, 133, 145, 189, 202, 201, 211, 245, 274]

    func = [rmf_rbm.rmf_poly_16O_0,
        rmf_rbm.rmf_poly_40Ca_0,
        rmf_rbm.rmf_poly_48Ca_0,
        rmf_rbm.rmf_poly_68Ni_0,
        rmf_rbm.rmf_poly_90Zr_0,
        rmf_rbm.rmf_poly_100Sn_0,
        rmf_rbm.rmf_poly_116Sn_0,
        rmf_rbm.rmf_poly_132Sn_0,
        rmf_rbm.rmf_poly_144Sm_0,
        rmf_rbm.rmf_poly_208Pb_0,
        ]

    jacfunc = [rmf_rbm.rmf_poly_16O_0_jac,
            rmf_rbm.rmf_poly_40Ca_0_jac,
            rmf_rbm.rmf_poly_48Ca_0_jac,
            rmf_rbm.rmf_poly_68Ni_0_jac,
            rmf_rbm.rmf_poly_90Zr_0_jac,
            rmf_rbm.rmf_poly_100Sn_0_jac,
            rmf_rbm.rmf_poly_116Sn_0_jac,
            rmf_rbm.rmf_poly_132Sn_0_jac,
            rmf_rbm.rmf_poly_144Sm_0_jac,
            rmf_rbm.rmf_poly_208Pb_0_jac,
            ]

    nucenergy_func=[rmf_rbm.nucleon_energy_16O_0,
                    rmf_rbm.nucleon_energy_40Ca_0,
                    rmf_rbm.nucleon_energy_48Ca_0,
                    rmf_rbm.nucleon_energy_68Ni_0,
                    rmf_rbm.nucleon_energy_90Zr_0,
                    rmf_rbm.nucleon_energy_100Sn_0,
                    rmf_rbm.nucleon_energy_116Sn_0,
                    rmf_rbm.nucleon_energy_132Sn_0,
                    rmf_rbm.nucleon_energy_144Sm_0,
                    rmf_rbm.nucleon_energy_208Pb_0,
                    ]
    fldenergy_func=[rmf_rbm.field_energy_16O_0,
                    rmf_rbm.field_energy_40Ca_0,
                    rmf_rbm.field_energy_48Ca_0,
                    rmf_rbm.field_energy_68Ni_0,
                    rmf_rbm.field_energy_90Zr_0,
                    rmf_rbm.field_energy_100Sn_0,
                    rmf_rbm.field_energy_116Sn_0,
                    rmf_rbm.field_energy_132Sn_0,
                    rmf_rbm.field_energy_144Sm_0,
                    rmf_rbm.field_energy_208Pb_0,
                    ]
    protonrad_func=[rmf_rbm.proton_radius_16O_0,
                    rmf_rbm.proton_radius_40Ca_0,
                    rmf_rbm.proton_radius_48Ca_0,
                    rmf_rbm.proton_radius_68Ni_0,
                    rmf_rbm.proton_radius_90Zr_0,
                    rmf_rbm.proton_radius_100Sn_0,
                    rmf_rbm.proton_radius_116Sn_0,
                    rmf_rbm.proton_radius_132Sn_0,
                    rmf_rbm.proton_radius_144Sm_0,
                    rmf_rbm.proton_radius_208Pb_0,
                    ]
    rmf_param = NM_to_RMF(theta)

    x0 = np.zeros((nbasis[nuc]))

    start = time.time()
    sol = optimize.root(func[nuc], x0, args=(rmf_param), jac=jacfunc[nuc], method="hybr", options={'col_deriv': 1, 'xtol': 1e-8})
    end = time.time()

    protrad = np.sqrt(protonrad_func[nuc](sol.x, rmf_param))
    energy = (nucenergy_func[nuc](sol.x, rmf_param) - \
        fldenergy_func[nuc](sol.x, rmf_param)) + 0.75*41*A[nuc]**(-1.0/3.0)
    return energy, protrad, sol, end-start

def plot_dens(nuc,sol):

    directory=glob.glob("HybridPolynomials/Results_"+nuc+"*/Basis/")[0]

    nuc_dict={'16O':0,'40Ca':1,'48Ca':2,'68Ni':3,'90Zr':4,'100Sn':5,'116Sn':6,'132Sn':7,'144Sm':8,'208Pb':9}
    j_dict={'16O':0,'40Ca':1,\
        '48Ca':[[0.5,1.5,0.5,2.5,1.5,0.5,3.5],[0.5,1.5,0.5,2.5,1.5,0.5]],'68Ni':3,'90Zr':4,'100Sn':5,'116Sn':6,'132Sn':7,'144Sm':8,'208Pb':9}

    index = nuc_dict[nuc]

    pstates = [3, 6, 6, 7,  10, 11, 11, 11, 13, 16]
    nstates = [3, 6, 7, 10, 11, 11, 14, 16, 16, 22]



    nx = 400
    dx=0.0375
    # x = np.arange(0.05,20.05,0.05)
    x = np.arange(dx,dx*nx+dx,dx)
    coeffs=[1.0,0.0,0.0,0.0,0.0]
    rho = np.zeros((nx,2))
    for state in range(1,nstates[index]+1):
        filename = directory + "Nucleus_"+nuc+"_NeutronsF_Level"+str(state)+".txt"
        temp = np.loadtxt(filename)**2
        nbasis = temp.shape[0]//nx
        for i in range(nx):
            for basis in range(nbasis):
                rho[i,0] += coeffs[basis]*temp[i+basis*nx]*(2*j_dict[nuc][0][state-1] + 1)/(4*np.pi*x[i]**2)
        filename = directory + "Nucleus_"+nuc+"_NeutronsG_Level"+str(state)+".txt"
        temp = np.loadtxt(filename)**2
        nbasis = temp.shape[0]//nx
        for i in range(nx):
            for basis in range(nbasis):
                rho[i,0] += coeffs[basis]*temp[i+basis*nx]*(2*j_dict[nuc][0][state-1] + 1)/(4*np.pi*x[i]**2)
    for state in range(1,pstates[index]+1):
        filename = directory + "Nucleus_"+nuc+"_ProtonsF_Level"+str(state)+".txt"
        temp = np.loadtxt(filename)**2
        nbasis = temp.shape[0]//nx
        for i in range(nx):
            for basis in range(nbasis):
                rho[i,1] += coeffs[basis]*temp[i+basis*nx]*(2*j_dict[nuc][1][state-1] + 1)/(4*np.pi*x[i]**2)
        filename = directory + "Nucleus_"+nuc+"_ProtonsG_Level"+str(state)+".txt"
        temp = np.loadtxt(filename)**2
        nbasis = temp.shape[0]//nx
        for i in range(nx):
            for basis in range(nbasis):
                rho[i,1] += coeffs[basis]*temp[i+basis*nx]*(2*j_dict[nuc][1][state-1] + 1)/(4*np.pi*x[i]**2)

    return rho

def dens(nuc, x0):
    if(nuc == '48Ca'):
        rhon = rmf_rbm_48Ca_neutdensity(x0)
        rhop = rmf_rbm_48Ca_protdensity(x0)
    return np.asarray([rhon,rhop])

def plot_dens(axis_label,rho):
    x = np.arange(0,20,0.02)
    layout = go.Layout(
        #title=f"ROC Curve (AUC = {auc_score:.3f})",
        title=f"Density",
        xaxis=dict(title="R (fm)", gridcolor="#2f3445",title_font_size=14),
        yaxis=dict(title="r$\rho$", gridcolor="#2f3445",title_font_size=14),
        #legend=dict(x=0, y=1.05, orientation="h"),
        #margin=dict(l=100, r=10, t=25, b=40),
        plot_bgcolor="#282b38",
        paper_bgcolor="#282b38",
        font={"color": "#a5b1cd", "size": 14},
    )

    #figure = px.line(x=Z, y=output, markers=True)
    figure = go.Figure([
        go.Scatter(
            name='Neutrons',
            x=x,
            y=rho[0,:],
            mode='lines',
            line=dict(color='#e76f51'),#'rgb(100, 100, 80)'),
        ),
        go.Scatter(
            name='Protons',
            x=x,
            y=rho[1,:],
            mode='lines',
            line=dict(color='#e76f51'),#'rgb(100, 100, 80)'),
        ),
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


#  -1.0   1.00000   0.0     0.0    72.45440     -1.0   1.00000   0.0     0.0    69.57074
#  -2.0   1.00000   0.0     0.0    54.17861     -2.0   1.00000   0.0     0.0    52.65930
#   1.0   1.00000   0.0     1.0    50.51665      1.0   1.00000   0.0     1.0    48.73188
#  -3.0   1.00000   0.0     0.0    34.94008     -3.0   1.00000   0.0     0.0    33.84392
#   2.0   1.00000   0.0     1.0    27.23649      2.0   1.00000   0.0     1.0    25.91329
#  -1.0   1.00000   1.0     1.0    24.76784     -1.0   1.00000   1.0     1.0    21.21943
#  -4.0   1.00000   0.0     0.0    16.25656      0.0   0.00000   0.0     0.0     0.00000