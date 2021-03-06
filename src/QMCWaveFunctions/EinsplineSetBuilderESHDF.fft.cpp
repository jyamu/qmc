//////////////////////////////////////////////////////////////////
// (c) Copyright 2003-  by Ken Esler and Jeongnim Kim           //
//////////////////////////////////////////////////////////////////
//   National Center for Supercomputing Applications &          //
//   Materials Computation Center                               //
//   University of Illinois, Urbana-Champaign                   //
//   Urbana, IL 61801                                           //
//   e-mail: jnkim@ncsa.uiuc.edu                                //
//                                                              //
// Supported by                                                 //
//   National Center for Supercomputing Applications, UIUC      //
//   Materials Computation Center, UIUC                         //
//////////////////////////////////////////////////////////////////

#include "QMCWaveFunctions/EinsplineSetBuilder.h"
#include "QMCWaveFunctions/OrbitalBuilderBase.h"
#include "Particle/DistanceTable.h"
#include "OhmmsData/AttributeSet.h"
#include "Utilities/Timer.h"
#include "Message/Communicate.h"
#include "Message/CommOperators.h"
#include "Numerics/HDFSTLAttrib.h"
#include "OhmmsData/HDFStringAttrib.h"
#include "ParticleIO/ESHDFParticleParser.h"
#include "ParticleBase/RandomSeqGenerator.h"
#include "qmc_common.h"

namespace qmcplusplus
{

bool sortByIndex(BandInfo leftB, BandInfo rightB)
{
  if (leftB.BandIndex==rightB.BandIndex)
  {
    if  ((leftB.Energy < rightB.Energy+1e-6)&&(leftB.Energy > rightB.Energy-1e-6))
      return leftB.TwistIndex < rightB.TwistIndex;
    else
      return leftB.Energy<rightB.Energy;
  }
  else
    return (leftB.BandIndex<rightB.BandIndex);
};


bool EinsplineSetBuilder::ReadOrbitalInfo_ESHDF()
{
  update_token(__FILE__,__LINE__,"ReadOrbitalInfo_ESHDF");
  app_log() << "  Reading orbital file in ESHDF format.\n";
  HDFAttribIO<TinyVector<int,3> > h_version(Version);
  h_version.read (H5FileID, "/version");
  app_log() << "  ESHDF orbital file version "
            << Version[0] << "." << Version[1] <<"." << Version[2] << endl;
  HDFAttribIO<Tensor<double,3> > h_Lattice(Lattice);
  h_Lattice.read      (H5FileID, "/supercell/primitive_vectors");
  RecipLattice = 2.0*M_PI*inverse(Lattice);
  SuperLattice = dot(TileMatrix, Lattice);
  char buff[1000];
  snprintf (buff, 1000,
            "  Lattice = \n    [ %9.6f %9.6f %9.6f\n"
            "      %9.6f %9.6f %9.6f\n"
            "      %9.6f %9.6f %9.6f ]\n",
            Lattice(0,0), Lattice(0,1), Lattice(0,2),
            Lattice(1,0), Lattice(1,1), Lattice(1,2),
            Lattice(2,0), Lattice(2,1), Lattice(2,2));
  app_log() << buff;
  snprintf (buff, 1000,
            "  SuperLattice = \n    [ %9.6f %9.6f %9.6f\n"
            "      %9.6f %9.6f %9.6f\n"
            "      %9.6f %9.6f %9.6f ]\n",
            SuperLattice(0,0), SuperLattice(0,1), SuperLattice(0,2),
            SuperLattice(1,0), SuperLattice(1,1), SuperLattice(1,2),
            SuperLattice(2,0), SuperLattice(2,1), SuperLattice(2,2));
  CheckLattice();
  app_log() << buff;
  for (int i=0; i<3; i++)
    for (int j=0; j<3; j++)
      LatticeInv(i,j) = RecipLattice(i,j)/(2.0*M_PI);
  int have_dpsi = false;
  int NumAtomicOrbitals = 0;
  NumCoreStates = NumMuffinTins = NumTwists = NumSpins = NumBands = NumAtomicOrbitals = 0;
  //vector<int> nels_spin(2);
  //nels_spin[0]=TargetPtcl.last(0)-TargetPtcl.first(0);
  //nels_spin[1]=TargetPtcl.getTotalNum()-nels_spin[0];
  NumElectrons=TargetPtcl.getTotalNum();
  HDFAttribIO<int> h_NumBands(NumBands),
              h_NumSpins(NumSpins), h_NumTwists(NumTwists), h_NumCore(NumCoreStates),
              h_NumMuffinTins(NumMuffinTins), h_have_dpsi(have_dpsi),
              h_NumAtomicOrbitals(NumAtomicOrbitals);
  h_NumBands.read      (H5FileID, "/electrons/kpoint_0/spin_0/number_of_states");
  h_NumCore.read       (H5FileID, "/electrons/kpoint_0/spin_0/number_of_core_states");
  //h_NumElectrons.read  (H5FileID, "/electrons/number_of_electrons");
  h_NumSpins.read      (H5FileID, "/electrons/number_of_spins");
  h_NumTwists.read     (H5FileID, "/electrons/number_of_kpoints");
  h_NumMuffinTins.read (H5FileID, "/muffin_tins/number_of_tins");
  h_have_dpsi.read     (H5FileID, "/electrons/have_dpsi");
  h_NumAtomicOrbitals.read (H5FileID, "/electrons/number_of_atomic_orbitals");
  HaveOrbDerivs = have_dpsi;
  app_log() << "bands=" << NumBands << ", elecs=" << NumElectrons
            << ", spins=" << NumSpins << ", twists=" << NumTwists
            << ", muffin tins=" << NumMuffinTins
            << ", core states=" << NumCoreStates << endl;
  app_log() << "atomic orbital=" << NumAtomicOrbitals << endl;
  if (TileFactor[0]!=1 || TileFactor[1]!=1 || TileFactor[2]!=1)
    app_log() << "  Using a " << TileFactor[0] << "x" << TileFactor[1]
              << "x" << TileFactor[2] << " tiling factor.\n";
  //////////////////////////////////
  // Read ion types and locations //
  //////////////////////////////////
  Vector<int> species_ids;
  HDFAttribIO<Vector<int> > h_species_ids(species_ids);
  h_species_ids.read (H5FileID, "/atoms/species_ids");
  int num_species;
  HDFAttribIO<int> h_num_species(num_species);
  h_num_species.read (H5FileID, "/atoms/number_of_species");
  vector<int> atomic_numbers(num_species);
  for (int isp=0; isp<num_species; isp++)
  {
    ostringstream name;
    name << "/atoms/species_" << isp << "/atomic_number";
    HDFAttribIO<int> h_atomic_number (atomic_numbers[isp]);
    h_atomic_number.read(H5FileID, name.str().c_str());
  }
  IonTypes.resize(species_ids.size());
  for (int i=0; i<species_ids.size(); i++)
    IonTypes[i] = atomic_numbers[species_ids[i]];
  HDFAttribIO<Vector<TinyVector<double,3> > > h_IonPos(IonPos);
  h_IonPos.read   (H5FileID, "/atoms/positions");
  for (int i=0; i<IonTypes.size(); i++)
    app_log() << "Atom type(" << i << ") = " << IonTypes(i) << endl;
  /////////////////////////////////////
  // Read atomic orbital information //
  /////////////////////////////////////
  AtomicOrbitals.resize(NumAtomicOrbitals);
  for (int iat=0; iat<NumAtomicOrbitals; iat++)
  {
    AtomicOrbital<complex<double> > &orb = AtomicOrbitals[iat];
    int lmax, polynomial_order, spline_points;
    RealType cutoff_radius, polynomial_radius, spline_radius;
    PosType position;
    HDFAttribIO<int> h_lmax(lmax), h_polynomial_order(polynomial_order),
                h_spline_points(spline_points);
    HDFAttribIO<RealType> h_cutoff_radius(cutoff_radius),
                h_polynomial_radius(polynomial_radius),
                h_spline_radius(spline_radius);
    HDFAttribIO<PosType> h_position(position);
    ostringstream groupstream;
    groupstream << "/electrons/atomic_orbital_" << iat << "/";
    string groupname = groupstream.str();
    h_lmax.read              (H5FileID, (groupname + "lmax"             ).c_str());
    h_polynomial_order.read  (H5FileID, (groupname + "polynomial_order" ).c_str());
    h_spline_points.read     (H5FileID, (groupname + "spline_points"    ).c_str());
    h_cutoff_radius.read     (H5FileID, (groupname + "cutoff_radius"    ).c_str());
    h_polynomial_radius.read (H5FileID, (groupname + "polynomial_radius").c_str());
    h_spline_radius.read     (H5FileID, (groupname + "spline_radius"    ).c_str());
    h_position.read          (H5FileID, (groupname + "position"         ).c_str());
    orb.set_pos (position);
    orb.set_lmax (lmax);
    orb.set_cutoff (cutoff_radius);
    orb.set_spline (spline_radius, spline_points);
    orb.set_polynomial (polynomial_radius, polynomial_order);
  }
  ///////////////////////////
  // Read the twist angles //
  ///////////////////////////
  TwistAngles.resize(NumTwists);
  TwistSymmetry.resize(NumTwists);
  TwistWeight.resize(NumTwists);
  for (int ti=0; ti<NumTwists; ti++)
  {
    ostringstream path;
    path << "/electrons/kpoint_" << ti << "/reduced_k";
    HDFAttribIO<PosType> h_Twist(TwistAngles[ti]);
    h_Twist.read (H5FileID, path.str().c_str());
    if ((Version[0] >= 2) and (Version[1] >= 1))
    {
      ostringstream sym_path;
      sym_path << "/electrons/kpoint_" << ti << "/symgroup";
      HDFAttribIO<int> h_Sym(TwistSymmetry[ti]);
      h_Sym.read (H5FileID, sym_path.str().c_str());
      ostringstream nsym_path;
      nsym_path << "/electrons/kpoint_" << ti << "/numsym";
      HDFAttribIO<int> h_Nsym(TwistWeight[ti]);
      h_Nsym.read (H5FileID, nsym_path.str().c_str());
    }
    // Early versions from wfconv had wrong sign convention for
    // k-points.  EinsplineSet uses the opposite sign convention
    // from most DFT codes.
    if (Version[0] >= 2)
      for (int dim=0; dim<OHMMS_DIM; dim++)
        TwistAngles[ti][dim] *= -1.0;
    //       snprintf (buff, 1000, "  Found twist angle (%6.3f, %6.3f, %6.3f)\n",
    //           TwistAngles[ti][0], TwistAngles[ti][1], TwistAngles[ti][2]);
    //       app_log() << buff;
  }
  if(qmc_common.use_density)
  {
    //////////////////////////////////////////////////////////
    // Only if it is bulk: If the density has not been set in TargetPtcl, and   //
    // the density is available, read it in and save it     //
    // in TargetPtcl.                                       //
    //////////////////////////////////////////////////////////
    if(TargetPtcl.Lattice.SuperCellEnum == SUPERCELL_BULK)
    {
      // FIXME:  add support for more than one spin density
      if (!TargetPtcl.Density_G.size())
      {
        HDFAttribIO<vector<TinyVector<int,OHMMS_DIM> > >
        h_reduced_gvecs(TargetPtcl.DensityReducedGvecs);
        HDFAttribIO<Array<RealType,OHMMS_DIM> >
        h_density_r (TargetPtcl.Density_r);
        TinyVector<int,3> mesh;
        h_reduced_gvecs.read (H5FileID, "/electrons/density/gvectors");
        int numG = TargetPtcl.DensityReducedGvecs.size();
        // Convert primitive G-vectors to supercell G-vectors
        // Also, flip sign since ESHDF format uses opposite sign convention
        #pragma omp parallel for
        for (int iG=0; iG < numG; iG++)
          TargetPtcl.DensityReducedGvecs[iG] =
            -1 * dot(TileMatrix, TargetPtcl.DensityReducedGvecs[iG]);
        app_log() << "  Read " << numG << " density G-vectors.\n";
        for (int ispin=0; ispin<NumSpins; ispin++)
        {
          ostringstream density_r_path, density_g_path;
          density_r_path << "/electrons/density/spin_" << ispin << "/density_r";
          density_g_path << "/electrons/density/spin_" << ispin << "/density_g";
          h_density_r.read (H5FileID, density_r_path.str().c_str());
          if (TargetPtcl.DensityReducedGvecs.size())
          {
            app_log() << "  EinsplineSetBuilder found density in the HDF5 file.\n";
            vector<ComplexType> density_G;
            HDFAttribIO<vector<ComplexType > > h_density_G (density_G);
            h_density_G.read (H5FileID, density_g_path.str().c_str());
            if (!density_G.size())
            {
              app_error() << "  Density reduced G-vectors defined, but not the"
                          << " density.\n";
              abort();
            }
            else
            {
              if (ispin == 0)
                TargetPtcl.Density_G = density_G;
              else
                for (int iG=0; iG<density_G.size(); iG++)
                  TargetPtcl.Density_G[iG] += density_G[iG];
            }
          }
        }
      }
      //////////////////////////////////////////////////////////
      // If the density has not been set in TargetPtcl, and   //
      // the density is available, read it in and save it     //
      // in TargetPtcl.                                       //
      //////////////////////////////////////////////////////////
      // FIXME:  add support for more than one spin potential
      if (!TargetPtcl.VHXC_r[0].size())
      {
        HDFAttribIO<vector<TinyVector<int,OHMMS_DIM> > >
        h_reduced_gvecs(TargetPtcl.VHXCReducedGvecs);
        TinyVector<int,3> mesh;
        h_reduced_gvecs.read (H5FileID, "/electrons/VHXC/gvectors");
        int numG = TargetPtcl.VHXCReducedGvecs.size();
        // Convert primitive G-vectors to supercell G-vectors
        // Also, flip sign since ESHDF format uses opposite sign convention
        #pragma omp parallel for
        for (int iG=0; iG < numG; iG++)
          TargetPtcl.VHXCReducedGvecs[iG] =
            -1 * dot(TileMatrix, TargetPtcl.VHXCReducedGvecs[iG]);
        app_log() << "  Read " << numG << " VHXC G-vectors.\n";
        for (int ispin=0; ispin<NumSpins; ispin++)
        {
          HDFAttribIO<Array<RealType,OHMMS_DIM> >
          h_VHXC_r (TargetPtcl.VHXC_r[ispin]);
          ostringstream VHXC_r_path, VHXC_g_path;
          VHXC_r_path << "/electrons/VHXC/spin_" << ispin << "/VHXC_r";
          VHXC_g_path << "/electrons/VHXC/spin_" << ispin << "/VHXC_g";
          h_VHXC_r.read (H5FileID, VHXC_r_path.str().c_str());
          if (TargetPtcl.VHXCReducedGvecs.size())
          {
            app_log() << "  EinsplineSetBuilder found VHXC in the HDF5 file.\n";
            vector<ComplexType> VHXC_G;
            HDFAttribIO<vector<ComplexType > > h_VHXC_G (VHXC_G);
            h_VHXC_G.read (H5FileID, VHXC_g_path.str().c_str());
            if (!VHXC_G.size())
            {
              app_error() << "  VHXC reduced G-vectors defined, but not the"
                          << " VHXC.\n";
              abort();
            }
            else
              TargetPtcl.VHXC_G[ispin] = VHXC_G;
          }
        }
      }
    }
  }
  else
  {
    app_log() << "   Skip initialization of the density" << endl;
  }
  HaveLocalizedOrbs = false;
  return true;
}


void EinsplineSetBuilder::OccupyBands_ESHDF(int spin, int sortBands)
{
  update_token(__FILE__,__LINE__,"OccupyBands_ESHDF");
  if (myComm->rank() != 0)
    return;

  vector<BandInfo>& SortBands(*FullBands[spin]);
  SortBands.clear(); //??? can exit if SortBands is already made?
  int maxOrbs(0);
  for (int ti=0; ti<DistinctTwists.size(); ti++)
  {
    int tindex = DistinctTwists[ti];
    // First, read valence states
    ostringstream ePath;
    ePath << "/electrons/kpoint_" << tindex << "/spin_"
          << spin << "/eigenvalues";
    vector<double> eigvals;
    HDFAttribIO<vector<double> > h_eigvals(eigvals);
    h_eigvals.read(H5FileID, ePath.str().c_str());
    for (int bi=0; bi<NumBands; bi++)
    {
      BandInfo band;
      band.IsCoreState = false;
      band.TwistIndex = tindex;
      band.BandIndex  = bi;
      band.MakeTwoCopies = MakeTwoCopies[ti];
      band.Energy = eigvals[bi];
      if (band.Energy > -1.0e100)
        SortBands.push_back(band);
      if (MakeTwoCopies[ti])
        maxOrbs+=2;
      else
        maxOrbs++;
    }
    // Now, read core states
    for (int cs=0; cs<NumCoreStates; cs++)
    {
      BandInfo band;
      band.IsCoreState = true;
      band.TwistIndex = tindex;
      band.BandIndex  = cs;
      band.MakeTwoCopies = MakeTwoCopies[ti];
      HDFAttribIO<double> h_energy(band.Energy);
      h_energy.read   (H5FileID, (CoreStatePath(ti,cs)+"eigenvalue").c_str());
      if (band.Energy > -1.0e100)
        SortBands.push_back(band);
      if (MakeTwoCopies[ti])
        maxOrbs+=2;
      else
        maxOrbs++;
    }
  }
  // Now sort the bands by energy
  if (sortBands==2)
  {
    app_log() << "Sorting the bands by index now:\n";
    sort (SortBands.begin(), SortBands.end(), sortByIndex);
  }
  else if (sortBands==1)
  {
    app_log() << "Sorting the bands now:\n";
    sort (SortBands.begin(), SortBands.end());
  }

  vector<int> gsOcc(maxOrbs);
  int N_gs_orbs=OrbitalSet->getOrbitalSetSize();
  int nocced(0), ntoshift(0);
  for (int ti=0; ti<SortBands.size(); ti++)
  {
    if (nocced<N_gs_orbs)
    {
      if (SortBands[ti].MakeTwoCopies && (N_gs_orbs-nocced>1))
      {
        nocced+=2;
        ntoshift++;
        gsOcc[ti]=2;
      }
      else if ( (SortBands[ti].MakeTwoCopies && (N_gs_orbs-nocced==1)) || !SortBands[ti].MakeTwoCopies )
      {
        nocced+=1;
        ntoshift++;
        gsOcc[ti]=1;
      }
    }
  }
//    if(qafm!=0)
//    {
//      app_log()<<"Finding AFM pair for first "<<ntoshift<<" orbitals."<<endl;
//
//      for (int ti=0; ti<ntoshift; ti++)
//      {
//        bool found(false);
//        PosType ku = TwistAngles[SortBands[ti].TwistIndex];
//        PosType k1 = OrbitalSet->PrimLattice.k_cart(ku);
//        for (int tj=0; tj<TwistAngles.size(); tj++)
//        {
//          if(tj!=SortBands[ti].TwistIndex)
//          {
//            ku=TwistAngles[tj];
//            PosType k2 = OrbitalSet->PrimLattice.k_cart(ku);
//            double dkx = abs(k1[0] - k2[0]);
//            double dky = abs(k1[1] - k2[1]);
//            double dkz = abs(k1[2] - k2[2]);
//            bool rightK = ((dkx<qafm+0.0001)&&(dkx>qafm-0.0001)&&(dky<0.0001)&&(dkz<0.0001));
//            if(rightK)
//            {
//              SortBands[ti].TwistIndex = tj;
//              //               app_log()<<"swapping: "<<ti<<" "<<tj<<endl;
//              found=true;
//              break;
//            }
//          }
//        }
//        if(!found)
//        {
//          if((abs(k1[1])<qafm+0.0001)&&(abs(k1[1])>qafm-0.0001)) k1[1]*=-1;
//          else if((abs(k1[2])<qafm+0.0001)&&(abs(k1[2])>qafm-0.0001)) k1[2]*=-1;
//
//          for (int tj=0; tj<TwistAngles.size(); tj++)
//          {
//            if(tj!=SortBands[ti].TwistIndex)
//            {
//              ku=TwistAngles[tj];
//              PosType k2 = OrbitalSet->PrimLattice.k_cart(ku);
//              double dkx = abs(k1[0] - k2[0]);
//              double dky = abs(k1[1] - k2[1]);
//              double dkz = abs(k1[2] - k2[2]);
//              bool rightK = ((dkx<qafm+0.0001)&&(dkx>qafm-0.0001)&&(dky<0.0001)&&(dkz<0.0001));
//              if(rightK)
//              {
//                SortBands[ti].TwistIndex = tj;
//                //               app_log()<<"swapping: "<<ti<<" "<<tj<<endl;
//                found=true;
//                break;
//              }
//            }
//          }
//        }
//
//        if(!found)
//        {
//          app_log()<<"Need twist: ("<<k1[0]+qafm<<","<<k1[1]<<","<<k1[2]<<")"<<endl;
//          app_log()<<"Did not find afm pair for orbital: "<<ti<<", twist index: "<<SortBands[ti].TwistIndex<<endl;
//          APP_ABORT("EinsplineSetBuilder::OccupyBands_ESHDF");
//        }
//      }
//    }
  if (occ_format=="energy")
  {
    // To get the occupations right.
    vector<int> Removed(0,0);
    vector<int> Added(0,0);
    for(int ien=0; ien<Occ.size(); ien++)
    {
      if (Occ[ien]<0)
        Removed.push_back(-Occ[ien]);
      else if (Occ[ien]>0)
        Added.push_back(Occ[ien]);
    }
    if(Added.size()-Removed.size() != 0)
    {
      app_log()<<"need to add and remove same number of orbitals. "<< Added.size()<<" "<<Removed.size()<<endl;
      APP_ABORT("ChangedOccupations");
    }
    vector<int> DiffOcc(maxOrbs,0);
    //Probably a cleaner way to do this.
    for(int i=0; i<Removed.size(); i++)
      DiffOcc[Removed[i]-1]-=1;
    for(int i=0; i<Added.size(); i++)
      DiffOcc[Added[i]-1]+=1;
    vector<int> SumOrb(SortBands.size(),0);
    int doi(0);
    for(int i=0; i<SumOrb.size(); i++)
    {
      if(SortBands[i].MakeTwoCopies)
      {
        SumOrb[i]=  gsOcc[i]+DiffOcc[doi++];
        SumOrb[i]+= DiffOcc[doi++];
      }
      else
        SumOrb[i]=gsOcc[i]+DiffOcc[doi++];
    }
    vector<BandInfo> ReOrderedBands;
    vector<BandInfo> RejectedBands;
    for(int i=0; i<SumOrb.size(); i++)
    {
      if(SumOrb[i]==2)
      {
        SortBands[i].MakeTwoCopies=true;
        ReOrderedBands.push_back(SortBands[i]);
      }
      else if (SumOrb[i]==1)
      {
        SortBands[i].MakeTwoCopies=false;
        ReOrderedBands.push_back(SortBands[i]);
      }
      else if (SumOrb[i]==0)
      {
        SortBands[i].MakeTwoCopies=false;
        RejectedBands.push_back(SortBands[i]);
      }
      else
      {
        app_log()<<" Trying to add the same orbital ("<<i<<") less than zero or more than 2 times."<<endl;
        APP_ABORT("Sorting Excitation");
      }
    }
    ReOrderedBands.insert(ReOrderedBands.end(),RejectedBands.begin(),RejectedBands.end());
    SortBands=ReOrderedBands;
  }
  else if (occ_format=="band")
  {
    app_log()<<"  Occupying bands based on (bi,ti) data."<<endl;
    if(Occ.size() != particle_hole_pairs*4)
    {
      app_log()<<" Need Occ = pairs*4. Occ is (ti,bi) of removed, then added."<<endl;
      app_log()<<Occ.size()<<" "<<particle_hole_pairs<<endl;
      APP_ABORT("ChangedOccupations");
    }
    int cnt(0);
    for(int ien=0; ien<SortBands.size(); ien++)
    {
      if((Occ[cnt] == SortBands[ien].TwistIndex)&&(Occ[cnt+1] == SortBands[ien].BandIndex))
        if(cnt<particle_hole_pairs*2)
        {
          gsOcc[ien]-=1;
          cnt+=2;
          app_log()<<"removing orbital "<<ien<<endl;
        }
        else
        {
          gsOcc[ien]+=1;
          app_log()<<"adding orbital "<<ien<<endl;
          cnt+=2;
        }
    }
    vector<BandInfo> ReOrderedBands;
    vector<BandInfo> RejectedBands;
    for(int i=0; i<SortBands.size(); i++)
    {
      if(gsOcc[i]==2)
      {
        SortBands[i].MakeTwoCopies=true;
        ReOrderedBands.push_back(SortBands[i]);
      }
      else if (gsOcc[i]==1)
      {
        SortBands[i].MakeTwoCopies=false;
        ReOrderedBands.push_back(SortBands[i]);
      }
      else if (gsOcc[i]==0)
      {
        SortBands[i].MakeTwoCopies=false;
        RejectedBands.push_back(SortBands[i]);
      }
      else
      {
        app_log()<<" Trying to add the same orbital ("<<i<<") less than zero or more than 2 times."<<endl;
        APP_ABORT("Sorting Excitation");
      }
    }
    ReOrderedBands.insert(ReOrderedBands.end(),RejectedBands.begin(),RejectedBands.end());
    SortBands=ReOrderedBands;
  }
  //for(int sw=0;sw<Removed.size();sw++){
  //  app_log()<<" Swapping two orbitals "<<Removed[sw]<<" and "<<Added[sw]<<endl;
  //  BandInfo tempband(SortBands[Removed[sw]-1]);
  //  SortBands[Removed[sw]-1] = SortBands[Added[sw]-1];
  //  SortBands[Added[sw]-1] = tempband;
  //}
  int orbIndex = 0;
  int numOrbs = 0;
  NumValenceOrbs=0;
  NumCoreOrbs=0;
  while (numOrbs < OrbitalSet->getOrbitalSetSize())
  {
    if (SortBands[orbIndex].MakeTwoCopies)
      numOrbs += 2;
    else
      numOrbs++;
    if (SortBands[orbIndex].IsCoreState)
      NumCoreOrbs++;
    else
      NumValenceOrbs++;
    orbIndex++;
  }
  NumDistinctOrbitals = orbIndex;
  app_log() << "We will read " << NumDistinctOrbitals << " distinct orbitals.\n";
  app_log() << "There are " << NumCoreOrbs << " core states and "
            << NumValenceOrbs << " valence states.\n";
}


/** TODO: FIXME RotateBands_ESHDF need psi_r */
void EinsplineSetBuilder::RotateBands_ESHDF (int spin, EinsplineSetExtended<complex<double > >* orbitalSet)
{
  update_token(__FILE__,__LINE__,"RotateBands_ESHDF:complex");
  bool root = (myComm->rank()==0);
  if (root)
  {
    rotationMatrix.resize(0);
    rotatedOrbitals.resize(0);
    xmlNodePtr kids=XMLRoot->children;
    while(kids != NULL)
    {
      string cname((const char*)(kids->name));
      if(cname == "rotationmatrix")
        putContent(rotationMatrix,kids);
      else
        if(cname=="rotatedorbitals")
          putContent(rotatedOrbitals,kids);
      kids=kids->next;
    }
    if ((rotatedOrbitals.size()*rotatedOrbitals.size() != rotationMatrix.size()) && (rotationMatrix.size()!=0))
    {
      app_log()<<" Rotation Matrix is wrong dimension. "<<rotationMatrix.size()<<" should be "<<rotatedOrbitals.size()*rotatedOrbitals.size()<<endl;
    }
    else
      if (rotationMatrix.size()>0)
      {
        app_log()<<" Rotating between: ";
        for (int i=0; i<rotatedOrbitals.size(); i++)
          app_log()<<rotatedOrbitals[i]<<" ";
        app_log()<<endl;
        app_log()<<" Using the following rotation"<<endl;
        for (int i=0; i<rotatedOrbitals.size(); i++)
        {
          for (int j=0; j<rotatedOrbitals.size(); j++)
            app_log()<<rotationMatrix[rotatedOrbitals.size()*i+j]<<" ";
          app_log()<<endl;
        }
      }
    if ((rotationMatrix.size()>0) && (rotatedOrbitals.size()>0) )
    {
      int N = NumDistinctOrbitals;
      int num(0);
      for (int iorb=0, indx=0; iorb<N; iorb++)
      {
        num += orbitalSet->MakeTwoCopies[iorb] ? 2 : 1;
        if (num==rotatedOrbitals[indx])
        {
          rotatedOrbitals[indx]=iorb;
          indx++;
        }
      }
      //simple copy file function. make backup.
      string backupName = H5FileName+"_bkup";
      ifstream fin(H5FileName.c_str(), ios::in | ios::binary);
      ofstream fout(backupName.c_str() , ios::in); // open with this mode to check whether file exists
      //       ofstream fout(backupName.c_str(), ios::out | ios::binary);
      if (fin.fail())
      {
        // reset status flags
        fin.clear();
        cout << " source file does not exist, try it again"<<endl;
        exit( 0 );
      }
      if (!fout.fail())
      {
        fout.close();
        cout << " destination file already exists, backup completed"<<endl;
      }
      else
      {
        fout.close();
        fout.open(backupName.c_str() , ios::out | ios::binary); // change to writting mode
        int BUFFER_SIZE = 128;
        char buffer[BUFFER_SIZE];
        while (!fin.eof() )
        {
          fin.read( buffer, BUFFER_SIZE);
          if (fin.bad())
          {
            cout << "Error reading data" << endl;
            exit( 0 );
          }
          else
            fout.write(buffer, fin.gcount());
        }
      }
      fin.close();
      fout.close();
      int nx, ny, nz, bi, ti;
      vector<Array<complex<double>,3> > allRotatedSplines;
      Array<complex<double>,3> splineData;
      TinyVector<int,3> mesh;
      // Find the orbital mesh size
      HDFAttribIO<TinyVector<int,3> > h_mesh(mesh);
      h_mesh.read (H5FileID, "/electrons/psi_r_mesh");
      h_mesh.read (H5FileID, "/electrons/mesh");
      //     myComm->bcast(mesh);
      nx=mesh[0];
      ny=mesh[1];
      nz=mesh[2];
      splineData.resize(nx,ny,nz);
      vector<BandInfo>& SortBands(*FullBands[spin]);
      for (int i=0; i<rotatedOrbitals.size(); i++)
      {
        int iorb = rotatedOrbitals[i];
        int ti   = SortBands[iorb].TwistIndex;
        int bi   = SortBands[iorb].BandIndex;
        double e = SortBands[iorb].Energy;
        PosType k;
        PosType twist = TwistAngles[ti];
        k = orbitalSet->PrimLattice.k_cart(twist);
        fprintf (stderr, "  Rotating state:  ti=%3d  bi=%3d energy=%8.5f k=(%7.4f, %7.4f, %7.4f) rank=%d \n",
                 ti, bi, e, k[0], k[1], k[2], myComm->rank() );
        ostringstream path;
        path << "/electrons/kpoint_" << ti << "/spin_" << spin << "/state_" << bi << "/";
        string psirName = path.str() + "psi_r";
        HDFAttribIO<Array<complex<double>,3> >  h_splineData(splineData);
        h_splineData.read(H5FileID, psirName.c_str());
        if ((splineData.size(0) != nx) ||
            (splineData.size(1) != ny) ||
            (splineData.size(2) != nz))
        {
          fprintf (stderr, "Error in EinsplineSetBuilder::ReadBands.\n");
          fprintf (stderr, "Extended orbitals should all have the same dimensions\n");
          abort();
        }
        allRotatedSplines.push_back(splineData);
      }
      app_log()<<endl;
      vector<Array<complex<double>,3> > allOriginalSplines(allRotatedSplines);
      #pragma omp parallel for
      for (int i=0; i<rotatedOrbitals.size(); i++)
        for (int ix=0; ix<nx; ix++)
          for (int iy=0; iy<ny; iy++)
            for (int iz=0; iz<nz; iz++)
              allRotatedSplines[i](ix,iy,iz)=0.0;
      #pragma omp parallel for
      for (int i=0; i<rotatedOrbitals.size(); i++)
      {
        for(int j=0; j<rotatedOrbitals.size(); j++)
        {
          for (int ix=0; ix<nx; ix++)
            for (int iy=0; iy<ny; iy++)
              for (int iz=0; iz<nz; iz++)
                allRotatedSplines[i](ix,iy,iz) += rotationMatrix[i*rotatedOrbitals.size()+j] * allOriginalSplines[j](ix,iy,iz);
        }
      }
      for (int i=0; i<rotatedOrbitals.size(); i++)
      {
        int iorb = rotatedOrbitals[i];
        int ti   = SortBands[iorb].TwistIndex;
        int bi   = SortBands[iorb].BandIndex;
        ostringstream path;
        path << "/electrons/kpoint_" << ti << "/spin_" << spin << "/state_" << bi << "/";
        string psirName = path.str() + "psi_r";
        HDFAttribIO<Array<complex<double>,3> >  h_splineData(allRotatedSplines[i],true);
        h_splineData.write(H5FileID, psirName.c_str());
      }
      //      for (int i=0;i<rotatedOrbitals.size();i++){
      //           int iorb = rotatedOrbitals[i];
      //           int ti   = SortBands[iorb].TwistIndex;
      //           int bi   = SortBands[iorb].BandIndex;
      //
      //           ostringstream path;
      //           path << "/electrons/kpoint_" << ti << "/spin_" << spin << "/state_" << bi << "/";
      //           string psirName = path.str() + "psi_r";
      //
      //           HDFAttribIO<Array<complex<double>,3> >  h_splineData(allOriginalSplines[i]);
      //           h_splineData.read(H5FileID, psirName.c_str());
      //         }
    }
    else
      app_log()<<" No rotations defined"<<endl;
  }
}

void EinsplineSetBuilder::RotateBands_ESHDF (int spin, EinsplineSetExtended<double>* orbitalSet)
{
  update_token(__FILE__,__LINE__,"RotateBands_ESHDF:double");
  bool root = (myComm->rank()==0);
  if (root)
  {
    rotationMatrix.resize(0);
    rotatedOrbitals.resize(0);
    xmlNodePtr kids=XMLRoot->children;
    while(kids != NULL)
    {
      string cname((const char*)(kids->name));
      if(cname == "rotationmatrix")
        putContent(rotationMatrix,kids);
      else
        if(cname=="rotatedorbitals")
          putContent(rotatedOrbitals,kids);
      kids=kids->next;
    }
    if ((rotatedOrbitals.size()*rotatedOrbitals.size() != rotationMatrix.size()) && (rotationMatrix.size()!=0))
    {
      app_log()<<" Rotation Matrix is wrong dimension. "<<rotationMatrix.size()<<" should be "<<rotatedOrbitals.size()*rotatedOrbitals.size()<<endl;
    }
    else
      if (rotationMatrix.size()>0)
      {
        app_log()<<" Rotating between: ";
        for (int i=0; i<rotatedOrbitals.size(); i++)
          app_log()<<rotatedOrbitals[i]<<" ";
        app_log()<<endl;
        app_log()<<" Using the following rotation"<<endl;
        for (int i=0; i<rotatedOrbitals.size(); i++)
        {
          for (int j=0; j<rotatedOrbitals.size(); j++)
            app_log()<<rotationMatrix[rotatedOrbitals.size()*i+j]<<" ";
          app_log()<<endl;
        }
      }
    if ((rotationMatrix.size()>0) && (rotatedOrbitals.size()>0) )
    {
      int N = NumDistinctOrbitals;
      int num(0);
      for (int iorb=0, indx=0; iorb<N; iorb++)
      {
        num += orbitalSet->MakeTwoCopies[iorb] ? 2 : 1;
        if (num==rotatedOrbitals[indx])
        {
          rotatedOrbitals[indx]=iorb;
          indx++;
        }
      }
      //simple copy file function. make backup.
      string backupName = H5FileName+"_bkup";
      ifstream fin(H5FileName.c_str(), ios::in | ios::binary);
      ofstream fout(backupName.c_str() , ios::in); // open with this mode to check whether file exists
      //       ofstream fout(backupName.c_str(), ios::out | ios::binary);
      if (fin.fail())
      {
        // reset status flags
        fin.clear();
        cout << " source file does not exist, try it again"<<endl;
        exit( 0 );
      }
      if (!fout.fail())
      {
        fout.close();
        cout << " destination file already exists, backup completed"<<endl;
      }
      else
      {
        fout.close();
        fout.open(backupName.c_str() , ios::out | ios::binary); // change to writting mode
        int BUFFER_SIZE = 128;
        char buffer[BUFFER_SIZE];
        while (!fin.eof() )
        {
          fin.read( buffer, BUFFER_SIZE);
          if (fin.bad())
          {
            cout << "Error reading data" << endl;
            exit( 0 );
          }
          else
            fout.write(buffer, fin.gcount());
        }
      }
      fin.close();
      fout.close();
      int nx, ny, nz, bi, ti;
      vector<Array<complex<double>,3> > allRotatedSplines;
      Array<complex<double>,3> splineData;
      TinyVector<int,3> mesh;
      // Find the orbital mesh size
      HDFAttribIO<TinyVector<int,3> > h_mesh(mesh);
      h_mesh.read (H5FileID, "/electrons/psi_r_mesh");
      h_mesh.read (H5FileID, "/electrons/mesh");
      //     myComm->bcast(mesh);
      nx=mesh[0];
      ny=mesh[1];
      nz=mesh[2];
      splineData.resize(nx,ny,nz);
      vector<BandInfo>& SortBands(*FullBands[spin]);
      for (int i=0; i<rotatedOrbitals.size(); i++)
      {
        int iorb = rotatedOrbitals[i];
        int ti   = SortBands[iorb].TwistIndex;
        int bi   = SortBands[iorb].BandIndex;
        double e = SortBands[iorb].Energy;
        PosType k;
        PosType twist = TwistAngles[ti];
        k = orbitalSet->PrimLattice.k_cart(twist);
        fprintf (stderr, "  Rotating state:  ti=%3d  bi=%3d energy=%8.5f k=(%7.4f, %7.4f, %7.4f) rank=%d \n",
                 ti, bi, e, k[0], k[1], k[2], myComm->rank() );
        ostringstream path;
        path << "/electrons/kpoint_" << ti << "/spin_" << spin << "/state_" << bi << "/";
        string psirName = path.str() + "psi_r";
        HDFAttribIO<Array<complex<double>,3> >  h_splineData(splineData);
        h_splineData.read(H5FileID, psirName.c_str());
        if ((splineData.size(0) != nx) ||
            (splineData.size(1) != ny) ||
            (splineData.size(2) != nz))
        {
          fprintf (stderr, "Error in EinsplineSetBuilder::ReadBands.\n");
          fprintf (stderr, "Extended orbitals should all have the same dimensions\n");
          abort();
        }
        allRotatedSplines.push_back(splineData);
      }
      app_log()<<endl;
      vector<Array<complex<double>,3> > allOriginalSplines(allRotatedSplines);
      #pragma omp parallel for
      for (int i=0; i<rotatedOrbitals.size(); i++)
        for (int ix=0; ix<nx; ix++)
          for (int iy=0; iy<ny; iy++)
            for (int iz=0; iz<nz; iz++)
              allRotatedSplines[i](ix,iy,iz)=0.0;
      #pragma omp parallel for
      for (int i=0; i<rotatedOrbitals.size(); i++)
      {
        for(int j=0; j<rotatedOrbitals.size(); j++)
        {
          for (int ix=0; ix<nx; ix++)
            for (int iy=0; iy<ny; iy++)
              for (int iz=0; iz<nz; iz++)
                allRotatedSplines[i](ix,iy,iz) += rotationMatrix[i*rotatedOrbitals.size()+j] * allOriginalSplines[j](ix,iy,iz);
        }
      }
      for (int i=0; i<rotatedOrbitals.size(); i++)
      {
        int iorb = rotatedOrbitals[i];
        int ti   = SortBands[iorb].TwistIndex;
        int bi   = SortBands[iorb].BandIndex;
        ostringstream path;
        path << "/electrons/kpoint_" << ti << "/spin_" << spin << "/state_" << bi << "/";
        string psirName = path.str() + "psi_r";
        HDFAttribIO<Array<complex<double>,3> >  h_splineData(allRotatedSplines[i],true);
        h_splineData.write(H5FileID, psirName.c_str());
      }
      //      for (int i=0;i<rotatedOrbitals.size();i++){
      //           int iorb = rotatedOrbitals[i];
      //           int ti   = SortBands[iorb].TwistIndex;
      //           int bi   = SortBands[iorb].BandIndex;
      //
      //           ostringstream path;
      //           path << "/electrons/kpoint_" << ti << "/spin_" << spin << "/state_" << bi << "/";
      //           string psirName = path.str() + "psi_r";
      //
      //           HDFAttribIO<Array<complex<double>,3> >  h_splineData(allOriginalSplines[i]);
      //           h_splineData.read(H5FileID, psirName.c_str());
      //         }
    }
    else
      app_log()<<" No rotations defined"<<endl;
  }
}
}

/***************************************************************************
 * $RCSfile$   $Author: jmcminis $
 * $Revision: 5343 $   $Date: 2011-08-18 21:44:30 -0400 (Thu, 18 Aug 2011) $
 * $Id: EinsplineSetBuilderESHDF.cpp 5343 2011-08-19 01:44:30Z jmcminis $
 ***************************************************************************/
