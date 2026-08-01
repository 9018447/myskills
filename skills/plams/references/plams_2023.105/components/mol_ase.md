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
  * [Components overview](components.html)
    * [Settings](settings.html)
    * [Jobs](jobs.html)
    * [Results](results.html)
    * [Job runners](runners.html)
    * [Job manager](jobmanager.html)
    * [Public functions](functions.html)
    * [Molecule](molecule.html)
      * [Molecule](mol_api.html)
      * [Atom](atombond.html)
      * [Bond](atombond.html#bond)
      * [RDKit interface](mol_rdkit.html)
      * ASE interface
      * [Packmol interface](mol_packmol.html)
    * [Utilities](utils.html)
    * [Trajectories](trajectories.html)
  * [Interfaces](../interfaces/interfaces.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Components overview](components.html)/
  * [Molecule](molecule.html)/
  * ASE interface

# ASE interface¶

“The Atomic Simulation Environment ([ASE](https://wiki.fysik.dtu.dk/ase)) is a set of tools and Python modules for setting up, manipulating, running, visualizing and analyzing atomistic simulations. The PLAMS interface to ASE is limited to handling [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") objects. It features access to the `ase.io` module for reading/writing [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") objects and two functions that translate PLAMS [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") objects into ASE `Atoms` objects and vice versa.

Please refer to the ASE documentation to see what can be done with ASE `Atoms` and its I/O module.

`toASE`(_molecule_ , _set_atomic_charges =False_)[[source]](../_modules/scm/plams/interfaces/molecule/ase.html#toASE)¶
    
Convert a PLAMS [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") to an ASE molecule (`ase.Atoms` instance). Translate coordinates, atomic numbers, and lattice vectors (if present). The order of atoms is preserved.

set_atomic_charges: bool
    
If True, set_initial_charges() will be called with the average atomic charge (taken from molecule.properties.charge). The purpose is to preserve the total charge, not to set any reasonable initial charges.

`fromASE`(_molecule_ , _properties =None_, _set_charge =False_)[[source]](../_modules/scm/plams/interfaces/molecule/ase.html#fromASE)¶
    
Convert an ASE molecule to a PLAMS [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"). Translate coordinates, atomic numbers, and lattice vectors (if present). The order of atoms is preserved.

Pass a [`Settings`](settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") instance through the `properties` option to inherit them to the returned molecule.

_class _`Molecule`[[source]](../_modules/scm/plams/mol/molecule.html#Molecule)¶
    
Additional reader and writer for [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") class:

`readase`(_f_ , _** other_)¶
    
Read Molecule using ASE engine

The `read` function of the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") class passes a file descriptor into here, so in this case you must specify the _format_ to be read by ASE:
[code] 
    mol = Molecule('file.cif', inputformat='ase', format='cif')
    
[/code]

The ASE Atoms object then gets converted to a PLAMS Molecule and returned. All _other_ options are passed to `ASE.io.read()`. See <https://wiki.fysik.dtu.dk/ase/ase/io/io.html> on how to use it.

Note

The nomenclature of PLAMS and ASE is incompatible for reading multiple geometries, make sure that you only read single geometries with ASE! Reading multiple geometries is not supported, each geometry needs to be read individually.

`writease`(_f_ , _** other_)¶
    
Write molecular coordinates using ASE engine.

The `write` function of the [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") class passes a file descriptor into here, so in this case you must specify the _format_ to be written by ASE. All _other_ options are passed to `ASE.io.write()`. See <https://wiki.fysik.dtu.dk/ase/ase/io/io.html> on how to use it.

These two write the same content to the respective files:
[code] 
    molecule.write('filename.anyextension', outputformat='ase', format='gen')
    molecule.writease('filename.anyextension', format='gen')
    
[/code]

[Next ](mol_packmol.html "Packmol interface") [ Previous](mol_rdkit.html "RDKit interface")

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
