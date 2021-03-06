from parsingFunctions      import *
from fieldGettingFunctions import *

# /!\ dev note : 
# all recipes must use a completely identical list of arguments

def getSigmaInf(nrad,nsec,rmin,rmax,dr,outdir,nout,Rinf,Rmed) :
    #dev note : this a prototype, we're missing declaration and testing
    sigmaMed,filesig = get2Dfield('d' ,nrad,nsec,outdir,nout)

    sigmaInf = sigmaMed.copy()
    for i in range(1, nrad) :
        for j in range(nsec) :
          sigmaInf[i,j] = ( sigmaMed[i-1,j] * (Rmed[i] - Rinf[i])  \
                          + sigmaMed[i,j] * (Rinf[i] - Rmed[i-1]) \
                          ) / (Rmed[i] - Rmed[i-1])  
    return sigmaInf, filesig


def getflow(nrad,nsec,rmin,rmax,dr,outdir,nout,Rinf,Rmed) :
    """new method : define flow at Rinf by shifting density
    --extrapolation based on what is found is fargo--"""
    print "warning : this method is known for showing a distorted version of the mass flow"
    print "use -rf instead of '-f'"
    sigmaInf,filesig = getSigmaInf(nrad,nsec,rmin,rmax,dr,outdir,nout,Rinf,Rmed)

    sigma,filesig = get2Dfield('d' ,nrad,nsec,outdir,nout)
    vrad,filevrad = get2Dfield('vr',nrad,nsec,outdir,nout)
    used_files  = [filesig, filevrad]

    flow2D = 2*np.pi*vrad*sigmaInf
    for i in range(nrad) :
        flow2D[i] *= Rinf[i]
    return flow2D, used_files


def getVThetaCent(nrad,nsec,rmin,rmax,dr,outdir,nout,Rinf,Rmed) :
    vtheta,filevtheta = get2Dfield('vt',nrad,nsec,outdir,nout)
    vt_cent = vtheta * 0.0
    for i in range(nrad) :
        for j in range(nsec) :
            if j == nsec-1 :
                vt_cent[i,j] = 0.5 * (vtheta[i,j] + vtheta[i,0])
            else :
                vt_cent[i,j] = 0.5 * (vtheta[i,j] + vtheta[i,j+1])
    return vt_cent, filevtheta


def getVRadCent(nrad,nsec,rmin,rmax,dr,outdir,nout,Rinf,Rmed) :
    vrad,filevrad = get2Dfield('vr',nrad,nsec,outdir,nout)
    vr_cent = vrad * 0.0
    for i in range(nrad) :
        for j in range(nsec) :
            if i == nrad-1 :
                vr_cent[i,j] = vrad[i,j]
            else :
                vr_cent[i,j] = ( (Rmed[i]  -Rinf[i])*vrad[i+1,j]\
                                  +(Rinf[i+1]-Rmed[i])*vrad[i,j]) / (Rinf[i+1]+Rinf[i])
    return vr_cent, filevrad


# -----------------------------------------------------------

RECIPES = {"sigmaInf" : getSigmaInf,
           "flow"     : getflow,
           "vtcent"   : getVThetaCent,
           "vrcent"   : getVRadCent}
