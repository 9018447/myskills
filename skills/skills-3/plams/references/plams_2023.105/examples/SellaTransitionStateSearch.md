[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../_static/plams_logo.png) ](../index.html)

  * 

Table of contents

  * [General](../general.html)
  * [Introduction](../intro.html)
  * [Getting started](../started.html)
  * [Components overview](../components/components.html)
  * [Interfaces](../interfaces/interfaces.html)
  * [Examples](examples.html)
    * [Getting Started](examples.html#getting-started)
    * [Molecule analysis](examples.html#molecule-analysis)
    * [Benchmarks](examples.html#benchmarks)
    * [Workflows](examples.html#workflows)
    * [COSMO-RS and property prediction](examples.html#cosmo-rs-and-property-prediction)
    * [Packmol and AMS-ASE interfaces](examples.html#packmol-and-ams-ase-interfaces)
      * [Packmol example](PackMolExample/PackMolExample.html)
      * [Engine ASE: AMS geometry optimizer with forces from any ASE calculator](CustomASECalculator.html)
      * [AMSCalculator: ASE geometry optimizer with AMS forces](AMSCalculator/ASECalculator.html)
      * [AMSCalculator: Access results files & Charged systems](AMSCalculator/ChargedAMSCalculator.html)
      * [i-PI path integral MD with AMS](i-PI-AMS.html)
      * Sella transition state search with AMS
    * [ParAMS and pyZacros](examples.html#params-and-pyzacros)
    * [Other AMS calculations](examples.html#other-ams-calculations)
    * [Pymatgen](examples.html#pymatgen)
    * [Pre-made recipes](examples.html#pre-made-recipes)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * Sella transition state search with AMS

# Sella transition state search with AMS¶

**Note** : This example requires AMS2023 or later.

This example shows how to couple the [Sella](https://doi.org/10.1021/acs.jctc.2c00395) code to AMS using the AMS [ASE calculator](AMSCalculator/ASECalculator.html#asecalculatorexample).

Sella implements special algorithms and coordinate systems for performing transition state searches.

AMS also internally implements several methods. The example compares

  * Sella with AMS/ADF providing the energies and forces

  * AMS-only, where the initial hessian is calculated with DFTB and the TS search is done with ADF

For more information about Sella, refer to the Sella documentation and examples.

Technical

Sella is not included with AMS and not supported by SCM. To install it into the AMS python environment, run
[code] 
    $AMSBIN/amspython -m pip install sella
    
[/code]

**Example usage:** ([`Download SellaTransitionStateSearch.py`](../_downloads/b4fb67c63c23fa5362613ce7852457a0/SellaTransitionStateSearch.py))
[code] 
    #!/usr/bin/env amspython
    import os
    import time
    
    from ase.io import read
    from scm.plams import *
    from scm.plams.interfaces.adfsuite.ase_calculator import AMSCalculator
    from sella import Sella
    
    """
    
    This examples runs a transition state search with the Sella python package and
    compares results and timings to the builtin transition state search in AMS (using a DFTB hessian to initialize the DFT transition state search).
    
    This example requires an ADF license.
    
    """
    
    def adf_settings():
        s = Settings()
        s.input.adf.basis.type = 'DZP'
        s.input.adf.basis.core = 'None'
        s.input.adf.xc.gga = 'pbe'
        s.input.adf.symmetry = 'nosym'
        return s
    
    def run_sella(molecule):
        """ Run a TS search with Sella """
        s = adf_settings()
        s.input.ams.task = 'SinglePoint'
        s.input.ams.properties.gradients = 'Yes'
    
        atoms = toASE(molecule)
    
        if os.path.exists("sella.log"):
            os.remove("sella.log")
        if os.path.exists("sella.traj"):
            os.remove("sella.traj")
    
        with AMSCalculator(settings=s, amsworker=True) as calc:
            atoms.calc = calc
            opt = Sella(atoms, internal=True, logfile="sella.log", trajectory="sella.traj")
            opt.run(fmax=0.027, steps=50)  # 0.027 eV/ang roughly matches AMS default criterion 0.001 Ha/ang
    
        traj = read("sella.traj", ":")
        print(f"Sella converged after {len(traj)} single-point calculations")
        print(f"Final energy: {atoms.get_potential_energy()} eV")
    
        optimized_mol = fromASE(atoms)
        return optimized_mol
    
    def run_ams(molecule):
        """ Run DFT transition state search but use initial hessian calculated with DFTB """
        s = adf_settings()
        s.input.ams.task = 'TransitionStateSearch'
        s.input.ams.geometryoptimization.initialhessian.type = 'CalculateWithFastEngine'
        job = AMSJob(settings=s, molecule=molecule, name='ams_ts')
        job.run()
        print(f"AMS finished after {len(job.results.get_history_property('Energy'))} iterations")
        print(f"AMS optimized energy: {job.results.get_energy(unit='eV')} eV")
    
    def get_molecule():
        return AMSJob.from_input("""
            System
              atoms
                 C         0.049484    0.042994    0.000000
                 H        -0.068980    0.638928   -0.915972
                 H        -0.068980    0.638928    0.915972
                 H        -0.841513   -0.626342    0.000000
                 H         0.555494   -1.148227    0.000000
                 Hg        2.303289   -0.007233    0.000000
                 Cl        4.429752    0.776056    0.000000
                 Cl        1.342057   -2.676083    0.000000
              end
            End
    
        """).molecule['']
    
    def main():
        os.environ['OMP_NUM_THREADS'] = '1'
        init()
        mol = get_molecule()
    
        start = time.time()
        run_sella(mol)
        print(f"Sella finished in {time.time()-start} seconds")
    
        start = time.time()
        run_ams(mol)
        print(f"AMS finished in {time.time()-start} seconds")
    
        finish()
    
    if __name__ == '__main__':
        main()
    
[/code]

[Next ](BAND_NiO_HubbardU.html "BAND: NiO with DFT+U") [ Previous](i-PI-AMS.html "i-PI path integral MD with AMS")

* * *

  * ### Application Areas

    * [Batteries & PVs](https://www.scm.com/applications/batteries/)
    * [Bonding Analysis](https://www.scm.com/applications/chemical-bonding-analysis/)
    * [Catalysis](https://www.scm.com/applications/catalysis/)
    * [Heavy Elements](https://www.scm.com/applications/heavy-elements/)
    * [Inorganic Chemistry](https://www.scm.com/applications/inorganic-chemistry/)
    * [Life Sciences](https://www.scm.com/applications/pharma/)
    * [Materials Science](https://www.scm.com/applications/materials-science/)
    * [Nanotechnology](https://www.scm.com/applications/nanotechnology/)
    * [Oil and Gas](https://www.scm.com/applications/oil-and-gas/)
    * [Organic Electronics](https://www.scm.com/applications/organic-electronics/)
    * [Polymers](https://www.scm.com/applications/polymers/)
    * [Spectroscopy](https://www.scm.com/applications/spectroscopy/)
    * [Supercomputer / HPC](https://www.scm.com/applications/a-computing-center/)
    * [Teaching Computational Chemistry with AMS](https://www.scm.com/applications/teaching/)

  * ### Products

    * [AMS Driver](https://www.scm.com/product/ams/)
    * [ADF](https://www.scm.com/product/adf/)
    * [BAND](https://www.scm.com/product/band_periodicdft/)
    * [COSMO-RS](https://www.scm.com/product/cosmo-rs/)
    * [DFTB](https://www.scm.com/product/dftb/)
    * [GUI](https://www.scm.com/product/gui/)
    * [ML Potentials & FF](https://www.scm.com/product/machine-learning-potentials/)
    * [MOPAC](https://www.scm.com/product/mopac/)
    * [ParAMS](https://www.scm.com/product/params/)
    * [PLAMS](https://www.scm.com/product/plams/)
    * [Quantum ESPRESSO](https://www.scm.com/product/quantum-espresso/)
    * [ReaxFF](https://www.scm.com/product/reaxff/)
    * [Workflows](https://www.scm.com/product/advanced-workflows/)

  * ### Support

    * [Brochure](https://www.scm.com/amsterdam-modeling-suite/brochures/)
    * [Consulting & Contract Research](https://www.scm.com/amsterdam-modeling-suite/consulting/)
    * [Discussion List](https://www.scm.com/adf-discussion-list/)
    * [Documentation](https://www.scm.com/support/ams-tutorials-and-manuals/)
    * [Downloads](https://www.scm.com/support/downloads/)
    * [FAQs](https://www.scm.com/faq/)
    * [GUI Tutorials](https://www.scm.com/doc/Tutorials/GUI_overview/GUI_overview_tutorials.html)
    * [Installation](https://www.scm.com/support/ams-installation-videos/)
    * [Literature Highlights](https://www.scm.com/category/highlights/)
    * [Papers Citing ADF](https://www.scm.com/amsterdam-modeling-suite/research-papers-citing-adf/)
    * [Release Notes](https://www.scm.com/support/documentation-previous-versions/release-notes/)
    * [Support Overview](https://www.scm.com/support/)
    * [Teaching Materials](https://www.scm.com/support/background/amsterdam-modeling-suite-teaching-materials/)
    * [Videos](https://www.scm.com/amsterdam-modeling-suite/videos-tutorials-and-web-presentations/)
    * [Webinars](https://www.scm.com/about-us/news-agenda/web-presentations-by-adf-experts/)
    * [Workshops](https://www.scm.com/about-us/news-agenda/adf-hands-on-workshops/)

  * ### About Us

    * [Careers](https://www.scm.com/about-us/careers/)
    * [Collaborations](https://www.scm.com/about-us/collaborations/)
    * [Contact Us](https://www.scm.com/about-us/contact-us/)
    * [Contributors](https://www.scm.com/about-us/our-authors/)
    * [EU Projects](https://www.scm.com/about-us/eu-projects/)
    * [Events](https://www.scm.com/about-us/news-agenda/)
    * [Mission & Vision](https://www.scm.com/about-us/mission-vision/)
    * [News](https://www.scm.com/category/news/)
    * [Newsletters](https://www.scm.com/newsletters/)
    * [The SCM Team](https://www.scm.com/about-us/our-people/)

  * ### Pricing & Licensing

    * [License Terms](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/scm-license-terms/)
    * [Ordering](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/ordering-procedure/)
    * [Price Calculator](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/price-quote/calculate-your-price/)
    * [Price Quote](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/price-quote/)
    * [Pricing & Licensing](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/)
    * [Resellers](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/adf-resellers/)

  * [Copyright](https://www.scm.com/copyright/)
  * [Terms of Use](https://www.scm.com/terms-of-use/)
  * [Privacy Policy](https://www.scm.com/privacy-policy/)
