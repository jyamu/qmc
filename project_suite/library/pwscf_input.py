import os
import types
from copy import deepcopy
from superstring import string2val
from numpy import fromstring,empty,array,float64,ones,pi,dot
from numpy.linalg import inv
from unit_converter import convert
from generic import obj
from structure import Structure,kmesh
from physical_system import PhysicalSystem
from project_base import Pobj
from simulation import SimulationInput
from debug import *


def read_str(sv):
    return sv.strip('"').strip("'")
#end def read_str


def read_int(sv):
    return int(sv)
#end def read_int


def read_float(sv):
    return float(sv.replace('d','e').replace('D','e'))
#end def read_float


bconv = {'.true.':True,'.false.':False}
def read_bool(sv):
    return bconv[sv]
#end def read_bool


def write_str(val):
    return "'"+val+"'"
#end def write_str


def write_int(val):
    return str(val)
#end def write_int


def write_float(val):
    return str(val)
    #return '{0:20.18e}'.format(val)
#end def write_float


def write_bool(val):
    if val:
        return '.true.'
    else:
        return '.false.'
    #end if
#end def write_bool


readval={str:read_str,int:read_int,float:read_float,bool:read_bool}
writeval={str:write_str,int:write_int,float:write_float,bool:write_bool}


def noconv(v):
    return v
#end def noconv


def array_from_lines(lines):
    s=''
    for l in lines:
        s+=l+' '
    #end for
    a = fromstring(s,sep=' ')
    nelem = len(a)
    nlines = len(lines)
    dim = nelem/nlines
    a.shape = nlines,dim
    return a
#end def array_from_lines


pwscf_precision = '16.8f'
pwscf_array_format = '{0:'+pwscf_precision+'}' 
def array_to_string(a,pad='   ',format=pwscf_array_format,converter=noconv,rowsep='\n'):
    s=''
    if len(a.shape)==1:
        s+=pad
        for v in a:
            s += format.format(converter(v))+' '
        #end for
        s+=rowsep
    else:
        for r in a:
            s+=pad
            for v in r:
                s += format.format(converter(v))+' '
            #end for
            s+=rowsep
        #end for
    #end if
    return s
#end def array_to_string


            

class PwscfInputBase(Pobj):
    ints=['nstep','iprint','gdir','nppstr','nberrycyc','ibrav','nat','ntyp','nbnd','tot_charge','nr1','nr2','nr3','nr1s','nr2s','nr3s','nspin','multiplicity','tot_magnetization','edir','report','electron_maxstep','mixing_ndim','mixing_fixed_ns','ortho_para','diago_cg_maxiter','diago_david_ndim','nraise','bfgs_ndim','num_of_images','fe_nstep','sw_nstep','modenum','n_charge_compensation','nlev','lda_plus_u_kind']
    floats=['dt','max_seconds','etot_conv_thr','forc_conv_thr','celldm','A','B','C','cosAB','cosAC','cosBC','nelec','ecutwfc','ecutrho','degauss','starting_magnetization','nelup','neldw','ecfixed','qcutz','q2sigma','Hubbard_alpha','Hubbard_U','Hubbard_J','starting_ns_eigenvalue','emaxpos','eopreg','eamp','angle1','angle2','fixed_magnetization','lambda','london_s6','london_rcut','conv_thr','mixing_beta','diago_thr_init','efield','tempw','tolp','delta_t','upscale','trust_radius_max','trust_radius_min','trust_radius_ini','w_1','w_2','temp_req','ds','k_max','k_min','path_thr','fe_step','g_amplitude','press','wmass','cell_factor','press_conv_thr','xqq','ecutcoarse','mixing_charge_compensation','comp_thr','exx_fraction','ecutfock']
    strs=['calculation','title','verbosity','restart_mode','outdir','wfcdir','prefix','disk_io','pseudo_dir','occupations','smearing','input_dft','U_projection_type','constrained_magnetization','mixing_mode','diagonalization','startingpot','startingwfc','ion_dynamics','ion_positions','phase_space','pot_extrapolation','wfc_extrapolation','ion_temperature','opt_scheme','CI_scheme','cell_dynamics','cell_dofree','which_compensation','assume_isolated']
    bools=['wf_collect','tstress','tprnfor','lkpoint_dir','tefield','dipfield','lelfield','lberry','nosym','nosym_evc','noinv','force_symmorphic','noncolin','lda_plus_u','lspinorb','do_ee','london','diago_full_acc','tqr','remove_rigid_rot','refold_pos','first_last_opt','use_masses','use_freezing']

    section_aliases = dict(celldm1='celldm(1)',celldm2='celldm(2)',celldm3='celldm(3)',celldm4='celldm(4)',celldm5='celldm(5)',celldm6='celldm(6)')

    var_types = dict()
    for v in ints:
        var_types[v]=int
    for v in floats:
        var_types[v]=float
    for v in strs:
        var_types[v]=str
    for v in bools:
        var_types[v]=bool
#end class PwscfInputBase




class Element(PwscfInputBase):
    name = None
    def add(self,**variables):
        self._add_attributes(**variables)
    #end def add

    def read(self,lines):
        self.not_implemented()
    #end def read

    def write(self,parent):
        self.not_implemented()
    #end def write

    def post_process_read(self,parent):
        None
    #end def post_process_read
#end class Element




class Section(Element):
    def read(self,lines):
        for l in lines:
            tokens = l.split(',')
            for t in tokens:
                if len(t)>0:
                    var,val = t.split('=')
                    var = var.strip()
                    val = val.strip()
                    varname = var.split('(')[0]
                    if not varname in self.variables:
                        self.error('pwscf input section {0} does not have a variable named {1}, please check your input\nif correct, please add a new variable ({1}) to the {0} PwscfInput class'.format(self.__class__.__name__,varname),trace=False)
                    #end if
                    if not varname in self.var_types:
                        self.error('a type has not been specified for variable {0}\nplease add it to PwscfInputBase'.format(varname),trace=False)
                    #end if
                    vtype = self.var_types[varname]
                    val = readval[vtype](val)
                    self[var] = val
                #end if
            #end for
        #end for
    #end def read

    def write(self,parent):
        c='&'+self.name.upper()+'\n'
        vars = list(self.keys())
        vars.sort()
        for var in vars:
            val = self[var]
            #vtype = type(val)
            #sval = writeval[vtype](val)
            
            vtype = None
            if isinstance(val,str):
                vtype = str
            elif isinstance(val,float):
                vtype = float
            #elif isinstance(val,bool):
            #    vtype = bool
            elif var in self.bools:
                vtype = bool
            elif isinstance(val,int):
                vtype = int
            #end if

            sval = writeval[vtype](val)

            if var in self.section_aliases.keys():
                vname = self.section_aliases[var]
            else:
                vname = var
            #end if
            #c+='   '+vname+' = '+sval+'\n'
            c+='   '+'{0:<15} = {1}\n'.format(vname,sval)
        #end for
        c+='/'+'\n\n'
        return c
    #end def write
#end class Section




class Card(Element):
    def __init__(self):
        self.specifier = ''
    #end def __init__

    def get_specifier(self,line):
        tokens = line.split()
        if len(tokens)>1:
            self.specifier = tokens[1].strip('{}').lower()
        #end if
    #end def get_specifier

    def read(self,lines):
        self.get_specifier(lines[0])
        self.read_contents(lines[1:])
    #end def read

    def write(self,parent):
        c = self.name.upper()+' '+self.specifier+'\n'
        c += self.write_contents()+'\n'
        return c
    #end def write

    def read_contents(self,lines):
        self.not_implemented()
    #end def read_contents

    def write_contents(self):
        self.not_implemented()
    #end def write_contents

    def change_specifier(self,new_specifier):
        self.not_implemented()
    #end def change_specifier    
#end class Card



class control(Section):
    name = 'control'
    variables = set(
        ['calculation','title','verbosity','restart_mode','wf_collect','nstep',
         'iprint','tstress','tprnfor','dt','outdir','wfcdir','prefix',
         'lkpoint_dir','max_seconds','etot_conv_thr','forc_conv_thr','disk_io',
         'pseudo_dir','tefield','dipfield','lelfield','lberry','gdir','nppstr',
         'nberrycyc'])
#end class control




class system(Section):
    name = 'system'
    variables = set(
        ['ibrav','celldm','A','B','C','cosAB','cosAC','cosBC','nat','ntyp',
         'nbnd','nelec','tot_charge','ecutwfc','ecutrho','nr1','nr2','nr3',
         'nr1s','nr2s','nr3s','nosym','nosym_evc','noinv','force_symmorphic',
         'occupations','degauss','smearing','nspin','noncolin',
         'starting_magnetization','nelup','neldw','multiplicity',
         'tot_magnetization','ecfixed','qcutz','q2sigma','input_dft',
         'lda_plus_u','Hubbard_alpha','Hubbard_U','starting_ns_eigenvalue',
         'U_projection_type','edir','emaxpos','eopreg','eamp','angle1',
         'angle2','constrained_magnetization','fixed_magnetization','lambda',
         'report','lspinorb','assume_isolated','do_ee','london','london_s6',
         'london_rcut','exx_fraction','ecutfock',
         'lda_plus_u_kind','Hubbard_J'])

    atomic_variables = obj(
        hubbard_u = 'Hubbard_U',
        start_mag = 'starting_magnetization',
        hubbard_j = 'Hubbard_J'
        )

    # specialized read for partial array variables (hubbard U, starting mag, etc)
    def post_process_read(self,parent):
        if 'atomic_species' in parent:
            keys = self.keys()
            for alias,name in self.atomic_variables.iteritems():
                has_var = False
                avals = obj()
                akeys = []
                for key in keys:
                    if key.startswith(name):
                        has_hubbard_u = True
                        akeys.append(key)
                        index = int(key.replace(name,'').strip('()'))
                        avals[index] = self[key]
                    #end if
                #end for
                if has_var:
                    for key in akeys:
                        del self[key]
                    #end for
                    atoms = parent.atomic_species.atoms
                    value = obj()
                    for i in range(len(atoms)):
                        index = i+1
                        if index in avals:
                            value[atoms[i]] = avals[i+1]
                        #end if
                    #end for
                    self[alias] = value
                #end if
            #end for
        #end if
    #end def post_process_read


    # specialized write for odd handling of hubbard U
    def write(self,parent):
        c='&'+self.name.upper()+'\n'
        vars = list(self.keys())
        vars.sort()
        for var in vars:
            val = self[var]
            if var in self.atomic_variables:
                if 'atomic_species' in parent:
                    atoms = parent.atomic_species.atoms
                    avar = self.atomic_variables[var]
                    for i in range(len(atoms)):
                        index = i+1
                        vname = '{0}({1})'.format(avar,index)
                        atom = atoms[i]
                        if atom in val:
                            sval = writeval[float](val[atom])
                            c+='   '+'{0:<15} = {1}\n'.format(vname,sval)
                        #end if
                    #end for
                else:
                    self.error('cannot write {0}, atomic_species is not present'.format(var))
                #end if
            else:
                #vtype = type(val)
                #sval = writeval[vtype](val)

                vtype = None
                if isinstance(val,str):
                    vtype = str
                elif isinstance(val,float):
                    vtype = float
                #elif isinstance(val,bool):
                #    vtype = bool
                elif var in self.bools:
                    vtype = bool
                elif isinstance(val,int):
                    vtype = int
                #end if
                sval = writeval[vtype](val)

                if var in self.section_aliases.keys():
                    vname = self.section_aliases[var]
                else:
                    vname = var
                #end if
                #c+='   '+vname+' = '+sval+'\n'
                c+='   '+'{0:<15} = {1}\n'.format(vname,sval)
            #end if
        #end for
        c+='/'+'\n\n'
        return c
    #end def write

#end class system


class electrons(Section):
    name = 'electrons'
    variables =  set(
        ['electron_maxstep','conv_thr','mixing_mode','mixing_beta','mixing_ndim',
         'mixing_fixed_ns','diagonalization','ortho_para','diago_thr_init',
         'diago_cg_maxiter','diago_david_ndim','diago_full_acc','efield',
         'startingpot','startingwfc','tqr'])
#end class electrons


class ions(Section):
    name = 'ions'
    variables = set(
        ['ion_dynamics','ion_positions','phase_space','pot_extrapolation',
         'wfc_extrapolation','remove_rigid_rot','ion_temperature','tempw',
         'tolp','delta_t','nraise','refold_pos','upscale','bfgs_ndim',
         'trust_radius_max','trust_radius_min','trust_radius_ini','w_1','w_2',
         'num_of_images','opt_scheme','CI_scheme','first_last_opt','temp_req',
         'ds','k_max','k_min','path_thr','use_masses','use_freezing','fe_step',
         'g_amplitude','fe_nstep','sw_nstep'])
#end class ions


class cell(Section):
    name = 'cell'
    variables =  set(
        ['cell_dynamics','press','wmass','cell_factor','press_conv_thr',
         'cell_dofree'])
#end class cell


class phonon(Section):
    name = 'phonon'
    variables =  set(['modenum','xqq'])
#end class phonon


class ee(Section):
    name = 'ee'
    variables = set(
        ['which_compensation','ecutcoarse','mixing_charge_compensation',
         'n_charge_compensation','comp_thr','nlev'])
#end class ee




class atomic_species(Card):
    name = 'atomic_species'

    def read_contents(self,lines):
        atoms = []
        masses   = obj()
        pseudopotentials = obj()
        for l in lines:
            tokens = l.split()
            atom = tokens[0]
            atoms.append(tokens[0])
            masses[atom] = float(tokens[1])
            pseudopotentials[atom] = tokens[2]
        #end for
        self.add(atoms=atoms,masses=masses,pseudopotentials=pseudopotentials)
    #end def read_contents

    def write_contents(self):
        c = ''
        for at in self.atoms:
            c += '   '+'{0:2}'.format(at)+' '+str(self.masses[at])+' '+self.pseudopotentials[at]+'\n'
        #end for
        return c
    #end def write_contents
#end class atomic_species


class atomic_positions(Card):
    name = 'atomic_positions'

    def read_contents(self,lines):
        npos = len(lines)
        dim = 3
        atoms = []
        positions = empty((npos,dim))
        relax_directions = empty((npos,dim),dtype=int)
        i=0
        has_relax_directions = False
        for l in lines:
            tokens = l.split()
            atoms.append(tokens[0])
            positions[i,:] = array(tokens[1:4],dtype=float64)
            has_relax_directions = len(tokens)==7
            if has_relax_directions:
                relax_directions[i,:] = array(tokens[4:7],dtype=int)
            #end if
            i+=1
        #end for
        self.add(atoms=atoms,positions=positions)
        if has_relax_directions:
            self.add(relax_directions=relax_directions)
        #end if
    #end def read_contents


    def write_contents(self):
        c = ''
        has_relax_directions = 'relax_directions' in self
        if has_relax_directions:
            rowsep = ''
        else:
            rowsep = '\n'
        #end if
        for i in range(len(self.atoms)):
            c +='   '+'{0:2}'.format(self.atoms[i])+' '
            c += array_to_string(self.positions[i],pad='',rowsep=rowsep)
            if has_relax_directions:
                c += array_to_string(self.relax_directions[i],pad='',format='{0}')
            #end if
        #end for
        return c
    #end def write_contents


    def change_specifier(self,new_specifier,pwi):
        scale,axes = pwi.get_common_vars('scale','axes')

        pos = self.positions

        spec = self.specifier
        if spec=='alat' or spec=='':
            pos *= scale
        elif spec=='bohr':
            None
        elif spec=='angstrom':
            pos *= convert(1.,'A','B')
        elif spec=='crystal':
            pos = dot(pos,axes)
        else:
            self.error('old specifier for atomic_positions is invalid\n  old specifier: '+spec+'\n  valid options: alat, bohr, angstrom, crystal')
        #end if

        spec = new_specifier
        if spec=='alat' or spec=='':
            pos /= scale
        elif spec=='bohr':
            None
        elif spec=='angstrom':
            pos /= convert(1.,'A','B')
        elif spec=='crystal':
            pos = dot(pos,inv(axes))
        else:
            self.error('new specifier for atomic_positions is invalid\n  new specifier: '+spec+'\n  valid options: alat, bohr, angstrom, crystal')
        #end if
            
        self.positions = pos
        self.specifier = new_specifier
    #end def change_specifier

#end class atomic_positions




class k_points(Card):
    name = 'k_points'

    def read_contents(self,lines):
        if self.specifier in ['tpiba','crystal','tpiba_b','crystal_b','']:
            self.nkpoints = int(lines[0])
            a = array_from_lines(lines[1:])
            self.kpoints = a[:,0:3]
            self.weights = a[:,3]
            self.weights.shape = (self.nkpoints,)
        elif self.specifier == 'automatic':
            a = fromstring(lines[0],sep=' ')
            self.grid  = a[0:3]
            self.shift = a[3:]
        else:
            self.error('k_points specifier '+self.specifier+' is unrecognized')
        #end if
    #end def read_contents


    def write_contents(self):
        c = ''        
        if self.specifier in ['tpiba','crystal','tpiba_b','crystal_b','']:
            self.nkpoints = len(self.kpoints)
            c+='   '+str(self.nkpoints)+'\n'
            a = empty((self.nkpoints,4))
            a[:,0:3] = self.kpoints
            a[:,3]   = self.weights[:]
            c+=array_to_string(a)
        elif self.specifier == 'automatic':
            c+='   '
            c+=array_to_string(array(self.grid),pad='',format='{0}',converter=int,rowsep='')
            c+=array_to_string(array(self.shift),pad=' ',format='{0}',converter=int)
        else:
            self.error('k_points specifier '+self.specifier+' is unrecognized')
        #end if
        return c
    #end def write_contents


    def change_specifier(self,new_specifier,pwi):
        scale,kaxes = pwi.get_common_vars('scale','kaxes')

        spec = self.specifier
        if spec=='tpiba' or spec=='':
            kpoints = self.kpoints*(2*pi)/scale
        elif spec=='gamma':
            kpoints = array([[0,0,0]])
        elif spec=='crystal':
            kpoints = dot(self.kpoints,kaxes)
        elif spec=='automatic':
            grid  = array(self.grid,dtype=int)
            shift = .5*array(self.shift)
            kpoints = kmesh(kaxes,grid,shift)
        elif spec=='tpiba_b' or spec=='crystal_b':
            self.error('specifiers tpiba_b and crystal_b have not yet been implemented in change_specifier')
        else:
            self.error('old specifier for k_points is invalid\n  old specifier: '+spec+'\n  valid options: tpiba, gamma, crystal, automatic, tpiba_b, crystal_b')
        #end if

        spec = new_specifier
        if spec=='tpiba' or spec=='':
            kpoints = kpoints/((2*pi)/scale)
        elif spec=='gamma':
            kpoints = array([[0,0,0]])
        elif spec=='crystal':
            kpoints = dot(kpoints,inv(kaxes))
        elif spec=='automatic':
            if self.specifier!='automatic':
                self.error('cannot map arbitrary kpoints into a Monkhorst-Pack mesh')
            #end if
        elif spec=='tpiba_b' or spec=='crystal_b':
            self.error('specifiers tpiba_b and crystal_b have not yet been implemented in change_specifier')
        else:
            self.error('new specifier for k_points is invalid\n  new specifier: '+spec+'\n  valid options: tpiba, gamma, crystal, automatic, tpiba_b, crystal_b')
        #end if
            
        self.kpoints   = kpoints
        self.specifier = new_specifier
    #end def change_specifier
#end class k_points




class cell_parameters(Card):
    name = 'cell_parameters'

    def read_contents(self,lines):
        self.vectors = array_from_lines(lines)
    #end def read_contents

    def write_contents(self):
        return array_to_string(self.vectors)
    #end def write_contents
#end class cell_parameters




class climbing_images(Card):
    name = 'climbing_images'

    def read_contents(self,lines):
        self.images = array_from_lines(lines)
    #end def read_contents

    def write_contents(self):
        c='   '
        for n in self.images:
            c+=str(int(n))+' '
        #end for
        return c
    #end def write_contents
#end class climbing_images




class constraints(Card):
    name = 'constraints'

    def read_contents(self,lines):
        tokens = lines[0].split()
        self.ncontraints = int(tokens[0])
        if len(tokens)>1:
            self.tolerance = float(tokens[1])
        #end if
        self.constraints = obj()
        for i in range(len(lines)-1):
            tokens = lines[i+1].split()
            cons = obj()
            cons.type = tokens[0]
            cons.parameters = array(tokens[1:],dtype=float64)
            self.constraints[i] = cons
        #end for
    #end def read_contents

    def write_contents(self):
        c = '   '+str(self.nconstraints)
        if 'tolerance' in self:
            c+=' '+str(self.tolerance)
        #end if
        for cons in self.constraints:
            c+='   '+cons.type+' '+array_to_string(cons.parameters,pad='')
        #end for
        return c
    #end def write_contents
#end class constraints




class collective_vars(Card):
    name = 'collective_vars'

    def read_contents(self,lines):
        tokens = lines[0].split()
        self.ncontraints = int(tokens[0])
        if len(tokens)>1:
            self.tolerance = float(tokens[1])
        #end if
        self.collective_vars = obj()
        for i in range(len(lines)-1):
            tokens = lines[i+1].split()
            collv = obj()
            collv.type = tokens[0]
            collv.parameters = array(tokens[1:],dtype=float64)
            self.collective_vars[i] = collv
        #end for
    #end def read_contents

    def write_contents(self):
        c= '   '+str(self.ncollective_vars)
        if 'tolerance' in self:
            c+=' '+str(self.tolerance)
        #end if
        for collv in self.collective_vars:
            c+='   '+collv.type+' '+array_to_string(collv.parameters,pad='')
        #end for        
        return c
    #end def write_contents
#end class collective_vars




class occupations(Card):
    name = 'occupations'

    def read_contents(self,lines):
        self.occupations = array_from_lines(lines)
    #end def read_contents
 
    def write_contents(self):
        return array_to_string(self.occupations)
    #end def write_contents
#end class occupations










class PwscfInput(SimulationInput):

    sections = ['control','system','electrons','ions','cell','phonon','ee']
    cards    = ['atomic_species','atomic_positions','k_points',
                'cell_parameters','climbing_images','constraints',
                'collective_vars','occupations']

    section_types = obj(
        control   = control  ,     
        system    = system   ,     
        electrons = electrons,     
        ions      = ions     ,     
        cell      = cell     ,     
        phonon    = phonon   ,     
        ee        = ee            
        )
    card_types = obj(
        atomic_species   = atomic_species  ,    
        atomic_positions = atomic_positions,    
        k_points         = k_points        ,    
        cell_parameters  = cell_parameters ,    
        climbing_images  = climbing_images ,    
        constraints      = constraints     ,    
        collective_vars  = collective_vars ,    
        occupations      = occupations         
        )

    element_types = obj()
    element_types.transfer_from(section_types)
    element_types.transfer_from(card_types)

    required_elements = ['control','system','electrons','atomic_species','atomic_positions','k_points']
        

    def __init__(self,*elements):
        elements = list(elements)
        if len(elements)==1 and os.path.exists(elements[0]):
            self.read(elements[0])
        elif len(elements)==1 and ('.' in elements[0] or '/' in elements[0]):
            self.error('input file '+elements[0]+' does not seem to exist')
        else:
            for element in self.required_elements:
                if element not in elements:
                    elements.append(element)
                #end if
            #end for
            for element in elements:
                if element in self.element_types:
                    self[element] = self.element_types[element]()
                else:
                    self.error('  Error: '+element+' is not a pwscf element\n  valid options are '+str(list(self.element_types.keys())))
                #end if
            #end for
        #end if
    #end def __init__


    def read_contents(self,contents):
        lines = contents.splitlines()
        in_element = False
        elem_type = None
        for line in lines:
            l = line.strip()
            if len(l)>0 and l[0]!='!':
                tokens = l.split()
                if l.startswith('&'):
                    if l[1:].lower() in self.sections:
                        prev_type = elem_type
                        in_element = True
                        elem_name = l[1:].lower()
                        elem_type = 'section'
                        c=[]
                    else:
                        print 'PwscfInput Error: '+l[1:]+' is not a recognized pwscf section, exiting.'
                        exit()
                    #end if
                elif tokens[0].lower() in self.cards and '=' not in l:
                    if elem_type == 'card':
                        if not elem_name in self:
                            self[elem_name] = self.element_types[elem_name]()
                        #end if
                        self[elem_name].read(c)
                    #end if
                    in_element = True
                    elem_name = tokens[0].lower()
                    elem_type = 'card'
                    c=[l]
                elif l=='/':
                    in_element = False
                    if not elem_name in self:
                        self[elem_name] = self.element_types[elem_name]()
                    #end if
                    self[elem_name].read(c)
                elif in_element:
                    c.append(l)
                else:
                    print 'PwscfInput Error: the following line is invalid, exiting.'
                    print l
                    exit()
                #end if
            #end if
        #end for
        if elem_type == 'card':
            if not elem_name in self:
                self[elem_name] = self.element_types[elem_name]()
            #end if
            self[elem_name].read(c)
        #end if
        #post-process hubbard u and related variables
        for element in self:
            element.post_process_read(self)
        #end for
    #end def read_contents


    def write_contents(self):
        contents = ''
        for s in self.sections:
            if s in self:
                contents += self[s].write(self)
            #end if
        #end for
        contents+='\n'
        for c in self.cards:
            if c in self:
                contents += self[c].write(self)
            #end if
        #end for
        contents+='\n'
        return contents
    #end def write_contents


    def get_common_vars(self,*vars):
        scale = None
        axes  = None
        kaxes = None

        if 'celldm(1)' in self.system:
            scale = self.system['celldm(1)']
            if 'cell_parameters' in self:
                axes = scale*array(self.cell_parameters.vectors)
                kaxes = 2*pi*inv(axes).T
            #end if
        #end if

        vals = []
        loc = locals()
        errors = False
        for var in vars:
            if var in loc:
                val = loc[var]
                if val==None:
                    self.error('requested variable '+var+' was not found',exit=False)
                    errors = True
                #end if
            else:
                self.error('requested variable '+var+' is not computed by get_common_vars',exit=False)
                errors = True
                val = None
            #end if
            vals.append(val)
        #end for
        if errors:
            self.error('could not get requested variables')
        #end if
        return vals
    #end def get_common_vars


    def incorporate_system(self,system,spin_polarized=False):
        system.check_folded_system()
        system.update_particles()
        system.change_units('B')
        p  = system.particles
        s  = system.structure
        nc = system.net_charge
        ns = system.net_spin

        nup = p.up_electron.count
        ndn = p.down_electron.count

        self.system.ibrav        = 0
        self.system['celldm(1)'] = 1.0e0
        nions,nspecies = p.count_ions(species=True)
        self.system.nat          = nions
        self.system.ntyp         = nspecies
        #self.system.nelec        = nup+ndn
        self.system.tot_charge   = nc
        mag = nup-ndn
        if mag!=0 or spin_polarized:
            self.system.nspin = 2
            self.system.tot_magnetization = mag
        #end if

        if not 'cell_parameters' in self:
            self.cell_parameters = self.element_types['cell_parameters']()
        #end if
        self.cell_parameters.specifier = 'cubic'
        self.cell_parameters.vectors   = s.axes.copy()

        kpoints = s.kpoints/(2*pi)
        nkpoints = len(kpoints)
        if nkpoints>0:
            self.k_points.specifier = 'tpiba'
            self.k_points.nkpoints  = nkpoints
            self.k_points.kpoints   = kpoints
            self.k_points.weights   = s.kweights.copy()
        #end if

        atoms = p.get_ions()
        masses = obj()
        for name,a in atoms.iteritems():
            masses[name] = convert(a.mass,'me','amu')
        #end for
        self.atomic_species.atoms  = list(atoms.keys())
        self.atomic_species.masses = masses
        # set pseudopotentials for renamed atoms (e.g. Cu3 is same as Cu)
        pp = self.atomic_species.pseudopotentials
        for atom in self.atomic_species.atoms:
            if not atom in pp:
                iselem,symbol = p.is_element(atom,symbol=True)
                if iselem and symbol in pp:
                    pp[atom] = str(pp[symbol])
                #end if
            #end if
        #end for

        self.atomic_positions.specifier = 'alat'
        self.atomic_positions.positions = s.pos.copy()
        self.atomic_positions.atoms     = list(s.elem)
        if 'frozen' in s:
            frozen = s.frozen
            if 'relax_directions' in self.atomic_positions:
                relax_directions = self.atomic_positions.relax_directions
            else:
                relax_directions = ones(s.pos.shape,dtype=int)
            #end if
            for i in xrange(len(s.pos)):
                relax_directions[i,0] = int(not frozen[i,0] and relax_directions[i,0])
                relax_directions[i,1] = int(not frozen[i,1] and relax_directions[i,1])
                relax_directions[i,2] = int(not frozen[i,2] and relax_directions[i,2])
            #end for
            self.atomic_positions.relax_directions = relax_directions
        #end if                    
    #end def incorporate_system

        
    def return_system(self):
        ibrav = self.system.ibrav
        if ibrav!=0:
            self.error('ability to handle non-zero ibrav not yet implemented')
        #end if

        scale,axes,kaxes = self.get_common_vars('scale','axes','kaxes')

        elem = list(self.atomic_positions.atoms)
        ap = self.atomic_positions.copy()
        ap.change_specifier('bohr',self)
        pos = ap.positions

        kp = self.k_points.copy()
        kp.change_specifier('tpiba',self)
        kpoints = kp.kpoints*(2*pi)/scale

        center = axes.sum(0)/2
        structure = Structure(
            axes    = axes,
            elem    = elem,
            scale   = scale,
            pos     = pos,
            center  = center,
            kpoints = kpoints,
            units   = 'B',
            rescale = False
            )
        structure.zero_corner()
        structure.recenter()
  
        ion_charge = 0
        valency = dict()
        atoms   = list(self.atomic_positions.atoms)
        for atom in self.atomic_species.atoms:
            pseudo_file = self.atomic_species.pseudopotentials[atom]
            if self.pseudopotentials!=None and pseudo_file in self.pseudopotentials:                
                pseudopot = self.pseudopotentials[pseudo_file]
                element = pseudopot.element
                valence = int(pseudopot.Z)
                ion_charge += atoms.count(atom)*valence
                valency[atom] = valence
            else:
                self.error('file '+pseudo_file+' was not listed in Pseudopotentials object\n  please specify pseudopotentials with the settings function',trace=False)
            #end if
        #end for

        if 'nelup' in self.system:
            nup = self.system.nelup
            ndn = self.system.neldw
            net_charge = ion_charge - nup - ndn
            net_spin   = nup - ndn
        elif 'tot_magnetization' in self.system:
            net_spin = self.system.tot_magnetization
            if 'nelec' in self.system:
                net_charge = ion_charge - self.system.nelec
            else:
                net_charge = 0
            #end if
        else:
            net_spin = 0
            if 'nelec' in self.system:
                net_charge = ion_charge - self.system.nelec
            else:
                net_charge = 0
            #end if
        #end if

        system = PhysicalSystem(structure,net_charge,net_spin,**valency)

        return system
    #end def return_system

#end class PwscfInput




def generate_pwscf_input(selector,**kwargs):
    if 'system' in kwargs:
        system = kwargs['system']
        if isinstance(system,PhysicalSystem):
            system.update_particles()
        #end if
    #end if
    if selector=='scf':
        return generate_scf_input(**kwargs)
    elif selector=='nscf':
        return generate_nscf_input(**kwargs)
    elif selector=='relax':
        return generate_relax_input(**kwargs)
    else:
        PwscfInput.class_error('selection '+str(selector)+' has not been implemented for pwscf input generation')
    #end if
#end def generate_pwscf_input



def generate_scf_input(prefix       = 'pwscf',
                       outdir       = 'pwscf_output',
                       input_dft    = None,
                       exx_fraction = None,
                       ecut         = 200.,
                       ecutrho      = None,
                       ecutfock     = None,
                       conv_thr     = 1e-10,
                       mixing_beta  = .7,
                       occupations  = 'smearing',
                       smearing     = 'fermi-dirac',
                       degauss      = 0.0001,
                       nosym        = False,
                       spin_polarized = False,
                       hubbard_u    = None,
                       start_mag    = None,
                       assume_isolated = None,
                       wf_collect   = True,
                       restart_mode = 'from_scratch',
                       tstress      = True,
                       tprnfor      = True,
                       disk_io      = 'low',
                       verbosity    = 'high',
                       ibrav        = 0,
                       electron_maxstep = 1000,
                       kgrid        = None,
                       kshift       = None,
                       pseudos      = None,
                       system       = None,
                       use_folded   = True,
                       group_atoms  = True):
    if pseudos is None:
        pseudos = []
    #end if
    
    pseudopotentials = obj()
    atoms = []
    for ppname in pseudos:
        element = ppname[0:2].strip('.')
        atoms.append(element)
        pseudopotentials[element] = ppname
    #end for

    if ecutrho is None:
        ecutrho = 4*ecut
    #end if

    pw = PwscfInput()
    pw.control.set(
        calculation  = 'scf',
        prefix       = prefix,
        restart_mode = restart_mode,
        tstress      = tstress,
        tprnfor      = tprnfor,
        pseudo_dir   = './',
        outdir       = outdir,
        disk_io      = disk_io,
        verbosity    = verbosity,
        wf_collect   = wf_collect
        )
    pw.system.set(
        ibrav       = ibrav,
        ecutwfc     = ecut,
        ecutrho     = ecutrho,
        nosym       = nosym
        )
    if assume_isolated!=None:
        pw.system.assume_isolated = assume_isolated
    #end if
    if occupations!=None:
        if occupations=='smearing':
            pw.system.set(
                occupations = occupations,
                smearing    = smearing,
                degauss     = degauss,
                )
        else:
            pw.system.occupations = occupations
        #end if
    #end if
    pw.electrons.set(
        conv_thr    = conv_thr,
        mixing_beta = mixing_beta,
        electron_maxstep = electron_maxstep
        )
    pw.atomic_species.set(
        atoms            = atoms,
        pseudopotentials = pseudopotentials
        )

    if input_dft!=None:
        pw.system.input_dft = input_dft
    #end if
    if exx_fraction!=None:
        pw.system.exx_fraction = exx_fraction
    #end if
    if ecutfock!=None:
        pw.system.ecutfock = ecutfock
    #end if

    system.check_folded_system()
    system.change_units('B')
    s = system.structure
    #setting the 'lattice' (cell axes) requires some delicate care
    #  qmcpack will fail if this is even 1e-10 off of what is in 
    #  the wavefunction hdf5 file from pwscf
    if s.folded_structure!=None:
        fs = s.folded_structure
        axes = array(array_to_string(fs.axes).split(),dtype=float)
        axes.shape = fs.axes.shape
        axes = dot(s.tmatrix,axes)
        if abs(axes-s.axes).sum()>1e-5:
            PwscfInput.class_error('supercell axes do not match tiled version of folded cell axes\n  you may have changed one set of axes (super/folded) and not the other\n  folded cell axes:\n'+str(fs.axes)+'\n  supercell axes:\n'+str(s.axes)+'\n  folded axes tiled:\n'+str(axes))
        #end if
    else:
        axes = array(array_to_string(s.axes).split(),dtype=float)
        axes.shape = s.axes.shape
    #end if
    s.adjust_axes(axes)

    if use_folded:
        system = system.get_primitive()
    #end if
        
    if start_mag!=None:
        spin_polarized=True
    #end if

    if system!=None:
        pw.incorporate_system(system,spin_polarized=spin_polarized)
    #end if

    if hubbard_u!=None:
        if not isinstance(hubbard_u,(dict,obj)):
            PwscfInput.class_error('input hubbard_u must be of type dict or obj')
        #end if
        pw.system.hubbard_u = deepcopy(hubbard_u)
        pw.system.lda_plus_u = True
    #end if
    if start_mag!=None:
        if not isinstance(start_mag,(dict,obj)):
            PwscfInput.class_error('input start_mag must be of type dict or obj')
        #end if
        pw.system.start_mag = deepcopy(start_mag)
        #if 'tot_magnetization' in pw.system:
        #    del pw.system.tot_magnetization
        ##end if
        if 'multiplicity' in pw.system:
            del pw.system.multiplicity
        #end if
    #end if

    if kshift==None:
        kshift = (1,1,1)
    #end if

    if system is not None:
        structure = system.structure
        if group_atoms:
            structure.group_atoms()
        #end if
        if structure.at_Gpoint():
            pw.k_points.clear()
            pw.k_points.set(
                specifier = 'automatic',
                grid  = (1,1,1),
                shift = (0,0,0)
                )
        elif structure.at_Lpoint():
            pw.k_points.clear()
            pw.k_points.set(
                specifier = 'automatic',
                grid  = (1,1,1),
                shift = (1,1,1)
                )
        #end if
    #end if

    if kgrid!=None:
        pw.k_points.clear()
        pw.k_points.set(
            specifier = 'automatic',
            grid     = kgrid,
            shift    = kshift
            )
    elif system==None:
        pw.k_points.clear()
        pw.k_points.set(
            specifier = 'automatic',
            grid     = (1,1,1),
            shift    = kshift
            )
    #end if


    return pw
#end def generate_scf_input




def generate_nscf_input(**kwargs):
    pw = generate_scf_input(**kwargs)
    pw.control.set(
        calculation = 'nscf'
        )
    return pw
#end def generate_nscf_input




def generate_relax_input(prefix       = 'pwscf',
                         outdir       = 'pwscf_output',
                         input_dft    = None,
                         exx_fraction = None,
                         ecut         = 50.,
                         ecutrho      = None,
                         ecutfock     = None,
                         conv_thr     = 1e-6,
                         mixing_beta  = .7,
                         occupations  = 'smearing',
                         smearing     = 'fermi-dirac',
                         degauss      = 0.0001,
                         nosym        = True,
                         spin_polarized = False,
                         assume_isolated = None,
                         upscale      = 100,
                         pot_extrapolation = 'second_order',
                         wfc_extrapolation = 'second_order',
                         kgrid        = None,
                         kshift       = None,
                         pseudos      = None,
                         system       = None,
                         use_folded   = False,
                         group_atoms  = True):
    if pseudos is None:
        pseudos = []
    #end if
    
    pseudopotentials = obj()
    atoms = []
    for ppname in pseudos:
        element = ppname[0:2].strip('.')
        atoms.append(element)
        pseudopotentials[element] = ppname
    #end for

    if ecutrho is None:
        ecutrho = 4*ecut
    #end if

    pw = PwscfInput('ions')
    pw.control.set(
        calculation  = 'relax',
        prefix       = prefix,
        restart_mode = 'from_scratch',
        #tstress      = True,
        #tprnfor      = True,
        pseudo_dir   = './',
        outdir       = outdir,
        disk_io      = 'low',
        verbosity    = 'high',
        wf_collect   = False
        )
    pw.system.set(
        ibrav       = 0,
        ecutwfc     = ecut,
        ecutrho     = ecutrho,
        nosym       = nosym
        )
    if assume_isolated!=None:
        pw.system.assume_isolated = assume_isolated
    #end if
    if occupations!=None:
        if occupations=='smearing':
            pw.system.set(
                occupations = occupations,
                smearing    = smearing,
                degauss     = degauss,
                )
        #end if
    #end if
    pw.electrons.set(
        conv_thr         = conv_thr,
        mixing_beta      = mixing_beta,
        electron_maxstep = 1000
        )
    pw.atomic_species.set(
        atoms            = atoms,
        pseudopotentials = pseudopotentials
        )
    pw.ions.set(
        ion_dynamics      = 'bfgs',
        upscale           = upscale,
        pot_extrapolation = pot_extrapolation,
        wfc_extrapolation = wfc_extrapolation
        )

    if input_dft!=None:
        pw.system.input_dft = input_dft
    #end if
    if exx_fraction!=None:
        pw.system.exx_fraction = exx_fraction
    #end if
    if ecutfock!=None:
        pw.system.ecutfock = ecutfock
    #end if
    if system!=None:
        if use_folded:
            system = system.get_primitive()
        #end if
        pw.incorporate_system(system,spin_polarized=spin_polarized)
    #end if

    if kshift==None:
        kshift = (1,1,1)
    #end if


    if system is not None:
        structure = system.structure
        if group_atoms:
            structure.group_atoms()
        #end if
        if structure.at_Gpoint():
            pw.k_points.clear()
            pw.k_points.set(
                specifier = 'automatic',
                grid  = (1,1,1),
                shift = (0,0,0)
                )
        elif structure.at_Lpoint():
            pw.k_points.clear()
            pw.k_points.set(
                specifier = 'automatic',
                grid  = (1,1,1),
                shift = (1,1,1)
                )
        #end if
    #end if

    if kgrid!=None:
        pw.k_points.clear()
        pw.k_points.set(
            specifier = 'automatic',
            grid     = kgrid,
            shift    = kshift
            )
    elif system==None:
        pw.k_points.clear()
        pw.k_points.set(
            specifier = 'automatic',
            grid     = (1,1,1),
            shift    = kshift
            )
    #end if

    return pw
#end def generate_relax_input


#def generate_nscf_input(prefix='pwscf',outdir='pwscf_output',ecut=200.,kpoints=None,weights=None,pseudos=None,system=None):
#    if pseudos is None:
#        pseudos = []
#    #end if
#    
#    pseudopotentials = obj()
#    atoms = []
#    for ppname in pseudos:
#        element = ppname[0:2]
#        atoms.append(element)
#        pseudopotentials[element] = ppname
#    #end for
#
#    pw = PwscfInput()
#    pw.control.set(
#        calculation  = 'nscf',
#        prefix       = prefix,
#        restart_mode = 'from_scratch',
#        tstress      = True,
#        tprnfor      = True,
#        pseudo_dir   = './',
#        outdir       = outdir,
#        disk_io      = 'low',
#        wf_collect   = True
#        )
#    pw.system.set(
#        ibrav       = 0,
#        degauss     = 0.001,
#        smearing    = 'mp',
#        occupations = 'smearing',
#        ecutwfc     = ecut,
#        ecutrho     = 4*ecut
#        )
#    pw.electrons.set(
#        conv_thr    = 1.e-10,
#        mixing_beta = 0.7
#        )
#    pw.atomic_species.set(
#        atoms            = atoms,
#        pseudopotentials = pseudopotentials
#        )
#
#    if system!=None:
#        pw.incorporate_system(system)
#    #end if
#
#    overwrite_kpoints = kpoints!=None or system==None
#    if kpoints==None:
#        kpoints = array([[0.,0,0]])
#    else:
#        kpoints = array(kpoints)
#    #end if
#    if weights==None:
#        weights = ones((len(kpoints),),dtype=float)
#    #end if
#    if overwrite_kpoints:
#        pw.k_points.clear()
#        pw.k_points.set(
#            specifier = 'tpiba',
#            kpoints   = kpoints,
#            weights   = weights
#            )
#    #end if
#
#    return pw
##end def generate_nscf_input
