#! /usr/bin/env python

import os
from optparse import OptionParser
from generic import obj



class SimTool(obj):
    
    indicators = ['setup','sent_files','submitted','finished','failed','got_output','analyzed']

    fields = set(indicators)


    def __init__(self):
        self.paths = []
        self.sims  = []
    #end def __init__


    def load(self,paths):
        for path in paths:
            sim = obj()
            sim.load(path)
            self.sims.append(sim)
            self.paths.append(path)
        #end for
    #end def load


    def write_state(self,fields=[]):
        if len(fields)==0:
            fields = self.indicators
        #end if
        forbidden = set(fields)-set(self.fields)
        if len(forbidden)>0:
            print 'unrecognized fields encountered:'
            for f in forbidden:
                print '  ',f
            #end for
            exit()
        #end if
        for i in range(len(self.paths)):
            path = self.paths[i]
            sim  = self.sims[i]
            print path
            for f in fields:
                print '   {0:<12} {1}'.format(f,int(sim[f]))
            #end for
        #end for
    #end def write_state

                
    def backup(self):
        for path in self.paths:
            base,file = os.path.split(path)
            bufile = os.path.join(base,'backup_'+file)
            os.system('cp '+path+' '+bufile)
        #end for
    #end def backup

                
    def restore(self):
        for path in self.paths:
            base,file = os.path.split(path)
            bufile = os.path.join(base,'backup_'+file)
            os.system('cp '+bufile+' '+path)
        #end for
    #end def restore


    def set_indicators(self,inds,val=1):
        if len(inds)==0:
            print 'no indicators specified'
            print '  options are: '+self.indicators
            exit()
        #end if
        forbidden = set(inds)-set(self.indicators)
        if len(forbidden)>0:
            print 'unrecognized indicators encountered:'
            for f in forbidden:
                print '  ',f
            #end for
            exit()
        #end if
        for i in range(len(self.paths)):
            path = self.paths[i]
            sim  = self.sims[i]
            for ind in inds:
                sim[ind] = val
            #end for
            sim.save(path)
        #end for
    #end def set_indicators
                
#end class SimTool


if __name__=='__main__':
    parser = OptionParser()
    (opts,inargs) = parser.parse_args()

    allowed_commands = ['show','complete','reset','set','unset','backup','restore']
    if len(inargs)==0:
        print 'simtool usage:'
        print '  allowed commands are'
        for comm in allowed_commands:
            print '   ',comm
        #end for
        exit()
    #end if

    paths = []
    command = ''
    args = []
    if len(inargs)>0:
        command = inargs[0]
        inargs=inargs[1:]
    #end if
    for arg in inargs:
        if os.path.exists(arg):
            paths.append(arg)
        else:
            args.append(arg)
        #end if
    #end for


    if not command in allowed_commands:
        print 'command '+command+' not recognized'
        exit()
    #end if

    if len(paths)==0:
        if os.path.exists('./sim.p'):
            paths = ['./sim.p']
        else:
            print 'no simulation images found'
            exit()
        #end if
    #end if

    st = SimTool()
    st.load(paths)

    if command=='show':
        st.write_state(args)
    elif command=='complete':
        inds = ['setup','sent_files','submitted','finished','got_output','analyzed']
        st.set_indicators(inds)
    elif command=='reset':
        st.set_indicators(st.indicators,val=0)
    elif command=='set':
        st.set_indicators(args)
    elif command=='unset':
        st.set_indicators(args,val=0)
    elif command=='backup':
        st.backup()
    elif command=='restore':
        st.restore()
    #end if
    
#end if
