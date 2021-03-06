from dictionnaries import *
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm

try :
    from tqdm import *
except ImportError :
    def tqdm (arg) :
        return arg

def gen_patchcollection(grid_x,grid_y,data,key) :
    dimX = len(grid_x)
    dimY = len(grid_y)
    patches = []
    print "Computing background"
    print "--------------------------"
    for i in tqdm(range(dimX)) :
        for j in range(dimY) :
            xy = grid_x[i], grid_y[j]
            try :
                width  = grid_x[i+1] - grid_x[i]
            except IndexError :
                pass
            try :
                height = grid_y[j+1] - grid_y[j]
            except IndexError :
                    pass
            rect = Rectangle(xy=xy, width=width, height=height,
                             #rasterized=True,#todo : check usage of this line
                             linewidth=0,
                             linestyle="None")
            patches.append(rect)
    cmap=CMAPS[key]
    patchcollection = PatchCollection(patches,
                                      linewidth=0,
                                      cmap=cmap)
    data1d = data.reshape(-1)
    patchcollection.set_array(data1d)
    return patchcollection


def findRadialLimits(r_p,rads,croper) :
    nr = len(rads)
    jmin,jmax = 0,nr
    while rads[jmin+1] < r_p-croper :
        jmin +=1
    while rads[jmax-2] > r_p+croper :
        jmax -=1
    return jmin-1,jmax-1


def findAzimuthalLimits(r_p,thetas,croper) :
    ns = len(thetas)
    imin,imax = 0,ns
    while r_p*thetas[imin] < -croper :
        imin +=1
    while r_p*thetas[imax-2] > croper :
        imax -=1
    return imin-1,imax-1


def shift(field,thetas,theta_p) :
    """this routine shifts the array along the theta axis
    to make the planet appear in the middle of the plot"""
    ns = len(thetas)
    i_p = 0
    while thetas[i_p] < theta_p :
        i_p += 1
    i_p -= 1
    corr = 2 *(theta_p - thetas[i_p])
    if thetas[i_p] < 0  :
        to_transport = i_p - ns/2
        rfield1 = field[:,to_transport:i_p+1]
        rfield2 = np.concatenate((field[:,i_p+1:],field[:,:to_transport]),axis=1)
    else :
        to_transport = i_p
        rfield1 = np.concatenate((field[:,i_p+1:],field[:,:i_p+1]),axis=1)
        rfield2 = field[:,i_p+1:i_p]#always empty... but this actually works
        
    rfield  = np.concatenate((rfield1,rfield2),axis=1)
    return rfield,corr


def sci_fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    label = '${}$'.format(a)
    if b != 0 :
        label += r'$\times 10^{{{}}}$'.format(b)
    return label

