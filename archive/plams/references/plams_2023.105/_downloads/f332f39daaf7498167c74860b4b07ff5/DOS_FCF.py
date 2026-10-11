import os, sys
from scm.plams import *

# This is a simplified PLAMS script to calculate the density of states (DOS)
# for the transfer between two systems, in this case NO2 radical and NO2 anion
# We start from pre-optimized geometries to save time, though normally the
# geometry optimization should come first, then we calculate the frequencies
# for both systems and finally the absorption and emission FCF spectra
# and finally the DOS is calculated from the FCF spectra using the FCFDOS utility
# implemented in PLAMS

# Pre-optimized geometries
geom_1 = 'no2_1.xyz'
geom_2 = 'no2_2.xyz'

def freq(mol, common, pdir):
    """Frequency calculation"""
    # Define settings
    settings = Settings()
    settings.update(common)
    settings.input.ams.Properties.NormalModes = 'Yes'
    settings.input.adf.title = 'Vibrational frequencies'
    # Run job
    frqjob = AMSJob(molecule=mol, settings=settings, name=pdir)
    results = frqjob.run()
    return results

def fcf(job1, job2, spctype, pdir):
    """FCF Job"""
    setfcf = Settings()
    setfcf.input.spectrum.type = spctype
    setfcf.input.state1 = job1.rkfpath(file='adf')
    setfcf.input.state2 = job2.rkfpath(file='adf')
    fcfjob = FCFJob(inputjob1=job1.rkfpath(file='adf'), inputjob2=job2.rkfpath(file='adf'), settings=setfcf, name=pdir)
    results = fcfjob.run()
    return results

def main():
    init()
    # Common settings
    settings = Settings()
    settings.input.adf.symmetry = 'NoSym'
    settings.input.adf.basis.type = 'DZP'
    settings.input.adf.basis.core = 'None'
    settings.input.adf.xc.lda = 'SCF VWN'
    settings.input.ams.Task = 'SinglePoint'
    #mol1 = Molecule(filename=geom_1)
    mol1 = Molecule()
    mol1.add_atom(Atom(atnum=7, coords=(0.0, 0.0, -0.01857566)))
    mol1.add_atom(Atom(atnum=8, coords=(0.0, 1.09915770,  -0.49171967 )))
    mol1.add_atom(Atom(atnum=8, coords=(0.0,-1.09915770,  -0.49171967 )))
    #mol2 = Molecule(filename=geom_2)
    mol2 = Molecule()
    mol2.add_atom(Atom(atnum=7, coords=(0.0, 0.0, 0.12041)))
    mol2.add_atom(Atom(atnum=8, coords=(0.0, 1.070642, -0.555172)))
    mol2.add_atom(Atom(atnum=8, coords=(0.0,-1.070642, -0.555172)))
    # Acceptor vibrational frequencies calculation
    set1 = Settings()
    set1.update(settings)
    set1.input.ams.system.charge = 0
    set1.input.adf.spinpolarization = 1
    set1.input.adf.unrestricted = 'Yes'
    frq1 = freq(mol1, set1, 'gsmol1')
    # Donor vibrational frequencies calculation
    set2 = Settings()
    set2.update(settings)
    set2.input.ams.system.charge = -1
    frq2 = freq(mol2, set2, 'gsmol2')
    # FCF jobs to calculate the vibronic spectra
    fcfabs = fcf(frq1, frq2, 'absorption', 'fcfabs')
    fcfemi = fcf(frq2, frq1, 'emission', 'fcfemi')
    # DOS calculation
    job = FCFDOS(fcfabs._kf.path, fcfabs._kf.path, 10000. , 10000.)
    dos = job.dos()
    print(f'The density of states is {dos:.5e}')
    return None

main()
