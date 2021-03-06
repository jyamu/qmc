//////////////////////////////////////////////////////////////////
// (c) Copyright 2004- by Jeongnim Kim and Jordan Vincent
//////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////
//   Jeongnim Kim
//   National Center for Supercomputing Applications &
//   Materials Computation Center
//   University of Illinois, Urbana-Champaign
//   Urbana, IL 61801
//   e-mail: jnkim@ncsa.uiuc.edu
//
// Supported by
//   National Center for Supercomputing Applications, UIUC
//   Materials Computation Center, UIUC
//////////////////////////////////////////////////////////////////
// -*- C++ -*-
/** @file HDFWalkerOuput.cpp
 * @breif definition  of HDFWalkerOuput  and other support class and functions
 */
#include "Particle/HDFWalkerOutput.h"
#include "Utilities/IteratorUtility.h"
#include "OhmmsData/FileUtility.h"
#include "HDFVersion.h"
#include <numeric>
#include <iostream>
#include <sstream>
#include <Message/Communicate.h>
#include <mpi/collectives.h>
#include <io/hdf_hyperslab.h>
#if defined(HAVE_ADIOS) && defined(ADIOS_VERIFY)
#include <adios.h>
#include "ADIOS/ADIOS_verify.h"
#endif

namespace qmcplusplus
{
/* constructor
 * @param W walkers to operate on
 * @param aroot the root file name
 * @param c communicator
 *
 * Create the HDF5 file "aroot.config.h5" for output.
 * Constructor is responsible to create a hdf5 file and create basic groups
 * so that subsequent write can utilize existing dataspaces.
 * HDF5 contains
 * - state_0
 *   -- walkers
 * - config_collection
 *   -- NumOfConfigurations current count of the configurations
 *   -- config0000 current configuration
 *   -- config#### configuration for each block
 * Other classes can add datasets as needed.
 * open/close functions are provided so that the hdf5 file is closed during
 * the life time of this object. This is necessary so that failures do not lead
 * to unclosed hdf5.
 */
HDFWalkerOutput::HDFWalkerOutput(MCWalkerConfiguration& W, const string& aroot,Communicate* c)
  : appended_blocks(0), number_of_walkers(0), currentConfigNumber(0)
  , number_of_backups(0), max_number_of_backups(4), myComm(c), RootName(aroot)
//       , fw_out(myComm)
{
  number_of_particles=W.getTotalNum();
  RemoteData.reserve(4);
  RemoteData.push_back(new BufferType);
  RemoteData.push_back(new BufferType);
  block = -1;
//     //FileName=myComm->getName()+hdf::config_ext;
//     //ConfigFileName=myComm->getName()+".storeConfig.h5";
//     string ConfigFileName=myComm->getName()+".storeConfig.h5";
//     HDFVersion cur_version;
//     int dim=OHMMS_DIM;
//     fw_out.create(ConfigFileName);
//     fw_out.write(cur_version.version,hdf::version);
//     fw_out.write(number_of_particles,"NumberElectrons");
//     fw_out.write(dim,"DIM");
}

/** Destructor writes the state of random numbers and close the file */
HDFWalkerOutput::~HDFWalkerOutput()
{
//     fw_out.close();
  delete_iter(RemoteData.begin(),RemoteData.end());
}

#ifdef HAVE_ADIOS
uint64_t HDFWalkerOutput::get_group_size(MCWalkerConfiguration& W)
{
  int walker_num =  W.getActiveWalkers();
  int particle_num = number_of_particles;
  return sizeof(int) * 4 + sizeof(OHMMS_PRECISION) * walker_num * particle_num * OHMMS_DIM;
}

bool HDFWalkerOutput::adios_checkpoint(MCWalkerConfiguration& W, int64_t adios_handle, int nblock)
{
  //Need 4 * 3 bytes for storing integers and then storage
  //for all the walkers
  if (RemoteData.empty())
    RemoteData.push_back(new BufferType);
  int walker_num =  W.getActiveWalkers();
  int particle_num = number_of_particles;
  int walker_dim_num = OHMMS_DIM;
  if(nblock > block)
  {
    //This is just another wrapper for vector
    RemoteData[0]->resize(walker_num * particle_num * walker_dim_num);
    //Copy over all the walkers into one chunk of contigous memory
    W.putConfigurations(RemoteData[0]->begin());
    block = nblock;
  }
  void* walkers = RemoteData[0]->data();
  uint64_t adios_groupsize, adios_totalsize;
  adios_groupsize = sizeof(int) * 3 + sizeof(*(RemoteData[0]->data()));
  adios_group_size (adios_handle, adios_groupsize, &adios_totalsize);
  adios_write (adios_handle, "walker_num", &walker_num);
  adios_write (adios_handle, "particle_num", &particle_num);
  int walker_size = walker_num * particle_num * walker_dim_num;
  adios_write (adios_handle, "walker_size", &walker_size);
  adios_write (adios_handle, "walkers", walkers);
  return true;
}

#ifdef ADIOS_VERIFY

void HDFWalkerOutput::adios_checkpoint_verify(MCWalkerConfiguration& W, ADIOS_FILE*fp)
{
  if (RemoteData.empty())
  {
    APP_ABORT_TRACE(__FILE__, __LINE__, "empty RemoteData. Not possible");
  }

  //RemoteData.push_back(new BufferType);
  int walker_num =  W.getActiveWalkers();
  int particle_num = number_of_particles;
  int walker_dim_num = OHMMS_DIM;
  //RemoteData[0]->resize(walker_num * particle_num * walker_dim_num);
  //W.putConfigurations(RemoteData[0]->begin());
  void* walkers = RemoteData[0]->data();
  IO_VERIFY::adios_checkpoint_verify_variables(fp, "walker_num", &walker_num);
  IO_VERIFY::adios_checkpoint_verify_variables(fp, "particle_num", &particle_num);
  int walker_size = walker_num * particle_num * walker_dim_num;
  IO_VERIFY::adios_checkpoint_verify_variables(fp, "walker_size", &walker_size);
  IO_VERIFY::adios_checkpoint_verify_local_variables(fp, "walkers", (OHMMS_PRECISION *)walkers);
}
#endif
#endif


/** Write the set of walker configurations to the HDF5 file.
 * @param W set of walker configurations
 *
 * Dump is for restart and do not preserve the file
 * - version
 * - state_0
 *  - block (int)
 *  - number_of_walkes (int)
 *  - walker_partition (int array)
 *  - walkers (nw,np,3)
 */
bool HDFWalkerOutput::dump(MCWalkerConfiguration& W, int nblock)
{
  string FileName=myComm->getName()+hdf::config_ext;
  //rotate files
  //if(!myComm->rank() && currentConfigNumber)
  //{
  //  ostringstream o;
  //  o<<myComm->getName()<<".b"<<(currentConfigNumber%5) << hdf::config_ext;
  //  rename(prevFile.c_str(),o.str().c_str());
  //}

  //try to use collective
  hdf_archive dump_file(myComm,true);
  dump_file.create(FileName);
  HDFVersion cur_version;
  dump_file.write(cur_version.version,hdf::version);
  dump_file.push(hdf::main_state);
  dump_file.write(nblock,"block");

  write_configuration(W,dump_file, nblock);
  dump_file.close();

  currentConfigNumber++;
  prevFile=FileName;
  return true;
}

void HDFWalkerOutput::write_configuration(MCWalkerConfiguration& W, hdf_archive& hout, int nblock)
{
  const int wb=OHMMS_DIM*number_of_particles;
  if(nblock > block)
  {
    RemoteData[0]->resize(wb*W.getActiveWalkers());
    W.putConfigurations(RemoteData[0]->begin());
    block = nblock;
  }

  hout.write(W.WalkerOffsets,"walker_partition");

  number_of_walkers=W.WalkerOffsets[myComm->size()];
  hout.write(number_of_walkers,hdf::num_walkers);

  TinyVector<int,3> gcounts(number_of_walkers,number_of_particles,OHMMS_DIM);
  //vector<int> gcounts(3);
  //gcounts[0]=number_of_walkers;
  //gcounts[1]=number_of_particles;
  //gcounts[2]=OHMMS_DIM;

  if(hout.is_collective())
  { 
    TinyVector<int,3> counts(W.getActiveWalkers(),            number_of_particles,OHMMS_DIM);
    TinyVector<int,3> offsets(W.WalkerOffsets[myComm->rank()],number_of_particles,OHMMS_DIM);
    hyperslab_proxy<BufferType,3> slab(*RemoteData[0],gcounts,counts,offsets);
    hout.write(slab,hdf::walkers);
  }
  else
  { //gaterv to the master and master writes it, could use isend/irecv
    if(myComm->size()>1)
    {
      vector<int> displ(myComm->size()), counts(myComm->size());
      for (int i=0; i<myComm->size(); ++i)
      {
        counts[i]=wb*(W.WalkerOffsets[i+1]-W.WalkerOffsets[i]);
        displ[i]=wb*W.WalkerOffsets[i];
      }
      if(!myComm->rank())
        RemoteData[1]->resize(wb*W.WalkerOffsets[myComm->size()]);
      mpi::gatherv(*myComm,*RemoteData[0],*RemoteData[1],counts,displ);
    }
    int buffer_id=(myComm->size()>1)?1:0;
    hyperslab_proxy<BufferType,3> slab(*RemoteData[buffer_id],gcounts);
    hout.write(slab,hdf::walkers);
  }
}

/*
bool HDFWalkerOutput::dump(ForwardWalkingHistoryObject& FWO)
{
//     string ConfigFileName=myComm->getName()+".storeConfig.h5";
//     fw_out.open(ConfigFileName);
//
//     if (myComm->size()==1)
//     {
//       for (int i=0; i<FWO.ForwardWalkingHistory.size(); i++ )
//       {
//         int fwdata_size=FWO.ForwardWalkingHistory[i]->size();
//         std::stringstream sstr;
//         sstr<<"Block_"<<currentConfigNumber;
//         fw_out.push(sstr.str());//open the group
//
//         vector<float> posVecs;
//         //reserve enough space
//         vector<long> IDs(fwdata_size,0);
//         vector<long> ParentIDs(fwdata_size,0);
//         vector<float>::iterator tend(posVecs.begin());
//         for (int j=0;j<fwdata_size;j++)
//         {
//           const ForwardWalkingData& fwdata(FWO(i,j));
//           IDs[j]=fwdata.ID;
//           ParentIDs[j]=fwdata.ParentID;
//           fwdata.append(posVecs);
//         }
//         fw_out.write(posVecs,"Positions");
//         fw_out.write(IDs,"WalkerID");
//         fw_out.write(ParentIDs,"ParentID");
//         fw_out.write(fwdata_size,hdf::num_walkers);
//
//         fw_out.pop();//close the group
//         ++currentConfigNumber;
//       }
//     }
// #if defined(HAVE_MPI)
//     else
//     {
//       const int n3=number_of_particles*OHMMS_DIM;
//       for (int i=0; i<FWO.ForwardWalkingHistory.size(); i++ )
//       {
//         int fwdata_size=FWO.ForwardWalkingHistory[i]->size();
//         std::stringstream sstr;
//         sstr<<"Block_"<<currentConfigNumber;
//         fw_out.push(sstr.str());//open the group
//
//         vector<int> counts(myComm->size());
//         mpi::all_gather(*myComm,fwdata_size,counts);
//
//         vector<float> posVecs;
//         //reserve space to minimize the allocation
//         posVecs.reserve(FWO.number_of_walkers*n3);
//         vector<long> myIDs(fwdata_size),pIDs(fwdata_size);
//         vector<float>::iterator tend(posVecs.begin());
//         for (int j=0;j<fwdata_size;j++)
//         {
//           const ForwardWalkingData& fwdata(FWO(i,j));
//           myIDs[j]=fwdata.ID;
//           pIDs[j]=fwdata.ParentID;
//           fwdata.append(posVecs);
//         }
//         vector<int> offsets(myComm->size()+1,0);
//         for(int i=0; i<myComm->size();++i) offsets[i+1]=offsets[i]+counts[i];
//         fwdata_size=offsets.back();
//         fw_out.write(fwdata_size,hdf::num_walkers);
//
//         vector<long> globalIDs;
//         if(myComm->rank()==0) globalIDs.resize(fwdata_size);
//
//         //collect WalkerID
//         mpi::gatherv(*myComm, myIDs, globalIDs, counts, offsets);
//         fw_out.write(globalIDs,"WalkerID");
//         //collect ParentID
//         mpi::gatherv(*myComm, pIDs, globalIDs, counts, offsets);
//         fw_out.write(globalIDs,"ParentID");
//
//         for(int i=0; i<counts.size();++i) counts[i]*=n3;
//         for(int i=0; i<offsets.size();++i) offsets[i]*=n3;
//         vector<float> gpos;
//         if(myComm->rank()==0) gpos.resize(offsets.back());
//         mpi::gatherv(*myComm, posVecs, gpos, counts, offsets);
//
//         fw_out.write(gpos,"Positions");
//
//         fw_out.pop();//close the group
//         ++currentConfigNumber;
//       }
//     }
// #endif
//     fw_out.close();
//     FWO.clearConfigsForForwardWalking();
//
    return true;
}*/

}
/***************************************************************************
 * $RCSfile$   $Author: cynthiagu $
 * $Revision: 6153 $   $Date: 2014-01-09 12:24:34 -0500 (Thu, 09 Jan 2014) $
 * $Id: HDFWalkerOutput.cpp 6153 2014-01-09 17:24:34Z cynthiagu $
 ***************************************************************************/
