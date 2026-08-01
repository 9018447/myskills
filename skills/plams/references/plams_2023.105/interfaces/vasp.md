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
  * [Interfaces](interfaces.html)
    * [Amsterdam Modeling Suite](amssuite.html)
    * [Other programs](thirdparty.html)
      * [CP2K](cp2k.html)
      * [Crystal](crystal.html)
      * [DFTB+](dftbplus.html)
      * [Dirac](dirac.html)
      * [MOPAC (standalone program)](mopac.html)
      * [ORCA](orca.html)
      * [RASPA](raspa.html)
      * VASP
        * Results
        * API
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Interfaces](interfaces.html)/
  * [Other programs](thirdparty.html)/
  * VASP

# VASP¶

(_contributed by_ [Patrick Melix](https://www.researchgate.net/profile/Patrick_Melix))

## Results¶

It is highly recommended to use the [ASE](https://wiki.fysik.dtu.dk/ase/ase/calculators/vasp.html) features for accessing the results of a `VASPJob` through the vasprun.xml. Use something like the snippet below to create a dummy ASE calculator and retrieve the results you need. Remember that ASE needs the path to the POTCARs in an environemnt variable.
[code] 
    ase_calc = Vasp(directory=str(job.path), xc='PBE') # set xc to anything, just needed for the automatisms of ASE
    ase_calc.read()
    print(ase_calc.get_potential_energy(force_consistent=False))
    forces = ase_calc.get_forces()
    ...
    
[/code]

## API¶

_class _`VASPJob`[[source]](../_modules/scm/plams/interfaces/thirdparty/vasp.html#VASPJob)¶
    
A class representing a single computational job with VASP <https://www.vasp.at/>

  * Set ‘ignore_molecule’ in `self.settings` to disable Molecule handling through ASE.

  * Set ‘ignore_potcar’ in `self.settings` to disable automatic POTCAR creation.

  * Set the path to the POTCAR files in `self.settings.input.potcar` for automatic POTCAR creation.

  * If POTCAR files not matching the element symbol should be used, give a translation dict in `self.settings.input.potcardict`.
    
E.g. {‘Fe’: ‘Fe_pv’}.

  * Settings branch `input.incar` is parsed into the INCAR file, `input.xxx` into the corresponding XXX file.

  * Use the PLAMS notation _h, _1, _2, … to obtain keywords in specific order (e.g. for the KPOINTS file).

`_result_type`¶
    
alias of `scm.plams.interfaces.thirdparty.vasp.VASPResults`

`get_input`()[[source]](../_modules/scm/plams/interfaces/thirdparty/vasp.html#VASPJob.get_input)¶
    
Transform all contents of `input` branch of `settings` into string.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/thirdparty/vasp.html#VASPJob.get_runscript)¶
    
Run VASP

Overwrite `self._command` to change the default VASP Binary.

`check`()[[source]](../_modules/scm/plams/interfaces/thirdparty/vasp.html#VASPJob.check)¶
    
Look for the normal termination line in output. Note, that does not mean your calculation was successful!

_class _`VASPResults`[[source]](../_modules/scm/plams/interfaces/thirdparty/vasp.html#VASPResults)¶
    
A class for VASP results.

`get_energy`(_index =- 1_, _unit ='a.u.'_)[[source]](../_modules/scm/plams/interfaces/thirdparty/vasp.html#VASPResults.get_energy)¶
    
Returns sigma->0 (!!!) energy without entropy.

`get_dispersion_energy`(_index =- 1_, _unit ='a.u.'_)[[source]](../_modules/scm/plams/interfaces/thirdparty/vasp.html#VASPResults.get_dispersion_energy)¶
    
Returns Edisp (eV) from the OUTCAR.

[Next ](../examples/examples.html "Examples") [ Previous](raspa.html "RASPA")

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
