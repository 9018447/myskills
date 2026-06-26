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
    * [ParAMS and pyZacros](examples.html#params-and-pyzacros)
    * [Other AMS calculations](examples.html#other-ams-calculations)
      * [BAND: NiO with DFT+U](BAND_NiO_HubbardU.html)
      * [Band structure](BandStructure/BandStructure.html)
      * [AMS biased MD / PLUMED](AMSPlumedMD/AMSPlumedMD.html)
      * Quantum ESPRESSO as an AMS engine: Antiferromagnetic FeO
      * [Basic molecular dynamics analysis](BasicMDPostanalysis.html)
      * [Hybrid engine: Use lowest energy](UseLowestEnergy.html)
      * [Universal Potential: M3GNet-UP-2022](M3GNet.html)
    * [Pymatgen](examples.html#pymatgen)
    * [Pre-made recipes](examples.html#pre-made-recipes)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * Quantum ESPRESSO as an AMS engine: Antiferromagnetic FeO

# Quantum ESPRESSO as an AMS engine: Antiferromagnetic FeO¶

**Note** : This example requires AMS2023 and that you have installed Quantum ESPRESSO from the AMS package manager.

See also

[Documentation for QE in AMS](../../QuantumEspresso/general.html)

**Example usage:** ([`Download QE_AMS_AFM_HubbardU.py`](../_downloads/37ed08f77d63c66c5c0236220d13d1a3/QE_AMS_AFM_HubbardU.py))
[code] 
    #!/usr/bin/env amspython
    from scm.plams import *
    
    def main():
        init()
    
        mol = get_system()
        s = get_settings()
        
        # Note: do NOT give the job the name "quantumespresso", as that will cause file name clashes
        job = AMSJob(molecule=mol, settings=s, name='afm-FeO')
        print(job.get_input())
    
        job.run()
    
        print("Final energy (hartree)")
        print(job.results.get_energy())
    
        finish()
    
    def get_settings() -> Settings:
        s = Settings()
    
        s.runscript.preamble_lines = ['export SCM_DISABLE_MPI=1']
        #s.runscript.preamble_lines.append('export QE_STARCMD="custom_start_command"')
    
        s.input.ams.Task = 'SinglePoint'
    
        pp_dict = {
            'Fe1' : 'QE/Fe.pbe-sp-van_ak.UPF',
            'Fe2' : 'QE/Fe.pbe-sp-van_ak.UPF',
            'O'   : 'QE/O.pbe-van_ak.UPF'
        }
        # Use the ._1 syntax for unstructured blocks like Pseudopotentials
        s.input.QuantumEspresso.Pseudopotentials._1 = pseudopotentials_block(pp_dict)
    
        # Use ._h and ._1 for unstructured blocks like K_Points
        s.input.QuantumEspresso.K_Points._h = 'automatic'
        s.input.QuantumEspresso.K_Points._1 = '6 6 6 0 0 0'
    
        # Hubbard U specified in the new QE 7.1 format (different from QE 7.0)
        s.input.QuantumEspresso.Hubbard._h = 'ortho-atomic'
        s.input.QuantumEspresso.Hubbard._1 = '''
            U Fe1-3d 4.6
            U Fe2-3d 4.6
        '''
    
        # When initializing many keys inside the same block
        # it can be convenient to group them like this
        s.input.QuantumEspresso.System = Settings(
            ecutwfc = 40.0,
            ecutrho = 240.0,
            occupations = 'smearing',
            smearing = 'gaussian',
            degauss = 0.02,
            nspin = 2,
            starting_magnetization = [ 'Fe1 1.0', 'Fe2 -1.0' ]
        )
    
        # You may also just use the normal PLAMS Settings dot notation 
        s.input.QuantumEspresso.Electrons.conv_thr = 1.0e-8
        s.input.QuantumEspresso.Electrons.mixing_beta = 0.3
    
        return s
    
    def get_system() -> Molecule:
        """
    
        Returns a PLAMS Molecule for FeO with the QE.Label properties set to 'Fe1'
        and 'Fe2' for the two Fe atoms
    
        """
    
        d = 4.33
        mol = Molecule()
        mol.add_atom(Atom(symbol='Fe', coords=(0, 0, 0)))
        mol.add_atom(Atom(symbol='Fe', coords=(d/2, d/2, 0)))
        mol.add_atom(Atom(symbol='O', coords=(0, d/2, 0)))
        mol.add_atom(Atom(symbol='O', coords=(d/2, 0, 0)))
    
        mol.lattice = [[d, 0, 0], [0, d, 0], [d/2, 0, d/2]]
    
        mol[1].properties.QE.Label='Fe1'
        mol[2].properties.QE.Label='Fe2'
    
        return mol
    
    def pseudopotentials_block(pp_dict):
        """
        Transforms a dictionary to a single string
        """
    
        return "\n     ".join(f'{k} {v}' for k,v in pp_dict.items())
    
    if __name__ == '__main__':
        main()
    
[/code]

[Next ](BasicMDPostanalysis.html "Basic molecular dynamics analysis") [ Previous](AMSPlumedMD/AMSPlumedMD.html "AMS biased MD / PLUMED")

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
