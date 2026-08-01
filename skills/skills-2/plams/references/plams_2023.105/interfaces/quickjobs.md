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
      * [AMS driver and engines](ams.html)
      * [AMS worker](amsworker.html)
      * [ASE Calculator for AMS](amscalculator.html)
      * Quick jobs
      * [Analysis tools: Densf, FCF, analysis](postadf.html)
      * [KF files](kffiles.html)
      * [COSMO-RS](crs.html)
      * [ParAMS](params.html)
      * [Conformers](conformers.html)
      * [Zacros](zacros.html)
      * [ADF (pre-2020 version)](adf.html)
      * [ReaxFF (pre-2019 version)](reaxff.html)
    * [Other programs](thirdparty.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Interfaces](interfaces.html)/
  * [Amsterdam Modeling Suite](amssuite.html)/
  * Quick jobs

# Quick jobs¶

Quick jobs that take in a structure and return a modified structure. For example, the `preoptimize()` function lets you quickly optimize a molecule without storing any results on disk. This mimics the preoptimize function of the AMS GUI.

You can specify the `model` string as a shorthand for engine settings:

  * ‘UFF’: the UFF force field

  * ‘GFNFF’: the GFNFF force field

  * ‘ANI-2x’: The ANI-2X machine learning potential

Alternatively, you can specify `settings` which will override the model.

`preoptimize`(_molecule_ , _model ='UFF'_, _settings =None_, _nproc =1_, _maxiterations =100_)[[source]](../_modules/scm/plams/interfaces/adfsuite/quickjobs.html#preoptimize)¶
    
Returns an optimized Molecule (or list of optimized molecules)

molecule: Molecule or list of Molecules
    
Molecule to optimize

model: str
    
Shorthand for some model, e.g. ‘UFF’

settings: Settings
    
Custom engine settings (overrides `model`)

nproc: int
    
Number of processes

maxiterations: int
    
Maximum number of iterations for the geometry optimization.

`refine_density`(_molecule_ , _density_ , _step_size =50_, _model ='UFF'_, _settings =None_, _nproc =1_, _maxiterations =100_)[[source]](../_modules/scm/plams/interfaces/adfsuite/quickjobs.html#refine_density)¶
    
Performs a series of geometry optimizations with densities approaching `density`. This can be useful if you want to compress a system to a given density, but cannot just use apply_strain() (because apply_strain() also scales the bond lengths).

This function can be useful if for example packmol does not succeed to pack molecules with the desired density. Packmol can then generate a structure with a lower density, and this function can be used to increase the density to the desired value.

Returns: a Molecule with the requested density.

molecule: Molecule
    
The molecule must have a 3D lattice

density: float
    
Target density in kg/m^3 (1000x the density in g/cm^3)

step_size: float
    
Step size for the density (in kg/m^3). Set step_size to a large number to only use 1 step.

model: str
    
e.g. ‘UFF’

settings: Settings
    
Engine settings (overrides `model`)

maxiterations: int
    
maximum number of iterations for the geometry optimization.

`refine_lattice`(_molecule_ , _lattice_ , _n_points =None_, _max_strain =0.15_, _model ='UFF'_, _settings =None_, _nproc =1_, _maxiterations =10_)[[source]](../_modules/scm/plams/interfaces/adfsuite/quickjobs.html#refine_lattice)¶
    
Returns a `Molecule` for which the lattice of the `molecule` is transformed to `lattice`, by performing short geometry optimizations (each for at most `maxiterations`) on gradually distorted lattices (linearly interpolating from the original lattice to the new lattice using `n_points` points).

This can be useful for transforming an orthorhombic box of a liquid into a non-orthorhombic box of a liquid, where the gradual transformation of the lattice ensures that the molecules do not become too distorted.

If init() has been called before calling this function, the job will be run in the current PLAMS working directory and will be deleted when the job finishes.

Returns: a Molecule with the requested lattice. If the refinement fails, `None` is returned.

molecule: Molecule
    
The initial molecule

lattice: list of list of float
    
List with 1, 2, or 3 elements. Each element is a list of float with 3 elements each. For example, `lattice=[[10, 0, 0],[-5, 5, 0],[0, 0, 12]]`.

n_points: None or int >=2
    
Number of points used for the linear interpolation. If None, n_points will be chosen such that the maximum strain for any step is at most `max_strain` compared to the original lattice vector lengths.

max_strain: float
    
Only if `n_points=None`, use this value to determine the maximum allowed strain from one step to the next (as a fraction of the length of the original lattice vectors).

model: str
    
e.g. ‘UFF’

settings: Settings
    
Engine settings (overrides `model`)

nproc: int
    
Number of processes used by the job

maxiterations: int
    
maximum number of iterations for the geometry optimizations.

[Next ](postadf.html "Analysis tools: Densf, FCF, analysis") [ Previous](amscalculator.html "ASE Calculator for AMS")

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
