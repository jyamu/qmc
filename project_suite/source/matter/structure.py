#! /usr/bin/env python

import os
from copy import deepcopy
from numpy import array,floor,empty,dot,diag,sqrt,pi,mgrid,exp,append,arange,ceil,cross,cos,sin,identity,ndarray,atleast_2d,around,ones
from numpy.linalg import inv,det,norm
from unit_converter import convert
from extended_numpy import nearest_neighbors
from generic import obj
from developer import DevBase,unavailable


try:
    from scipy.special import erfc
except ImportError:
    erfc = unavailable('scipy.special','erfc')
#end try
try:
    from matplotlib.pyplot import plot,subplot,title,xlabel,ylabel
except (ImportError,RuntimeError):
    plot,subplot,title,xlabel,ylabel = unavailable('matplotlib.pyplot','plot','subplot','title','xlabel','ylabel')
#end try



def equate(expr):
    return expr
#end def equate

def negate(expr):
    return not expr
#end def negate



def kmesh(kaxes,dim,shift=None):
    if shift is None:
        shift = (0.,0,0)
    #end if
    ndim = len(dim)
    d = array(dim)
    s = array(shift)
    s.shape = 1,ndim
    d.shape = 1,ndim
    kp = empty((1,ndim),dtype=float)
    kgrid = empty((d.prod(),ndim))
    n=0
    for k in range(dim[2]):
        for j in range(dim[1]):
            for i in range(dim[0]):
                kp[:] = i,j,k
                kp = dot((kp+s)/d,kaxes)
                #kp = (kp+s)/d
                kgrid[n] = kp
                n+=1
            #end for
        #end for
    #end for
    return kgrid
#end def kmesh


def tile_points(points,tilevec,axin):
    if not isinstance(points,ndarray):
        points = array(points)
    #end if
    if not isinstance(tilevec,ndarray):
        tilevec = array(tilevec)
    #end if
    if not isinstance(axin,ndarray):
        axin = array(axin)
    #end if
    t = tilevec
    if len(points.shape)==1:
        npoints,dim = len(points),1
    else:
        npoints,dim = points.shape
    #end if
    ntpoints = npoints*t.prod()
    if ntpoints==0:
        tpoints = array([])
    else:
        tpoints  = empty((ntpoints,dim))
        ns=0
        ne=npoints
        for k in range(t[2]):
            for j in range(t[1]):
                for i in range(t[0]):
                    v = dot(array([[i,j,k]]),axin)
                    for d in range(dim):
                        tpoints[ns:ne,d] = points[:,d]+v[0,d]
                    #end for
                    ns+=npoints 
                    ne+=npoints
                #end for
            #end for
        #end for
    #end if
    axes = dot(diag(t),axin)
    return tpoints,axes
#end def tile_points





class Sobj(DevBase):
    None
#end class Sobj



class Structure(Sobj): 
    def __init__(self,axes=None,scale=1.,elem=None,pos=None,
                 center=None,kpoints=None,kweights=None,kgrid=None,kshift=(0,0,0),permute=None,units=None,tiling=None,rescale=True,dim=3):
        if center is None:
            if axes !=None:
                center = array(axes).sum(0)/2
            else:
                center = dim*[0]
            #end if
        #end if
        if axes is None:
            axes = []
        #end if
        if elem is None:
            elem = []
        #end if
        if pos is None:
            pos = empty((0,dim))
        #end if
        self.scale  = 1.
        self.units  = units
        self.dim    = dim
        self.center = array(center)
        self.axes   = array(axes)
        self.elem   = array(elem)
        self.pos    = array(pos)
        self.kpoints  = empty((0,dim))            
        self.kweights = empty((0,))         
        self.folded_structure = None
        self.remove_folded_structure()
        if len(axes)==0:
            self.kaxes=array([])
        else:
            self.kaxes=2*pi*inv(self.axes).T
        #end if
        if tiling!=None:
            self.tile(tiling,in_place=True)
        #end if
        if kpoints!=None:
            self.add_kpoints(kpoints,kweights)
        #end if
        if kgrid!=None:
            self.add_kmesh(kgrid,kshift)
        #end if        
        if rescale:
            self.rescale(scale)
        else:
            self.scale = scale
        #end if
        if permute!=None:
            self.permute(permute)
        #end if
    #end def __init__

    def remove_folded_structure(self):
        #print 'removing folded structure',self.folded_structure.__class__.__name__
        self.folded_structure = None
        self.tmatrix = None
    #end def remove_folded_structure

            
    def group_atoms(self):
        if len(self.elem)>0:
            order = self.elem.argsort()
            self.elem = self.elem[order]
            self.pos  = self.pos[order]
        #end if
        if self.folded_structure!=None:
            self.folded_structure.group_atoms()
        #end if
    #end def group_atoms


    def reset_axes(self,axes=None):
        if axes is None:
            axes = self.axes
        else:
            axes = array(axes)
        #end if
        self.axes  = axes
        self.kaxes = 2*pi*inv(axes).T
        self.center = axes.sum(0)/2
        self.remove_folded_structure()
    #end def reset_axes


    def adjust_axes(self,axes):
        self.skew(dot(inv(self.axes),axes))
    #end def adjust_axes
        
        
    def bounding_box(self,scale=1.0,box='tight',recenter=False):
        pmin    = self.pos.min(0)
        pmax    = self.pos.max(0)
        pcenter = (pmax+pmin)/2
        prange  = pmax-pmin
        if box=='tight':
            axes = diag(prange)
        elif box=='cubic' or box=='cube':
            prmax = prange.max()
            axes = diag((prmax,prmax,prmax))
        elif isinstance(box,ndarray) or isinstance(box,list):
            box = array(box)
            if box.shape!=(3,3):
                self.error('requested box must be 3-dimensional (3x3 axes)\n  you provided: '+str(box)+'\n shape: '+str(box.shape))
            #end if
            binv = inv(box)
            pu = dot(self.pos,binv)
            pmin    = pu.min(0)
            pmax    = pu.max(0)
            pcenter = (pmax+pmin)/2
            prange  = pmax-pmin
            axes    = dot(diag(prange),box)
        else:
            self.error("invalid request for box\n  valid options are 'tight', 'cubic', or axes array (3x3)\n  you provided: "+str(box))
        #end if
        self.reset_axes(scale*axes)
        self.slide(self.center-pcenter,recenter)
    #end def bounding_box


    def permute(self,permutation):
        dim = self.dim
        P = empty((dim,dim),dtype=int)
        if len(permutation)!=dim:
            self.error(' permutation vector must have {0} elements\n you provided {1}'.format(dim,permutation))
        #end if
        for i in range(dim):
            p = permutation[i]
            pv = zeros((dim,),dtype=int)
            if p=='x' or p=='0':
                pv[0] = 1
            elif p=='y' or p=='1':
                pv[1] = 1
            elif p=='z' or p=='2':
                pv[2] = 1
            #end if
            P[:,i] = pv[:]
        #end for
        self.center = dot(self.center,P)
        if len(self.axes)>0:
            self.axes = dot(self.axes,P)
        #end if
        if len(self.pos)>0:
            self.pos = dot(self.pos,P)
        #end if
        if len(self.kaxes)>0:
            self.kaxes = dot(self.kaxes,P)
        #end if
        if len(self.kpoints)>0:
            self.kpoints = dot(self.kpoints,P)
        #end if
        if self.folded_structure!=None:
            T = self.tmatrix
            if abs(T-diag(T)).sum()>1e-6:
                self.remove_folded_structure()
            else:
                self.folded_structure.permute(permutation)
            #end if
        #end if
    #end def permute
                

    def upcast(self,DerivedStructure):
        if not issubclass(DerivedStructure,Structure):
            self.error(DerivedStructure.__name__,'is not derived from Structure')
        #end if
        ds = DerivedStructure()
        for name,value in self.iteritems():
            ds[name] = deepcopy(value)
        #end for
        return ds
    #end def upcast

    
    def incorporate(self,other):
        self.elem = array(list(self.elem)+list(other.elem))
        self.pos  = array(list(self.pos )+list(other.pos ))
    #end def incorporate


    def distances(self,pos1=None,pos2=None):
        if isinstance(pos1,Structure):
            pos1 = pos1.pos
        #end if
        if pos2==None:
            if pos1==None:
                return sqrt((self.pos**2).sum(1))
            else:
                pos2 = self.pos
            #end if
        #end if
        if len(pos1)!=len(pos2):
            self.error('positions arrays are not the same length')
        #end if
        return sqrt(((pos1-pos2)**2).sum(1))
    #end def distances

    
    def volume(self):
        if len(self.axes)==0:
            return None
        else:
            return abs(det(self.axes))
        #end if
    #end def volume


    def rwigner(self):
        if self.dim!=3:
            self.error('rwigner is currently only implemented for 3 dimensions')
        #end if
        rmin = 1e90
        n=empty((1,3))
        for k in range(-1,2):
            for j in range(-1,2):
                for i in range(-1,2):
                    if i!=0 or j!=0 or k!=0:
                        n[:] = i,j,k
                        rmin = min(rmin,.5*norm(dot(n,self.axes)))
                    #end if
                #end for
            #end for
        #end for
        return rmin
    #end def rwigner


    def rinscribe(self):
        if self.dim!=3:
            self.error('rinscribe is currently only implemented for 3 dimensions')
        #end if
        radius = 1e99
        dim=3
        axes=self.axes
        for d in range(dim):
            i = d
            j = (d+1)%dim
            rc = cross(axes[i,:],axes[j,:])
            radius = min(radius,.5*abs(det(axes))/norm(rc))
        #end for
        return radius
    #end def rinscribe


    def rmin(self):
        return self.rwigner()
    #end def rmin


    def rcell(self):
        return self.rinscribe()
    #end def rcell


    def set_orig(self):
        self.orig_pos = pos.copy()
    #end def set_orig

    
    def rescale(self,scale):
        self.scale  *= scale
        self.axes   *= scale
        self.pos    *= scale
        self.center *= scale
        self.kaxes  /= scale
        self.kpoints/= scale
        if self.folded_structure!=None:
            self.folded_structure.rescale(scale)
        #end if
    #end def rescale


    def stretch(self,s1,s2,s3):
        if self.dim!=3:
            self.error('stretch is currently only implemented for 3 dimensions')
        #end if
        d = diag((s1,s2,s3))
        self.skew(d)
    #end def stretch

        
    def skew(self,skew):
        axinv  = inv(self.axes)
        axnew  = dot(self.axes,skew)
        kaxinv = inv(self.kaxes)
        kaxnew = dot(inv(skew),self.kaxes)
        self.pos     = dot(dot(self.pos,axinv),axnew)
        self.center  = dot(dot(self.center,axinv),axnew)
        self.kpoints = dot(dot(self.kpoints,kaxinv),kaxnew)
        self.axes  = axnew
        self.kaxes = kaxnew
        if self.folded_structure!=None:
            T = self.tmatrix
            fskew = dot(T,dot(skew,inv(T)))
            self.folded_structure.skew(fskew)
        #end if
    #end def skew
        
    
    def change_units(self,units):
        if units!=self.units:
            scale = convert(1,self.units,units)
            self.scale  *= scale
            self.axes   *= scale
            self.pos    *= scale
            self.center *= scale
            self.kaxes  /= scale
            self.kpoints/= scale
            self.units  = units
        #end if
        if self.folded_structure!=None:
            self.folded_structure.change_units(units)
        #end if
    #end def change_units
                              
        
    def cleave(self,c,v,remove=False,insert=True):
        c = array(c)
        v = array(v)
        self.cell_image(c)
        self.recenter()
        indices = []
        for i in range(len(self.pos)):
            if dot(pos[i,:]-c[:],v[:])>0:
                pos[i,:] = pos[i,:] + v[:]
                indices.append(i)
            #end if
        #end for
        if insert:
            dist_scale = self.rinscribe()
            components = 0
            for i in range(self.dim):
                axis = self.axes[i]
                a = axis/norm(axis)
                comp = abs(dot(a,v))
                if comp > dist_scale*1e-6:
                    components+=1
                    iaxis = i
                #end if
            #end for
            commensurate = components==1
            if not commensurate:
                self.error('cannot insert vacuum because cleave is incommensurate with the cell\n  cleave plane must be parallel to a cell face')
            #end if
            a = self.axes[i]
            self.axes[i] = (1+dot(v,v)/dot(v,a))*a
        #end if
        if remove:
            self.remove(indices)
        #end if
        self.remove_folded_structure()
    #end def cleave


    def translate(self,v):
        pos = self.pos
        for i in range(len(pos)):
            pos[i]+=v
        #end for
        self.center+=v
        if self.folded_structure!=None:
            self.folded_structure.translate(v)
        #end if
    #end def translate

                              
    def slide(self,v,recenter=True):
        pos = self.pos
        for i in range(len(pos)):
            pos[i]+=v
        #end for
        if recenter:
            self.recenter()
        #end if
        if self.folded_structure!=None:
            self.folded_structure.slide(v,recenter)
        #end if
    #end def slide


    def zero_corner(self):
        corner = self.center-self.axes.sum(0)/2
        self.translate(-corner)
    #end def zero_corner


    def locate_simple(self,pos):
        pos = array(pos)
        if pos.shape==(self.dim,):
            pos = [pos]
        #end if
        nn = nearest_neighbors(1,self.pos,pos)
        return nn.ravel()
    #end def

    
    def locate(self,identifiers,radii=None,negate=False):
        indices = None
        if isinstance(identifiers,Structure):
            cell = identifiers
            indices = cell.inside(self.pos)
        elif isinstance(identifiers,ndarray) and identifiers.dtype==bool:
            indices = arange(len(self.pos))[identifiers]
        elif isinstance(identifiers,int):
            indices = [identifiers]
        elif len(identifiers)>0 and isinstance(identifiers[0],int):
            indices = identifiers
        #end if
        if radii!=None or indices==None:
            if indices is None:
                pos = identifiers
            else:
                pos = self.pos[indices]
            #end if
            if isinstance(radii,float) or isinstance(radii,int):
                radii = len(pos)*[radii]
            elif radii!=None and len(radii)!=len(pos):
                self.error('lengths of input radii and positions do not match\n  len(radii)={0}\n  len(pos)={1}'.format(len(radii),len(pos)))
            #end if
            dtable = self.min_image_distances(pos)
            indices = []
            if radii is None:
                for i in range(len(pos)):
                    indices.append(dtable[i].argmin())
                #end for
            else:
                ipos = arange(len(self.pos))
                for i in range(len(pos)):
                    indices.extend(ipos[dtable[i]<radii[i]])
                #end for
            #end if
        #end if
        if negate:
            indices = list(set(range(len(self.pos)))-set(indices))
        #end if
        return indices
    #end def locate

    
    def freeze(self,identifiers,radii=None,negate=False,directions='xyz'):
        indices = self.locate(identifiers,radii,negate)
        if isinstance(directions,str):
            directions = len(indices)*[directions]
        #dnd if
        frozen = obj()
        i=-1
        for index in indices:
            i+=1
            frozen[index] = str(directions[i])
        #end for
        if len(frozen)>0:
            self.frozen = frozen
        #end if
    #end def freeze


    def carve(self,identifiers):
        indices = self.locate(identifiers)
        if isinstance(identifiers,Structure):
            sub = identifiers
            sub.elem = self.elem[indices].copy()
            sub.pos  = self.pos[indices].copy()
        else:
            sub = self.copy()
            sub.elem = self.elem[indices]
            sub.pos  = self.pos[indices]
        #end if
        sub.host_indices = array(indices)
        return sub
    #end def carve

        
    def remove(self,identifiers):
        indices = self.locate(identifiers)
        keep = list(set(range(len(self.pos)))-set(indices))
        erem = self.elem[indices]
        prem = self.pos[indices]
        self.elem = self.elem[keep]
        self.pos  = self.pos[keep]
        self.remove_folded_structure()
        return erem,prem
    #end def remove

    
    def replace(self,identifiers,elem=None,pos=None):
        indices = self.locate(identifiers)
        if isinstance(elem,Structure):
            cell = elem
            elem = cell.elem
            pos  = cell.pos
        elif elem==None:
            elem = self.elem
        #end if
        indices=array(indices)
        elem=array(elem)
        pos =array(pos)
        nrem = len(indices)
        nadd = len(pos)
        if nadd<nrem:
            ar = array(range(0,nadd))
            rr = array(range(nadd,nrem))
            self.elem[indices[ar]] = elem[:]
            self.pos[indices[ar]]  = pos[:]
            self.remove(indices[rr])
        elif nadd>nrem:
            ar = array(range(0,nrem))
            er = array(range(nrem,nadd))
            self.elem[indices[ar]] = elem[ar]
            self.pos[indices[ar]]  = pos[ar]
            ii = indices[ar[-1]]
            self.elem = array( list(self.elem[0:ii])+list(elem[er])+list(self.elem[ii:]) )
            self.pos = array( list(self.pos[0:ii])+list(pos[er])+list(self.pos[ii:]) )
        else:
            self.elem[indices] = elem[:]
            self.pos[indices]  = pos[:]
        #end if
        self.remove_folded_structure()
    #end def replace


    def replace_nearest(self,elem,pos=None):
        if isinstance(elem,Structure):
            cell = elem
            elem = cell.elem
            pos  = cell.pos
        #end if
        nn = nearest_neighbors(1,self.pos,pos)
        np = len(pos)
        nps= len(self.pos)
        d = empty((np,))
        ip = array(range(np))
        ips= nn.ravel()
        for i in ip:
            j = ips[i]
            d[i]=sqrt(((pos[i]-self.pos[j])**2).sum())
        #end for
        order = d.argsort()
        ip = ip[order]
        ips=ips[order]
        replacable = empty((nps,))
        replacable[:] = False
        replacable[ips]=True
        insert = []
        last_replaced=nps-1
        for n in range(np):
            i = ip[n]
            j = ips[n]
            if replacable[j]:
                self.pos[j] = pos[i]
                self.elem[j]=elem[i]
                replacable[j]=False
                last_replaced = j
            else:
                insert.append(i)
            #end if
        #end for
        insert=array(insert)
        ii = last_replaced
        if len(insert)>0:
            self.elem = array( list(self.elem[0:ii])+list(elem[insert])+list(self.elem[ii:]) )
            self.pos = array( list(self.pos[0:ii])+list(pos[insert])+list(self.pos[ii:]) )
        #end if
        self.remove_folded_structure()
    #end def replace_nearest

    
    def min_image_vectors(self,points,points2=None,axes=None):
        points = array(points)
        single = points.shape==(self.dim,)
        if single:
            points = [points]
        #end if
        if points2 is None:
            points2 = self.pos
        #end if
        npoints  = len(points)
        npoints2 = len(points2)
        vtable = empty((npoints,npoints2,self.dim))
        if axes is None:
            axes  = self.axes
        #end if
        axinv = inv(axes)
        i=-1
        for p in points:
            i+=1
            j=-1
            for pp in points2:
                j+=1
                u = dot(pp-p,axinv)
                vtable[i,j] = dot(u-floor(u+.5),axes)
            #end for
        #end for
        if single:
            vtable = vtable[0]
        #end if
        return vtable
    #end def min_image_vectors


    def min_image_distances(self,points,points2=None,axes=None):
        vtable = self.min_image_vectors(points,points2,axes)
        rdim = len(vtable.shape)-1
        return sqrt((vtable**2).sum(rdim))
    #end def min_image_distances

    
    def neighbor_table(self,points,points2=None,axes=None,distances=False):
        dtable = self.min_image_distances(points,points2,axes)
        ntable = empty(dtable.shape,dtype=int)
        for i in range(len(dtable)):
            ntable[i] = dtable[i].argsort()
        #end for
        if not distances:
            return ntable
        else:
            for i in range(len(dtable)):
                dtable[i] = dtable[i][ntable[i]]
            #end for
            return ntable,dtable
        #end if
    #end def neighbor_table


    def min_image_norms(self,points,norms):
        if isinstance(norms,int) or isinstance(norms,float):
            norms = [norms]
        #end if
        vtable = self.min_image_vectors(points)
        rdim = len(vtable.shape)-1
        nout = []
        for p in norms:
            nout.append( ((abs(vtable)**p).sum(rdim))**(1./p) )
        #end for
        if len(norms)==1:
            nout = nout[0]
        #end if
        return nout
    #end def min_image_norms


    def cell_image(self,p):
        if self.dim!=3:
            self.error('cell_image is currently only implemented for 3 dimensions')
        #end if
        pos = atleast_2d(p)
        c = empty((1,3))
        c[:] = self.center[:]
        axes = self.axes
        axinv = inv(axes)
        for i in range(len(pos)):
            u = dot(pos[i]-c,axinv)
            pos[i] = dot(u-floor(u+.5),axes)+c
        #end for
        if isinstance(p,ndarray):
            p[:] = pos[:]
        elif len(pos)==1 and len(p)==3:
            p[0] = pos[0,0]
            p[1] = pos[0,1]
            p[2] = pos[0,2]
        else:
            for i in range(len(p)):
                p[i][0] = pos[i,0]
                p[i][1] = pos[i,1]
                p[i][2] = pos[i,2]
            #end for
        #end if
    #end def cell_image


    def recenter(self,center=None):
        if center!=None:
            self.center=array(center)
        #end if
        pos = self.pos
        c = empty((1,self.dim))
        c[:] = self.center[:]
        axes = self.axes
        axinv = inv(axes)
        for i in range(len(pos)):
            u = dot(pos[i]-c,axinv)
            pos[i] = dot(u-floor(u+.5),axes)+c
        #end for
        self.recenter_k()
    #end def recenter

    
    def recenter_k(self,kpoints=None,kaxes=None,kcenter=None,remove_duplicates=False):
        use_self = kpoints==None
        if use_self:
            kpoints=self.kpoints
        #end if
        if kaxes==None:
            kaxes=self.kaxes
        #end if
        if len(kpoints)>0:
            axes = kaxes
            axinv = inv(axes)
            if kcenter is None:
                c = axes.sum(0)/2
            else:
                c = array(kcenter)
            #end if
            for i in range(len(kpoints)):
                u = dot(kpoints[i]-c,axinv)
                kpoints[i] = dot(u-floor(u+.5),axes)+c
            #end for
            if remove_duplicates:
                inside = self.inside(kpoints,axes,c)
                kpoints  = kpoints[inside]
                nkpoints = len(kpoints)
                unique = empty((nkpoints,),dtype=bool)
                unique[:] = True
                nn = nearest_neighbors(1,kpoints)
                if nkpoints>1:
                    nn.shape = nkpoints,
                    dist = self.distances(kpoints,kpoints[nn])
                    tol = 1e-8
                    duplicates = arange(nkpoints)[dist<tol]
                    for i in duplicates:
                        if unique[i]:
                            for j in duplicates:
                                if sqrt(((kpoints[i]-kpoints[j])**2).sum(1))<tol:
                                    unique[j] = False
                                #end if
                            #end for
                        #end if
                    #end for
                #end if
                kpoints = kpoints[unique]
            #end if
        #end if
        if use_self:
            self.kpoints = kpoints
        else:
            return kpoints   
        #end if
    #end def recenter_k


    def inside(self,pos,axes=None,center=None,tol=1e-8):
        if axes==None:
            axes=self.axes
        #end if
        if center==None:
            center=self.center
        #end if
        axes = array(axes)
        center = array(center)
        inside = []
        surface = []
        su = []
        axinv = inv(axes)
        for i in range(len(pos)):
            u = dot(pos[i]-center,axinv)
            umax = abs(u).max()
            if abs(umax-.5)<tol:
                surface.append(i)
                su.append(u)
            elif umax<.5:
                inside.append(i)
            #end if
        #end for
        npos,dim = pos.shape
        drange = range(dim)
        n = len(surface)
        i=0
        while i<n:
            j=i+1
            while j<n:
                du = abs(su[i]-su[j])
                match = False
                for d in drange:
                    match = match or abs(du[d]-1.)<tol
                #end for
                if match:
                    surface[j]=surface[-1]
                    surface.pop()
                    su[j]=su[-1]
                    su.pop()
                    n-=1
                else:
                    j+=1
                #end if
            #end while
            i+=1
        #end while
        inside+=surface
        return inside
    #end def inside


    def tile(self,*td,**kwargs):
        in_place = False
        if 'in_place' in kwargs:
            in_place = kwargs['in_place']
        #end if
        if self.dim!=3:
            self.error('tile is currently only implemented for 3 dimensions')
        #end if
        dim = self.dim
        if len(td)==1:
            if isinstance(td[0],int):
                tiling = dim*[td[0]]
            else:
                tiling = td[0]
            #end if
        else:
            tiling = td
        #end if
        tiling = array(tiling)
        t = array(tiling,dtype=int)
        if abs(tiling-t).sum()>1e-6:
            self.error('requested tiling is non-integer\n tiling requested: '+str(tiling))
        #end if

        matrix_tiling = t.shape == (dim,dim)
        if matrix_tiling:
            #find a tiling tuple from the tiling matrix
            # do this by shearing the tiling matrix (or equivalently the tiled cell)
            # until it is orthogonal (in the untiled cell axes)
            # this is just rearranging triangular tiles of space to reshape the cell
            # so that t1*t2*t3 = det(T) = det(A_tiled)/det(A_untiled)
            #this way the atoms in the (perhaps oddly shaped) supercell can be 
            # obtained from simple translations of the untiled cell positions
            T = t  #tiling matrix
            tilematrix = T.copy()
            del t
            Tnew = array(T,dtype=float) #sheared/orthogonal tiling matrix
            tbar = identity(dim) #basis for shearing
            dr = range(dim)
            other = [] # other[d] = dimensions other than d
            for d in dr: 
                other.append(set(dr)-set([d]))
            #end for
            #move each axis to be parallel to barred directions
            # these are volume preserving shears of the supercell
            # each shear keeps two cell face planes fixed while moving the others
            for d in dr:
                tb = tbar[d] 
                t  = T[d]
                d2,d3 = other[d]
                n = cross(Tnew[d2],Tnew[d3])  #vector normal to 2 cell faces
                tn = dot(n,t)*1./dot(n,tb)*tb #new axis vector
                Tnew[d] = tn
            #end for
            #the resulting tiling matrix should be diagonal and integer
            tr = diag(Tnew)
            t  = array(around(tr),dtype=int)
            nondiagonal = abs(Tnew-diag(tr)).sum()>1e-6
            noninteger  = abs(tr-t).sum()>1e-6
            if nondiagonal:
                self.error('could not find a diagonal tiling matrix for generating tiled atomic positions')
            #end if
            if noninteger:
                self.error('calculated diagonal tiling matrix is non-integer\n  tiled atomic positions cannot be determined')
            #end if
        else:
            tilematrix = diag(t)
        #end if

        ncells = t.prod()

        self.recenter()

        elem = array(ncells*list(self.elem))
        if ncells==1:
            pos    = array(self.pos)   
            axes   = array(self.axes)  
            center = array(self.center)
        else:
            pos,axes = tile_points(self.pos,t,self.axes)
            if matrix_tiling:
                axes = dot(self.axes,tilematrix)
            #end if
            center = axes.sum(0)/2
        #end if
        kaxes = dot(inv(tilematrix),self.kaxes)
        #kpoints = self.recenter_k(self.kpoints,kaxes,True)
        kpoints  = array(self.kpoints)
        kweights = array(self.kweights)

        ts = self.copy()
        ts.center  = center
        ts.elem    = elem
        ts.axes    = axes
        ts.pos     = pos
        ts.kaxes   = kaxes
        ts.kpoints = kpoints
        ts.kweights= kweights

        ts.recenter()
        ts.unique_kpoints()
        if self.folded_structure!=None:
            ts.tmatrix = dot(self.tmatrix,tilematrix)
            ts.folded_structure = self.folded_structure.copy()
        elif ncells>1:
            ts.tmatrix = tilematrix
            ts.folded_structure = self.copy()
        #end if

        if in_place:
            self.clear()
            self.transfer_from(ts)
            ts = self
        #end if

        return ts
    #end def tile


    def kfold(self,tmatrix,kpoints,kweights):
        if len(kpoints)!=len(kweights):
            self.error('kpoints and kweights must have the same length in kfold\n  kpoints length: {0}\n  kweights length: {1}'.format(len(kpoints),len(kweights)))
        #end if
        if not isinstance(tmatrix,ndarray):
            tmatrix = array(tmatrix)
        #end if
        dim = self.dim
        if tmatrix.shape==(dim,dim):
            tiling = array(around(diag(tmatrix)),dtype=int)
            tdiag = diag(tiling)
            if abs(tdiag-tmatrix).sum()>1e-6:
                self.error('kfold does not currently support tiling matrices with off-diagonal elements\n  tiling must be of the form (tx,ty,tz)\n  you provided: '+str(tmatrix))
            #end if
        elif len(tmatrix)==dim:
            tiling = array(around(tmatrix),dtype=int)
            if abs(tiling-tmatrix).sum()>1e-6:
                self.error('tiling must be integer')
            #end if
        elif isinstance(tmatrix,int):
            tiling = (tmatrix,tmatrix,tmatrix)
        else:
            self.error('invalid tiling matrix provided to kfold\n  tiling matrix must be integer diagonal matrix, vector, or scalar\n  you provided:'+str(tmatrix))
        #end if
        ncells = tiling.prod()
        kp,kaxnew = tile_points(kpoints,tiling,self.kaxes)
        kw = array(ncells*list(kweights),dtype=float)/ncells
        return kp,kw
    #end def kfold


    def fold(self,small,*requests):
        self.error('fold needs a developers attention to make it equivalent with tile')
        if self.dim!=3:
            self.error('fold is currently only implemented for 3 dimensions')
        #end if
        self.recenter_k()
        corners = []
        ndim = len(small.axes)
        imin = empty((ndim,),dtype=int)
        imax = empty((ndim,),dtype=int)
        imin[:] =  1000000
        imax[:] = -1000000
        axinv  = inv(self.kaxes)
        center = self.kaxes.sum(0)/2 
        c = empty((1,3))
        for k in -1,2:
            for j in -1,2:
                for i in -1,2:
                    c[:] = i,j,k
                    c = dot(c,small.kaxes)
                    u = dot(c-center,axinv)
                    for d in range(ndim):
                        imin[d] = min(int(floor(u[0,d])),imin[d])
                        imax[d] = max(int(ceil(u[0,d])),imax[d])
                    #end for
                #end for
            #end for
        #end for

        axes = small.kaxes
        axinv = inv(small.kaxes)

        center = small.kaxes.sum(0)/2
        nkpoints = len(self.kpoints)
        kindices = []
        kpoints  = []
        shift = empty((ndim,))
        kr = range(nkpoints)
        for k in range(imin[2],imax[2]+1):
            for j in range(imin[1],imax[1]+1):
                for i in range(imin[0],imax[0]+1):
                    for n in kr:
                        shift[:] = i,j,k
                        shift = dot(shift,self.kaxes)
                        kp = self.kpoints[n]+shift
                        u = dot(kp-center,axinv)
                        if abs(u).max()<.5+1e-10:
                            kindices.append(n)
                            kpoints.append(kp)
                        #end if
                    #end for
                #end for
            #end for
        #end for
        kindices = array(kindices)
        kpoints  = array(kpoints)
        inside = self.inside(kpoints,axes,center)
        kindices = kindices[inside]
        kpoints  = kpoints[inside]

        small.kpoints = kpoints
        small.recenter_k()
        kpoints = array(small.kpoints)
        if len(requests)>0:
            results = []
            for request in requests:
                if request=='kmap':
                    kmap = obj()
                    for k in self.kpoints:
                        kmap[tuple(k)] = []
                    #end for
                    for i in range(len(kpoints)):
                        kp = tuple(self.kpoints[kindices[i]])
                        kmap[kp].append(array(kpoints[i]))
                    #end for
                    for kl,ks in kmap.iteritems():
                        kmap[kl] = array(ks)
                    #end for
                    res = kmap
                elif request=='tilematrix':
                    res = self.tilematrix(small)
                else:
                    self.error(request+' is not a recognized input to fold')
                #end if
                results.append(res)
            #end if
            return results
        #end if
    #end def fold


    def tilematrix(self,small,tol=1e-6):
        tm = dot(inv(small.axes),self.axes)
        tilemat = array(around(tm),dtype=int)
        error = abs(tilemat-tm).sum()
        non_integer_elements = error > tol
        if non_integer_elements:
            self.error('large cell cannot be constructed as an integer tiling of the small cell\n  large cell axes:  \n'+str(self.axes)+'\n  small cell axes:  \n'+str(small.axes)+'\n  tiling matrix:  \n'+str(tm)+'\n  integerized tiling matrix:  \n'+str(tilemat)+'\n  error: '+str(error)+'\n  tolerance: '+str(tol))
        #end if
        return tilemat
    #end def tilematrix
            

    def add_kpoints(self,kpoints,kweights=None):
        if kweights is None:
            kweights = ones((len(kpoints),))
        #end if
        self.kpoints  = append(self.kpoints,kpoints,axis=0)
        self.kweights = append(self.kweights,kweights)
        if self.folded_structure!=None:
            kp,kw = self.kfold(self.tmatrix,kpoints,kweights)
            self.folded_structure.add_kpoints(kp,kw)
        #end if
    #end def add_kpoints


    def clear_kpoints(self):
        self.kpoints  = empty((0,self.dim))
        self.kweights = empty((0,))
        if self.folded_structure!=None:
            self.folded_structure.clear_kpoints()
        #end if
    #end def clear_kpoints


    def add_kmesh(self,kgrid,kshift=None):
        self.add_kpoints(kmesh(self.kaxes,kgrid,kshift))
    #end def add_kmesh

    
    def kpoints_unit(self):
        return dot(self.kpoints,inv(self.kaxes))
    #end def kpoints_unit


    def kpoints_reduced(self):
        return self.kpoints*self.scale/(2*pi)
    #end def kpoints_reduced


    def inversion_symmetrize_kpoints(self,tol=1e-10):
        kp    = self.kpoints
        kaxes = self.kaxes
        ntable,dtable = self.neighbor_table(kp,-kp,kaxes,distances=True)
        pairs = set()
        keep = empty((len(kp),),dtype=bool)
        keep[:] = True
        for i in range(len(dtable)):
            if keep[i] and dtable[i,0]<tol:
                j = ntable[i,0]
                if j!=i and keep[j]:
                    keep[j] = False
                    self.kweights[i] += self.kweights[j]
                #end if
            #end if
        #end for
        self.kpoints  = self.kpoints[keep]
        self.kweights = self.kweights[keep]
    #end def inversion_symmetrize_kpoints

        
    def unique_kpoints(self,tol=1e-10):
        kmap = obj()
        kp    = self.kpoints
        if len(kp)>0:
            kaxes = self.kaxes
            ntable,dtable = self.neighbor_table(kp,kp,kaxes,distances=True)
            npoints = len(kp)
            keep = empty((len(kp),),dtype=bool)
            keep[:] = True
            kmo = obj()
            for i in range(npoints):
                if keep[i]:
                    km = []
                    jn=0
                    while jn<npoints and dtable[i,jn]<tol:
                        j = ntable[i,jn]
                        km.append(j)
                        if j!=i and keep[j]:
                            keep[j] = False
                            self.kweights[i] += self.kweights[j]
                        #end if
                        jn+=1
                    #end while
                    kmo[i] = set(km)
                #end if
            #end for
            self.kpoints  = self.kpoints[keep]
            self.kweights = self.kweights[keep]
            j=0
            for i in range(len(keep)):
                if keep[i]:
                    kmap[j] = kmo[i]
                    j+=1
                #end if
            #end for
        #end if
        return kmap
    #end def unique_kpoints


    def kmap(self):
        kmap = None
        if self.folded_structure!=None:
            fs = self.folded_structure
            self.kpoints  = array(fs.kpoints)
            self.kweights = array(fs.kweights)
            kmap = self.unique_kpoints()
        #end if
        return kmap
    #end def kmap


    def pos_unit(self,pos=None):
        if pos is None:
            pos = self.pos
        #end if
        return dot(pos,inv(self.axes))
    #end def pos_unit


    def at_Gpoint(self):
        kpu = self.kpoints_unit()
        kg = array([0,0,0])
        return len(kpu)==1 and norm(kg-kpu[0])<1e-6
    #end def at_Gpoint


    def at_Lpoint(self):
        kpu = self.kpoints_unit()
        kg = array([.5,.5,.5])
        return len(kpu)==1 and norm(kg-kpu[0])<1e-6
    #end def at_Lpoint


    def at_real_kpoint(self):
        kpu = 2*self.kpoints_unit()
        return len(kpu)==1 and abs(kpu-around(kpu)).sum()<1e-6
    #end def at_real_kpoint


    def bonds(self,neighbors,vectors=False):
        if self.dim!=3:
            self.error('bonds is currently only implemented for 3 dimensions')
        #end if
        natoms,dim = self.pos.shape
        centers = empty((natoms,neighbors,dim))
        distances = empty((natoms,neighbors))
        vect      = empty((natoms,neighbors,dim))
        t = self.tile((3,3,3))
        t.recenter(self.center)
        nn = nearest_neighbors(neighbors+1,t.pos,self.pos)
        for i in range(natoms):
            ii = nn[i,0]
            n=0
            for jj in nn[i,1:]:
                p1 = t.pos[ii]
                p2 = t.pos[jj]
                centers[i,n,:] = (p1+p2)/2
                distances[i,n]= sqrt(((p1-p2)**2).sum())
                vect[i,n,:] = p2-p1
                n+=1
            #end for
        #end for
        sn = self.copy()
        nnr = nn[:,1:].ravel()
        sn.elem = t.elem[nnr]
        sn.pos  = t.pos[nnr]
        sn.recenter()
        indices = self.locate(sn.pos)
        indices = indices.reshape(natoms,neighbors)
        if not vectors:
            return indices,centers,distances
        else:
            return indices,centers,distances,vect
        #end if
    #end def bonds

        
    def displacement(self,reference,map=False):
        if self.dim!=3:
            self.error('displacement is currently only implemented for 3 dimensions')
        #end if
        ref = reference.tile((3,3,3))
        ref.recenter(reference.center)
        rmap = array(3**3*range(len(reference.pos)),dtype=int)
        nn = nearest_neighbors(1,ref.pos,self.pos).ravel()
        displacement = self.pos - ref.pos[nn]
        if not map:
            return displacement
        else:
            return displacement,rmap[nn]
        #end if
    #end def displacement


    def scalar_displacement(self,reference):
        return sqrt((self.displacement(reference)**2).sum(1))
    #end def scalar_displacement

    
    def distortion(self,reference,neighbors):
        if self.dim!=3:
            self.error('distortion is currently only implemented for 3 dimensions')
        #end if
        if reference.volume()/self.volume() < 1.1:
            ref = reference.tile((3,3,3))
            ref.recenter(reference.center)
        else:
            ref = reference
        #end if
        rbi,rbc,rbl,rbv =  ref.bonds(neighbors,vectors=True)
        sbi,sbc,sbl,sbv = self.bonds(neighbors,vectors=True)
        nn = nearest_neighbors(1,reference.pos,self.pos).ravel()
        distortion = empty(sbv.shape)
        magnitude  = empty((len(self.pos),))
        for i in range(len(self.pos)):
            ir = nn[i]
            bonds  = sbv[i]
            rbonds = rbv[ir]
            ib  = empty((neighbors,),dtype=int)
            ibr = empty((neighbors,),dtype=int)
            r  = range(neighbors)
            rr = range(neighbors)
            for n in range(neighbors):
                mindist = 1e99
                ibmin  = -1
                ibrmin = -1
                for nb in r:
                    for nbr in rr:
                        d = norm(bonds[nb]-rbonds[nbr])
                        if d<mindist:
                            mindist=d
                            ibmin=nb
                            ibrmin=nbr
                        #end if
                    #end for
                #end for
                ib[n]=ibmin
                ibr[n]=ibrmin
                r.remove(ibmin)
                rr.remove(ibrmin)
                #end for
            #end for
            d = bonds[ib]-rbonds[ibr]
            distortion[i] = d
            magnitude[i] = (sqrt((d**2).sum(axis=1))).sum()
        #end for
        return distortion,magnitude
    #end def distortion


    def bond_compression(self,reference,neighbors):
        ref = reference
        rbi,rbc,rbl =  ref.bonds(neighbors)
        sbi,sbc,sbl = self.bonds(neighbors)
        bondlen = rbl.mean()
        return abs(1.-sbl/bondlen).max(axis=1)
    #end def bond_compression


    def shell(self,cell,neighbors,direction='in'):
        if self.dim!=3:
            self.error('shell is currently only implemented for 3 dimensions')
        #end if
        dd = {'in':equate,'out':negate}
        dir = dd[direction]
        natoms,dim=self.pos.shape
        ncells=3**3
        ntile = ncells*natoms
        pos = empty((ntile,dim))
        ind = empty((ntile,),dtype=int)
        oind = range(natoms)
        for nt in range(ncells):
            n=nt*natoms
            ind[n:n+natoms]=oind[:]
            pos[n:n+natoms]=self.pos[:]
        #end for
        nt=0
        for k in -1,0,1:
            for j in -1,0,1:
                for i in -1,0,1:
                    iv = array([[i,j,k]])
                    v = dot(iv,self.axes)
                    for d in range(dim):
                        ns = nt*natoms
                        ne = ns+natoms
                        pos[ns:ne,d] += v[0,d]
                    #end for
                    nt+=1
                #end for
            #end for
        #end for
        
        inside = empty(ntile,)
        inside[:]=False
        ins = cell.inside(pos)
        inside[ins]=True

        iishell = set()
        nn = nearest_neighbors(neighbors,pos)
        for ii in range(len(nn)):
            for jj in nn[ii]:
                in1 = inside[ii]
                in2 = inside[jj]
                if dir(in1 and not in2):
                    iishell.add(ii)
                #end if
                if dir(in2 and not in1):
                    iishell.add(jj)
                #end if
            #end if
        #end if
        ishell = ind[list(iishell)]
        return ishell
    #end def shell


    def madelung(self,axes=None,tol=1e-10):
        if self.dim!=3:
            self.error('madelung is currently only implemented for 3 dimensions')
        #end if
        if axes==None:
            a = self.axes.T
        else:
            a = axes.T
        #end if
        volume = abs(det(a))
        b = 2*pi*inv(a)
        rconv = 8*(3.*volume/(4*pi))**(1./3)
        kconv = 2*pi/rconv
        gconst = -1./(4*kconv**2)
        vmc = -pi/(kconv**2*volume)-2*kconv/sqrt(pi)
        
        nshells = 20
        vshell = [0.]
        p = Sobj()
        m = Sobj()
        for n in range(1,nshells+1):
            i = mgrid[-n:n+1,-n:n+1,-n:n+1]
            i = i.reshape(3,(2*n+1)**3)
            R = sqrt((dot(a,i)**2).sum(0))
            G2 = (dot(b,i)**2).sum(0)
            
            izero = n + n*(2*n+1) + n*(2*n+1)**2

            p.R  = R[0:izero]
            p.G2 = G2[0:izero]
            m.R  = R[izero+1:]
            m.G2  = G2[izero+1:]
            domains = [p,m]
            vshell.append(0.)
            for d in domains:
                vshell[n] += (erfc(kconv*d.R)/d.R).sum() + 4*pi/volume*(exp(gconst*d.G2)/d.G2).sum()
            #end for
            if abs(vshell[n]-vshell[n-1])<tol:
                break
            #end if
        #end for
        vm = vmc + vshell[-1]

        if axes==None:
            self.Vmadelung = vm
        #end if
        return vm
    #end def madelung


    def read_xyz(self,filepath):
        elem = []
        pos  = []
        if os.path.exists(filepath):
            lines = open(filepath,'r').read().splitlines()
        else:
            lines = filepath.splitlines()
        #end if
        ntot = 1000000
        natoms = 0
        for l in lines:
            ls = l.strip()
            if ls.isdigit():
                ntot = int(ls)
            #end if
            tokens = ls.split()
            if len(tokens)==4:
                elem.append(tokens[0])
                pos.append(array(tokens[1:],float))
                natoms+=1
                if natoms==ntot:
                    break
                #end if
            #end if
        #end for
        self.elem  = array(elem)
        self.pos   = array(pos)
        self.units = 'A'
    #end def read_xyz


    def write_xyz(self,filepath=None,header=True,units='A'):
        if self.dim!=3:
            self.error('write_xyz is currently only implemented for 3 dimensions')
        #end if
        s = self.copy()
        s.change_units(units)
        c=''
        if header:
            c += str(len(s.elem))+'\n\n'
        #end if
        for i in range(len(s.elem)):
            e = s.elem[i]
            p = s.pos[i]
            #c+='{0:2}  {1:12.6e} {2:12.6e} {3:12.6e}\n'.format(e,p[0],p[1],p[2])
            c+=' {0:2} {1:12.8f} {2:12.8f} {3:12.8f}\n'.format(e,p[0],p[1],p[2])
        #end for
        if filepath!=None:
            open(filepath,'w').write(c)
        else:
            return c
        #end if
    #end def write_xyz


    def plot2d_ax(self,ix,iy,*args,**kwargs):
        if self.dim!=3:
            self.error('plot2d_ax is currently only implemented for 3 dimensions')
        #end if
        iz = list(set([0,1,2])-set([ix,iy]))[0]
        ax = self.axes.copy()
        a  = self.axes[iz]
        dc = self.center-ax.sum(0)/2
        pp = array([0*a,ax[ix],ax[ix]+ax[iy],ax[iy],0*a])
        for i in range(len(pp)):
            pp[i]+=dc
            pp[i]-=dot(a,pp[i])/dot(a,a)*a
        #end for
        plot(pp[:,ix],pp[:,iy],*args,**kwargs)
    #end def plot2d_ax


    def plot2d_pos(self,ix,iy,*args,**kwargs):
        if self.dim!=3:
            self.error('plot2d_pos is currently only implemented for 3 dimensions')
        #end if
        iz = list(set([0,1,2])-set([ix,iy]))[0]
        pp = self.pos.copy()
        a = self.axes[iz]
        for i in range(len(pp)):
            pp[i] -= dot(a,pp[i])/dot(a,a)*a
        #end for
        plot(pp[:,ix],pp[:,iy],*args,**kwargs)
    #end def plot2d


    def plot2d(self,pos_style='b.',ax_style='k-'):
        if self.dim!=3:
            self.error('plot2d is currently only implemented for 3 dimensions')
        #end if
        subplot(1,3,1)
        self.plot2d_ax(0,1,ax_style,lw=2)
        self.plot2d_pos(0,1,pos_style)
        title('a1,a2')
        subplot(1,3,2)
        self.plot2d_ax(1,2,ax_style,lw=2)
        self.plot2d_pos(1,2,pos_style)
        title('a2,a3')
        subplot(1,3,3)
        self.plot2d_ax(2,0,ax_style,lw=2)
        self.plot2d_pos(2,0,pos_style)
        title('a3,a1')
    #end def plot2d

    def show(self,viewer='vmd',filepath='/tmp/tmp.xyz'):
        if self.dim!=3:
            self.error('show is currently only implemented for 3 dimensions')
        #end if
        self.write_xyz(filepath)
        os.system(viewer+' '+filepath)
    #end def show
#end class Structure



class DefectStructure(Structure):
    def __init__(self,*args,**kwargs):
        if len(args)>0 and isinstance(args[0],Structure):
            self.transfer_from(args[0],copy=True)
        else:
            Structure.__init__(self,*args,**kwargs)
        #end if
    #end def __init__


    def defect_from_bond_compression(self,compression_cutoff,bond_eq,neighbors):
        bind,bcent,blens = self.bonds(neighbors)
        ind = bind[ abs(blens/bond_eq - 1.) > compression_cutoff ]
        idefect = array(list(set(ind.ravel())))
        defect = self.carve(idefect)
        return defect
    #end def defect_from_bond_compression

    
    def defect_from_displacement(self,displacement_cutoff,reference):
        displacement = self.scalar_displacement(reference)
        idefect = displacement > displacement_cutoff
        defect = self.carve(idefect)
        return defect
    #end def defect_from_displacement


    def compare(self,dist_cutoff,d1,d2=None):
        if d2==None:
            d2 = d1
            d1 = self
        #end if
        res = Sobj()
        natoms1 = len(d1.pos)
        natoms2 = len(d2.pos)
        if natoms1<natoms2:
            dsmall,dlarge = d1,d2
        else:
            dsmall,dlarge = d2,d1
        #end if
        nn = nearest_neighbors(1,dlarge,dsmall)
        dist = dsmall.distances(dlarge[nn.ravel()])
        dmatch = dist<dist_cutoff
        ismall = array(range(len(dsmall.pos)))
        ismall = ismall[dmatch]
        ilarge = nn[ismall]
        if natoms1<natoms2:
            i1,i2 = ismall,ilarge
        else:
            i2,i1 = ismall,ilarge
        #end if
        natoms_match = dmatch.sum()
        res.all_match = natoms1==natoms2 and natoms1==natoms_match
        res.natoms_match = natoms_match
        res.imatch1 = i1
        res.imatch2 = i2
        return res
    #end def compare
#end class DefectStructure



class Crystal(Structure):
    lattice_constants = obj(
        triclinic    = ['a','b','c','alpha','beta','gamma'],
        monoclinic   = ['a','b','c','beta'],
        orthorhombic = ['a','b','c'],
        tetragonal   = ['a','c'],
        hexagonal    = ['a','c'],
        cubic        = ['a'],
        rhombohedral = ['a','alpha']
        )

    lattices = list(lattice_constants.keys())

    centering_types = obj(
        primitive             = 'P',
        base_centered         = ('A','B','C'),
        face_centered         = 'F',
        body_centered         = 'I',
        rhombohedral_centered = 'R'        
        )

    lattice_centerings = obj(
        triclinic = ['P'],
        monoclinic = ['P','A','B','C'],
        orthorhombic = ['P','C','I','F'],
        tetragonal   = ['P','I'],
        hexagonal    = ['P','R'],
        cubic        = ['P','I','F'],
        rhombohedral = ['P']
        )

    centerings = obj(
        P = [],
        A = [[0,.5,.5]],
        B = [[.5,0,.5]],
        C = [[.5,.5,0]],
        F = [[0,.5,.5],[.5,0,.5],[.5,.5,0]],
        I = [[.5,.5,.5]],
        R = [[2./3, 1./3, 1./3],[1./3, 2./3, 2./3]]
        )

    cell_types = set(['primitive','conventional'])

    cell_aliases = obj(
        prim = 'primitive',
        conv = 'conventional'
        )
    cell_classes = obj(
        sc  = 'cubic',
        bcc = 'cubic',
        fcc = 'cubic',
        hex = 'hexagonal'
        )
    for lattice in lattices:
        cell_classes[lattice]=lattice
    #end for

    
    #helpful websites for structures
    #  wikipedia.org
    #  webelements.com
    #  webmineral.com
    #  springermaterials.com


    known_crystals = {
        ('diamond','fcc'):obj(
            lattice   = 'cubic',
            cell      = 'primitive',
            centering = 'F',
            constants = 3.57,
            units     = 'A',
            atoms     = 'C',
            basis     = [[0,0,0],[.25,.25,.25]]
            ),
        ('diamond','sc'):obj(
            lattice   = 'cubic',
            cell      = 'conventional',
            centering = 'F',
            constants = 3.57,
            units     = 'A',
            atoms     = 'C',
            basis     = [[0,0,0],[.25,.25,.25]]
            ),
        ('diamond','prim'):obj(
            lattice   = 'cubic',
            cell      = 'primitive',
            centering = 'F',
            constants = 3.57,
            units     = 'A',
            atoms     = 'C',
            basis     = [[0,0,0],[.25,.25,.25]]
            ),
        ('diamond','conv'):obj(
            lattice   = 'cubic',
            cell      = 'conventional',
            centering = 'F',
            constants = 3.57,
            units     = 'A',
            atoms     = 'C',
            basis     = [[0,0,0],[.25,.25,.25]]
            ),
        ('wurtzite','prim'):obj(
            lattice   = 'hexagonal',
            cell      = 'primitive',
            centering = 'P',
            constants = (3.35,5.22),
            units     = 'A',
            #atoms     = ('Zn','O'),
            #basis     = [[1./3, 2./3, 3./8],[1./3, 2./3, 0]]
            atoms     = ('Zn','O','Zn','O'),
            basis     = [[0,0,5./8],[0,0,0],[2./3,1./3,1./8],[2./3,1./3,1./2]]
            ),
        ('ZnO','prim'):obj(
            lattice   = 'wurtzite',
            cell      = 'prim',
            constants = (3.35,5.22),
            units     = 'A',
            atoms     = ('Zn','O','Zn','O')
            ),
        ('NaCl','prim'):obj(
            lattice   = 'cubic',
            cell      = 'primitive',
            centering = 'F',
            constants = 5.64,
            units     = 'A',
            atoms     = ('Na','Cl'),
            basis     = [[0,0,0],[.5,0,0]],
            basis_vectors = 'conventional'
            ),
        ('copper','prim'):obj(
            lattice   = 'cubic',
            cell      = 'primitive',
            centering = 'F',
            constants = 3.615,
            units     = 'A',
            atoms     = 'Cu'
            ),
        ('calcium','prim'):obj(
            lattice   = 'cubic',
            cell      = 'primitive',
            centering = 'F',
            constants = 5.588,
            units     = 'A',
            atoms     = 'Ca'
            ),
        # http://www.webelements.com/oxygen/crystal_structure.html
        #   Phys Rev 160 694
        ('oxygen','prim'):obj(
            lattice   = 'monoclinic',
            cell      = 'primitive',
            centering = 'C',
            constants = (5.403,3.429,5.086,132.53),
            units     = 'A',
            angular_units = 'degrees',
            atoms     = ('O','O'),
            basis     = [[0,0,1.15/2],[0,0,-1.15/2]],
            basis_vectors = identity(3)
            ),
        # http://en.wikipedia.org/wiki/Calcium_oxide
        # http://www.springermaterials.com/docs/info/10681719_224.html
        ('CaO','prim'):obj(
            lattice   = 'NaCl',
            cell      = 'prim',
            constants = 4.81,
            atoms     = ('Ca','O')
            ),
        ('CaO','conv'):obj(
            lattice   = 'NaCl',
            cell      = 'conv',
            constants = 4.81,
            atoms     = ('Ca','O')
            ),
        # http://en.wikipedia.org/wiki/Copper%28II%29_oxide
        #   http://iopscience.iop.org/0953-8984/3/28/001/
        # http://www.webelements.com/compounds/copper/copper_oxide.html
        # http://www.webmineral.com/data/Tenorite.shtml
        ('CuO','prim'):obj(
            lattice   = 'monoclinic',
            cell      = 'primitive',
            centering = 'C',
            constants = (4.683,3.422,5.128,99.54),
            units     = 'A',
            angular_units = 'degrees',
            atoms     = ('Cu','O','Cu','O'),
            basis     = [[.25,.25,0],[0,.418,.25],
                         [.25,.75,.5],[.5,.5-.418,.75]],
            basis_vectors = 'conventional'
            ),
        ('Ca2CuO3','prim'):obj(# kateryna foyevtsova
            lattice   = 'orthorhombic',
            cell      = 'primitive',
            centering = 'I',
            constants = (3.77,3.25,12.23),
            units     = 'A',
            atoms     = ('Cu','O','O','O','Ca','Ca'),
            basis     = [[   0,   0,   0 ],
                         [ .50,   0,   0 ],
                         [   0,   0, .16026165],
                         [   0,   0, .83973835],
                         [   0,   0, .35077678],
                         [   0,   0, .64922322]],
            basis_vectors = 'conventional'
            ),
        ('La2CuO4','prim'):obj( #tetragonal structure
            lattice   = 'tetragonal',
            cell      = 'primitive',
            centering = 'I',
            constants = (3.809,13.169),
            units     = 'A',
            atoms     = ('Cu','O','O','O','O','La','La'),
            basis     = [[  0,    0,    0],
                         [ .5,    0,    0],
                         [  0,   .5,    0],
                         [  0,    0,  .182],
                         [  0,    0, -.182],
                         [  0,    0,  .362],
                         [  0,    0, -.362]]
            ),
        ('CuO2_plane','prim'):obj( 
            lattice   = 'tetragonal',
            cell      = 'primitive',
            centering = 'P',
            constants = (3.809,13.169),
            units     = 'A',
            atoms     = ('Cu','O','O'),
            basis     = [[  0,    0,    0],
                         [ .5,    0,    0],
                         [  0,   .5,    0]]
            ),
        ('graphite_aa','hex'):obj(
            axes      = [[1./2,-sqrt(3.)/2,0],[1./2,sqrt(3.)/2,0],[0,0,1]],
            constants = (2.462,3.525),
            units     = 'A',
            atoms     = ('C','C'),
            basis     = [[0,0,0],[2./3,1./3,0]]
            ),
        ('graphite_ab','hex'):obj(
            axes      = [[1./2,-sqrt(3.)/2,0],[1./2,sqrt(3.)/2,0],[0,0,1]],
            constants = (2.462,3.525),
            units     = 'A',
            cscale    = (1,2),
            atoms     = ('C','C','C','C'),
            basis     = [[0,0,0],[2./3,1./3,0],[0,0,1./2],[1./3,2./3,1./2]]
            )        
        }

    kc_keys = list(known_crystals.keys())
    for (name,cell) in kc_keys:
        desc = known_crystals[name,cell]
        if cell=='prim' and not (name,'conv') in known_crystals:
            cdesc = desc.copy()
            if cdesc.cell=='primitive':
                cdesc.cell = 'conventional'
                known_crystals[name,'conv'] = cdesc
            elif cdesc.cell=='prim':
                cdesc.cell = 'conv'
                known_crystals[name,'conv'] = cdesc
            #end if
        #end if
    #end if
    del kc_keys


    def __init__(self,lattice=None,cell=None,centering=None,constants=None,
                 atoms=None,basis=None,basis_vectors=None,tiling=None,cscale=None,
                 axes=None,units=None,angular_units='degrees',kpoints=None,
                 kgrid=None,kshift=(0,0,0),permute=None):
        if lattice is None and cell is None and atoms is None and units is None:
            return
        #end if

        gi = obj(
            lattice       = lattice      ,  
            cell          = cell         ,
            centering     = centering    ,
            constants     = constants    ,   
            atoms         = atoms        ,
            basis         = basis        ,
            basis_vectors = basis_vectors,
            tiling        = tiling       ,
            cscale        = cscale       ,
            axes          = axes         ,
            units         = units        ,
            angular_units = angular_units,
            kpoints       = kpoints      ,
            kgrid         = kgrid        ,
            kshift        = kshift       ,
            permute       = permute
            )
        generation_info = gi.copy()

        lattice_in = lattice
        if isinstance(lattice,str):
            lattice=lattice.lower()
        #end if
        if isinstance(cell,str):
            cell=cell.lower()
        #end if

        known_crystal = False
        if (lattice_in,cell) in self.known_crystals:
            known_crystal = True
            lattice_info = self.known_crystals[lattice_in,cell].copy()
        elif (lattice,cell) in self.known_crystals:
            known_crystal = True
            lattice_info = self.known_crystals[lattice,cell].copy()
        #end if
        
        if known_crystal:
            while 'lattice' in lattice_info and 'cell' in lattice_info and (lattice_info.lattice,lattice_info.cell) in self.known_crystals:
                li_old = lattice_info
                lattice_info = self.known_crystals[li_old.lattice,li_old.cell].copy()
                del li_old.lattice
                del li_old.cell
                lattice_info.transfer_from(li_old,copy=False)
            #end while
            if 'cell' in lattice_info:
                cell = lattice_info.cell
            elif cell in self.cell_aliases:
                cell = self.cell_aliases[cell]
            elif cell in self.cell_classes:
                lattice = self.cell_classes[cell]
            else:
                self.error('cell shape '+cell+' is not recognized\n  the variable cell_classes or cell_aliases must be updated to include '+cell)
            #end if
            if 'lattice' in lattice_info:
                lattice = lattice_info.lattice
            #end if
            if 'angular_units' in lattice_info:
                angular_units = lattice_info.angular_units
            #end if
            inputs = obj(
                centering     = centering,
                constants     = constants,
                atoms         = atoms,
                basis         = basis,
                basis_vectors = basis_vectors,
                tiling        = tiling,
                cscale        = cscale,
                axes          = axes,
                units         = units
                )
            for var,val in inputs.iteritems():
                if val is None and var in lattice_info:
                    inputs[var] = lattice_info[var]
                #end if
            #end for
            centering,constants,atoms,basis,basis_vectors,tiling,cscale,axes,units=inputs.list('centering','constants','atoms','basis','basis_vectors','tiling','cscale','axes','units')
        #end if

        if constants is None:
            self.error('the variable constants must be provided')
        #end if
        if atoms is None:
            self.error('the variable atoms must be provided')
        #end if

        if lattice not in self.lattices:
            self.error('lattice type '+str(lattice)+' is not recognized\n  valid lattice types are: '+str(list(self.lattices)))
        #end if
        if cell=='conventional':
            if centering is None:
                self.error('centering must be provided for a conventional cell\n  options for a '+lattice+' lattice are: '+str(self.lattice_types[lattice]))
            elif centering not in self.centerings:
                self.error('centering type '+str(centering)+' is not recognized\n  options for a '+lattice+' lattice are: '+str(self.lattice_types[lattice]))
            #end if
        #end if
        if isinstance(constants,int) or isinstance(constants,float):
            constants=[constants]
        #end if
        if len(constants)!=len(self.lattice_constants[lattice]):
            self.error('the '+lattice+' lattice depends on the constants '+str(self.lattice_constants[lattice])+'\n you provided '+str(len(constants))+': '+str(constants))
        #end if
        if isinstance(atoms,str):
            if basis!=None:
                atoms = len(basis)*[atoms]
            else:
                atoms=[atoms]
            #end if
        #end if
        if basis is None:
            if len(atoms)==1:
                basis = [(0,0,0)]
            else:
                self.error('must provide as many basis coordinates as basis atoms\n  atoms provided: '+str(atoms)+'\n  basis provided: '+str(basis))
            #end if
        #end if
        if basis_vectors!=None and not isinstance(basis_vectors,str) and len(basis_vectors)!=3:
            self.error('3 basis vectors must be given, you provided '+str(len(basis))+':\n  '+str(basis_vectors))
        #end if

        if tiling is None:
            tiling = (1,1,1)
        #end if
        if cscale is None:
            cscale = len(constants)*[1]
        #end if
        if len(cscale)!=len(constants):
            self.error('cscale and constants must be the same length')
        #end if
        basis  = array(basis)
        tiling = array(tiling,dtype=int)
        cscale = array(cscale)
        constants = cscale*array(constants)

        a,b,c,alpha,beta,gamma = None,None,None,None,None,None
        if angular_units=='radians':
            pi_1o2 = pi/2
            pi_2o3 = 2*pi/3
        elif angular_units=='degrees':
            pi_1o2 = 90.
            pi_2o3 = 120.
        else:
            self.error('angular units must be radians or degrees\n  you provided '+str(angular_units))
        #end if
        if lattice=='triclinic':
            a,b,c,alpha,beta,gamma = constants
        elif lattice=='monoclinic':
            a,b,c,beta = constants
            alpha = gamma = pi_1o2
        elif lattice=='orthorhombic':
            a,b,c = constants
            alpha=beta=gamma=pi_1o2
        elif lattice=='tetragonal':
            a,c = constants
            b=a
            alpha=beta=gamma=pi_1o2
        elif lattice=='hexagonal':
            a,c = constants
            b=a
            alpha=beta=pi_1o2
            gamma=pi_2o3
        elif lattice=='cubic':
            a=constants[0]
            b=c=a
            alpha=beta=gamma=pi_1o2
        elif lattice=='rhombohedral':
            a,alpha = constants
            b=c=a
            beta=gamma=alpha
        #end if
        if angular_units=='degrees':
            alpha *= pi/180
            beta  *= pi/180
            gamma *= pi/180
        #end if

        points = [[0,0,0]]
        if axes is None:
            if cell not in self.cell_types:
                self.error('cell must be primitive or conventional\n  You provided: '+str(cell))
            #end if
            if cell=='primitive' and centering=='P':
                cell='conventional'
            #end if
            #get the conventional axes
            a1c = array([a,0,0])
            a2c = array([b*cos(gamma),b*sin(gamma),0])
            a3c = array([c*cos(beta),c*cos(alpha)*sin(beta),c*sin(alpha)*sin(beta)])
            axes_conv = array([a1c,a2c,a3c]).copy()
            #get the primitive axes
            if centering=='P':
                a1 = a1c
                a2 = a2c
                a3 = a3c
            elif centering=='A':
                a1 = a1c
                a2 = (a2c+a3c)/2
                a3 = (-a2c+a3c)/2
            elif centering=='B':
                a1 = (a1c+a3c)/2
                a2 = a2c
                a3 = (-a1c+a3c)/2
            elif centering=='C':
                a1 = (a1c-a2c)/2
                a2 = (a1c+a2c)/2
                a3 = a3c
            elif centering=='I':
                a1=[ a/2, b/2,-c/2]
                a2=[-a/2, b/2, c/2]
                a3=[ a/2,-b/2, c/2]
            elif centering=='F':
                a1=[a/2, b/2,   0]
                a2=[  0, b/2, c/2]
                a3=[a/2,   0, c/2]
            elif centering=='R':
                a1=[   a,              0,   0]
                a2=[ a/2,   a*sqrt(3.)/2,   0]
                a3=[-a/6, a/(2*sqrt(3.)), c/3]
            else:
                self.error('the variable centering must be specified\n  valid options are: P,A,B,C,I,F,R')
            #end if
            axes_prim = array([a1,a2,a3])
            if cell=='primitive':
                axes = axes_prim
            elif cell=='conventional':            
                axes = axes_conv
                points.extend(self.centerings[centering])
            #end if            
        elif known_crystal:
            axes = dot(diag([a,b,c]),array(axes))
        #end if
        points = array(points,dtype=float)

        elem = []
        pos  = []
        if basis_vectors is None:
            basis_vectors = axes
        elif basis_vectors=='primitive':
            basis_vectors = axes_prim
        elif basis_vectors=='conventional':
            basis_vectors = axes_conv
        #end if
        nbasis = len(atoms)
        for point in points:
            for i in range(nbasis):
                atom   = atoms[i]
                bpoint = basis[i]
                p = dot(point,axes) + dot(bpoint,basis_vectors)
                elem.append(atom)
                pos.append(p)
            #end for
        #end for
        pos = array(pos)

        ao,eo,po = axes,elem,pos

        #ncells = tiling.prod()
        #if ncells>1:
        #    elem = array(ncells*elem)
        #    pos,axes = tile_points(pos,tiling,axes)
        ##end if

        self.set(
            constants = array([a,b,c]),
            angles    = array([alpha,beta,gamma]),
            generation_info = generation_info
            )

        Structure.__init__(
            self,
            axes    = axes,
            scale   = a,
            elem    = elem,
            pos     = pos,
            center  = axes.sum(0)/2,
            units   = units,
            tiling  = tiling,
            kpoints = kpoints,
            kgrid   = kgrid,
            kshift  = kshift,
            permute = permute,
            rescale = False)
    #end def __init__
#end class Crystal



def generate_cell(shape,tiling=None,scale=1.,units=None,struct_type=Structure):
    if tiling is None:
        tiling = (1,1,1)
    #end if
    axes = Sobj()
    axes.sc  =  1.*array([[ 1,0,0],[0, 1,0],[0,0, 1]])
    axes.bcc = .5*array([[-1,1,1],[1,-1,1],[1,1,-1]])
    axes.fcc = .5*array([[ 1,1,0],[1, 0,1],[0,1, 1]])
    ax     = dot(diag(tiling),axes[shape])
    center = ax.sum(0)/2
    c = Structure(axes=ax,scale=scale,center=center,units=units)
    if struct_type!=Structure:
        c=c.upcast(struct_type)
    #end if
    return c
#end def generate_cell



def generate_structure(type='crystal',*args,**kwargs):
    if type=='crystal':
        return generate_crystal_structure(*args,**kwargs)
    elif type=='defect':
        return generate_defect_structure(*args,**kwargs)
    elif type=='atom':
        return generate_atom_structure(*args,**kwargs)
    else:
        Structure.class_error(str(type)+' is not a valid structure type\n  options are crystal or defect')
    #end if
#end def generate_structure




def generate_atom_structure(atom=None,units='B',struct_type=Structure):
    return Structure(elem=[atom],pos=[[0,0,0]],units=units)
#end def generate_atom_structure



def generate_crystal_structure(lattice=None,cell=None,centering=None,
                               constants=None,atoms=None,basis=None,
                               basis_vectors=None,tiling=None,cscale=None,
                               axes=None,units=None,angular_units='degrees',
                               kpoints=None,kgrid=None,kshift=(0,0,0),permute=None,
                               structure=None,shape=None,element=None,scale=None, #legacy inputs
                               struct_type=Crystal):    

    if structure!=None:
        lattice = structure
    #end if
    if shape!=None:
        cell = shape
    #end if
    if element!=None:
        atoms = element
    #end if
    if scale!=None:
        constants = scale
    #end if

    s=Crystal(
        lattice       = lattice      ,  
        cell          = cell         ,
        centering     = centering    ,
        constants     = constants    ,   
        atoms         = atoms        ,
        basis         = basis        ,
        basis_vectors = basis_vectors,
        tiling        = tiling       ,
        cscale        = cscale       ,
        axes          = axes         ,
        units         = units        ,
        angular_units = angular_units,
        kpoints       = kpoints      ,
        kgrid         = kgrid        ,
        kshift        = kshift       ,
        permute       = permute
        )

    if struct_type!=Crystal:
        s=s.upcast(struct_type)
    #end if

    return s
#end def generate_crystal_structure



defects = obj(
    diamond = obj(
        H = obj(
            pristine = [[0,0,0]],
            defect   = [[0,0,0],[.625,.375,.375]]
            ),
        T = obj(
            pristine = [[0,0,0]],
            defect   = [[0,0,0],[.5,.5,.5]]
            ),
        X = obj(
            pristine = [[.25,.25,.25]],
            defect   = [[.39,.11,.15],[.11,.39,.15]]
            ),
        FFC = obj(
            #pristine = [[   0,   0,   0],[.25,.25,.25]],
            #defect   = [[.151,.151,-.08],[.10,.10,.33]]
            pristine = [[   0,   0,    0],[.25 ,.25 ,.25 ],[.5  ,.5  ,    0],[.75 ,.75 ,.25 ],[1.5  ,1.5  ,0   ],[1.75 ,1.75 ,.25 ]],
            defect   = [[.151,.151,-.081],[.099,.099,.331],[.473,.473,-.059],[.722,.722,.230],[1.528,1.528,.020],[1.777,1.777,.309]]
            )
        )
    )


def generate_defect_structure(defect,structure,shape=None,element=None,
                              tiling=None,scale=1.,kgrid=None,kshift=(0,0,0),
                              units=None,struct_type=DefectStructure):
    if structure in defects:
        dstruct = defects[structure]
    else:
        DefectStructure.class_error('defects for '+structure+' structure have not yet been implemented')
    #end if
    if defect in dstruct:
        drep = dstruct[defect]
    else:
        DefectStructure.class_error(defect+' defect not found for '+structure+' structure')
    #end if

    ds = generate_crystal_structure(
        structure = structure,
        shape     = shape,
        element   = element,
        tiling    = tiling,
        scale     = 1.0,
        kgrid     = kgrid,
        kshift    = kshift,
        units     = units,
        struct_type = struct_type
        )

    ds.replace(drep.pristine,pos=drep.defect)

    ds.rescale(scale)
    
    return ds
#end def generate_defect_structure




#if __name__=='__main__':
#    from numpy.random import rand
#    from matplotlib.pyplot import figure,plot,show
#
#    ax = array([[1.0,.3,.1],[.2,1.2,-.1],[.2,.1,1.]])
#    #ax = array([[1.0,0,0],[0,1.,0],[0,0,1.]])
#    pos = 4*(rand(50,3)-.5)
#    c = (ax[0]+ax[1])/2
#    elem = []
#    for i in range(len(pos)):
#        elem.append('Ge')
#    #end for
#    s = Structure(axes=ax,pos=pos,elem=elem)
#
#    #figure()
#    #plot(s.pos[:,0],s.pos[:,1],'bo')
#    #plot([0,x1,x1+x2,x2,0],[0,y1,y1+y2,y2,0],'k-',lw=2)
#    #s.recenter(c)
#    #plot(s.pos[:,0],s.pos[:,1],'r.')
#
#    #figure()
#    #s.plot2d('bo')
#    #s.recenter(c)
#    #s.plot2d('r.')
#    #show()
#
#    figure()
#    s.recenter(c)
#    s.plot2d('bo')
#    cs=s.carve(s.axes/2,s.center)
#    cs.plot2d('r.')
#    show()
##end if



if __name__=='__main__':
    a = convert(5.639,'A','B')

    large = generate_structure('diamond','fcc','Ge',(2,2,2),a)
    small = generate_structure('diamond','fcc','Ge',(1,1,1),a)

    large.add_kmesh((1,1,1))

    kmap = large.fold(small)

    print small.kpoints_unit()

#end if
