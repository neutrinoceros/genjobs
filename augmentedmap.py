#!/usr/bin/python
#-*-coding:utf-8-*-
# --------------------------
# Author : Clément Robert
# written may 2017
# --------------------------

from lib_parsing import * # built-in module that comes with the toolbox
import matplotlib.pyplot as plt

# Defintions **********************************************************

# PARSING *************************************************************

#args = getScriptArgs()

config = ("/home/crobert/Bureau/sandboxPLOT2D/data/in/phase0.par") #tmp
bg_key = "d"#tmp
NOUT = 20#tmp
crop_limit = 5.#tmp
azim_crop = True



OUTDIR  = parseString(config, 'OutputDir'       )
PlanetF = parseString(config, 'PlanetConfig'    )#to use
SPACING = parseString(config, 'RadialSpacing'   )
NRAD    = parseValue (config, 'nrad'            )
NSEC    = parseValue (config, 'nsec'            )
RMIN    = parseValue (config, 'rmin',      float)
RMAX    = parseValue (config, 'rmax',      float)
ninterm = parseValue (config, 'ninterm'         )
DT      = parseValue (config, 'DT',        float)

DR      = (RMAX-RMIN)/NRAD
dtheta  = 2.*np.pi/NSEC

base_theta    = np.linspace(0.,2*np.pi,NSEC)
rotated_theta = np.linspace(-np.pi,np.pi,NSEC)


# get planetary info
r_p     = 1.#tmp
theta_p = 0#tmp
q_p     = 0.001#tmp


# MAIN LOOP ***********************************************************

# optionnally, we could have the option of using cartesian coordinates


# define plotting objects (fig, ax), choosing aspect carefully to have 
# same scale in both directions 
# this will be easy to spot when we plot hill "sphere"
fig = plt.figure()
ax = fig.add_subplot(111,aspect='auto')
#ax = fig.add_subplot(211,aspect='auto')
#ax2 = fig.add_subplot(212,aspect='auto')

bg_field, bgfile = get2Dfield(bg_key,NRAD,NSEC,OUTDIR,NOUT)
bg_used_radii    = getrad(RMIN,RMAX,NRAD,DR,bg_key,SPACING)

# crop plotting region, cut out fields (optional)
def Hill_radius(r_p,q_p) :
    return r_p*(q_p/3)**(1./3)


def findRadialLimits(r_p,q_p,rads,croper=5.) :
    R_H = Hill_radius(r_p,q_p)
    nr = len(rads)
    jmin,jmax = 0,nr-1
    while rads[jmin] < r_p-croper*R_H :
        jmin +=1
    while rads[jmax] > r_p+croper*R_H :
        jmax -=1
    return jmin,jmax

def findAzimLimits(r_p,q_p,thetas,croper=5.) :
    R_H = Hill_radius(r_p,q_p)
    ns = len(thetas)
    imin,imax = 0,ns-1
    while r_p*thetas[imin] < -croper*R_H :#FIXME
        imin +=1
    while r_p*thetas[imax] > croper*R_H :#FIXME
        imax -=1
    return imin,imax

def crop_field(field,jmin,jmax) :
    cfield = field[jmin:jmax,:]
    return cfield


#plot background
# define background field, vt, vr
# useful options should be density, label, FLI

def rotate(field,thetas,theta_p) :
    ns = len(thetas)
    i_p = 0
    while thetas[i_p] < theta_p :
        i_p += 1

    cesure  = ns/2 - i_p
    ffield1 = np.concatenate((field[:,-cesure:ns-1],field[:,0:i_p]),axis=1)
    ffield2 = field[:,i_p:-cesure]
    ffield  = np.concatenate((ffield1,ffield2),axis=1)
    return ffield,cesure


Jmin,Jmax = findRadialLimits(r_p,q_p,bg_used_radii,crop_limit)
bg_field,cesure = rotate(bg_field,base_theta,theta_p)
bg_used_radii_crop = bg_used_radii[Jmin:Jmax]
bg_field_crop = bg_field[Jmin:Jmax,:]

#These two lines need to be run after rotation...
i_p = 0
while base_theta[i_p] < theta_p :
    i_p += 1
j_p = 0
while bg_used_radii_crop[j_p] < r_p :
    j_p += 1

bg_used_theta = rotated_theta

#finding limits of the plot
if azim_crop :
    azim_crop = crop_limit
else :
    azim_crop = 1000
Imin,Imax = findAzimLimits(r_p,q_p,bg_used_theta,azim_crop)


im = ax.imshow(bg_field_crop,cmap='viridis',aspect="auto")


# set ticks
ax.set_xticks([0,NSEC/4,NSEC/2,3*NSEC/4,NSEC])
ax.set_xticklabels([r"$-\pi$",r"$-\pi/2$",r"$0$",r"$\pi/2$",r"$\pi$"])

ytickslab = [r"${0}$".format(round(bg_used_radii_crop[int(n)],2)) for n in ax.get_yticks()[:-1]]
ax.set_yticklabels(ytickslab)
ax.set_xlabel(r"$\theta$", size=20)
ax.set_ylabel(r"$r$",      size=20)

#set limits
ax.set_xlim(Imin,Imax)
ax.set_ylim(0,Jmax-(Jmin+1))
# draw hill sphere(s) #todo : make this optional
def circle(x0,y0,r,theta) :
    return x0+r*np.cos(theta), y0+r*np.sin(theta)

R_H = Hill_radius(r_p,q_p)
thetas=np.linspace(0,2*np.pi,100)

R_H_code = R_H/(r_p*dtheta)
ax.plot( *circle(NSEC/2,j_p,R_H_code,thetas),         c='w', ls='--')
ax.plot( *circle(NSEC/2,j_p,0.3*R_H_code,thetas),     c='r', ls='-')

cb = fig.colorbar(im)
cb.set_label("background value")#tmp
# draw stream lines (optional)


# print out or save figure (optional flag)
#plt.show()
fig.savefig("coucou.png")
