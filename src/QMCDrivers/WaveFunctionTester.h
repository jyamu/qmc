//////////////////////////////////////////////////////////////////
// (c) Copyright 2003- by Jeongnim Kim
//////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////
//   Jeongnim Kim
//   National Center for Supercomputing Applications &
//   Materials Computation Center
//   University of Illinois, Urbana-Champaign
//   Urbana, IL 61801
//   e-mail: jnkim@ncsa.uiuc.edu
//   Tel:    217-244-6319 (NCSA) 217-333-3324 (MCC)
//
// Supported by
//   National Center for Supercomputing Applications, UIUC
//   Materials Computation Center, UIUC
//   Department of Physics, Ohio State University
//   Ohio Supercomputer Center
//////////////////////////////////////////////////////////////////
// -*- C++ -*-
#ifndef QMCPLUSPLUS_WAVEFUNCTIONTEST_H
#define QMCPLUSPLUS_WAVEFUNCTIONTEST_H

#include "QMCDrivers/QMCDriver.h"
#include "QMCApp/ParticleSetPool.h"
namespace qmcplusplus
{

/** Test the correctness of TrialWaveFunction for the values,
    gradients and laplacians
*/
class WaveFunctionTester: public QMCDriver
{
public:
  /// Constructor.
  WaveFunctionTester(MCWalkerConfiguration& w,
                     TrialWaveFunction& psi,
                     QMCHamiltonian& h,
                     ParticleSetPool& ptclPool,
                     WaveFunctionPool& ppool);

  ~WaveFunctionTester();

  bool run();
  bool put(xmlNodePtr q);

private:
  ParticleSetPool &PtclPool;
  ParticleSet::ParticlePos_t deltaR;
  string checkRatio, checkClone, checkHamPbyP, sourceName, wftricks, checkEloc;
  xmlNodePtr myNode;
  /// Copy Constructor (disabled)
  WaveFunctionTester(const WaveFunctionTester& a):
    QMCDriver(a), PtclPool(a.PtclPool) { }
  /// Copy Operator (disabled)
  WaveFunctionTester& operator=(const WaveFunctionTester&)
  {
    return *this;
  }
  void runRatioTest();
  void runRatioTest2();
  void runBasicTest();
  void runCloneTest();
  void runDerivTest();
  void runDerivNLPPTest();
  void runDerivCloneTest();
  void runGradSourceTest();
  void runZeroVarianceTest();
  void runwftricks();
  void runNodePlot();
  void printEloc();
  vector<RealType> Mv3(vector<vector<RealType> >& M, vector<RealType>& v);

  ofstream *fout;
};
}
#endif
/***************************************************************************
 * $RCSfile$   $Author: jnkim $
 * $Revision: 6182 $   $Date: 2014-01-22 12:03:34 -0500 (Wed, 22 Jan 2014) $
 * $Id: WaveFunctionTester.h 6182 2014-01-22 17:03:34Z jnkim $
 ***************************************************************************/
