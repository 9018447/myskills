[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](_static/plams_logo.png) ](index.html)

  * 

Table of contents

  * [General](general.html)
  * Introduction
    * What is PLAMS
    * What can be done with PLAMS
    * Simple example
    * What PLAMS is _not_
    * About this documentation
  * [Getting started](started.html)
  * [Components overview](components/components.html)
  * [Interfaces](interfaces/interfaces.html)
  * [Examples](examples/examples.html)
  * [Cookbook](cookbook/cookbook.html)
  * [Citations](citations.html)

  * [FAQ](FAQ.html)

__[PLAMS](index.html)

  * [Documentation](PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](index.html)/
  * Introduction

# Introduction¶

## What is PLAMS¶

PLAMS (Python Library for Automating Molecular Simulation) is a collection of tools that aims to provide powerful, flexible and easily extendable Python interface to molecular modeling programs. It takes care of input preparation, job execution, file management and output processing as well as helps with building more advanced data workflows.

Usually the daily work of a computational chemist consists of running a number of calculations. Those calculations are done using one or more molecular modeling programs like ADF, BAND, Turbomole or Dirac (we will call such programs _external binaries_). Obtaining results with one of such programs requires a series of steps. First, the subject of the problem (description of a molecular system, set of desired simulation parameters) has to be presented in the format understandable by molecular modeling program and written to an _input file_ which is usually a text file. Then the program is executed, it runs and produces _output_ which is a collection of text or binary files. That output usually contains more information than is required for a particular problem so data of interest has to be extracted and (possibly) postprocessed. That different computational tools use different input and output formats and are executed differently. In most cases many _single calculations_ need to be performed to solve the problem of interest. That requires significant effort to be put into data hygiene to avoid confusing or overwriting input and output files from distinct calculations.

Each of the above steps, apart from actual calculation done by a molecular modeling program, needs to be performed by a human. Preparing and editing text files, creating folders in the filesystem, copying files between them and reading data from output are tedious, repetitive and highly error-prone work. Some users deal with it using automation, usually in form of ad hoc shell scripts. A few programs, like Amsterdam Modeling Suite, offer graphical user interface to help with this kind of work, but again, input preparation and output examination, even though assisted with convenient tools, have to be done by a human. Quite often it turns out to be a performance bottleneck to create big automatic computational workflows, where output data of one calculation is used (usually after some processing) as an input to another calculation, sometimes done with different program on a different machine.

PLAMS was created to solve these problems. It takes responsibility of tiresome and monotonous technical details allowing you to focus on real science and your problem. It lets you do all the things mentioned above (and many more) using simple Python scripts. It gives you a helping hand with automating repetitive or complicated tasks while still leaving you with 100% control over what is really happening with your files, disks and CPUs.

## What can be done with PLAMS¶

The key design principle of PLAMS is _flexibility_. If something (and by something we mean: adjusting an input parameter, executing some program with particular options, extracting a value from output etc.) can be done by hand, it can be done with PLAMS. The internal structure of the library was designed in highly modular, object-oriented manner. Thanks to that it takes very little effort to adjust its behavior to one’s personal needs or to extend its functionality.

The most important features of PLAMS:

  * preparing, running and examining results of a molecular modeling jobs from within a single Python script

  * convenient automatic file and folder management

  * running jobs in parallel without a need to prepare a special parallel script

  * integration with popular job schedulers (OGE, SLURM, TORQUE)

  * molecular coordinates manipulation using user-friendly [`Molecule`](components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") class, supporting various formats (`xyz`, `mol`, `mol2`, `pdb`), as well as interfaces to ASE and RDKit.

  * prevention of multiple runs of the same job

  * easy data transfer between separate runs

  * efficient restarting in case of crash

  * full coverage of all input options and output data in Amsterdam Modeling Suite programs

  * easy extendable for other programs, job schedulers, file formats etc.

  * interfaces for Dirac, ORCA, CP2K, DFTB+, Crystal (and more coming soon)

## Simple example¶

To provide some real life example: here is a simple PLAMS script which calculates a potential energy curve of a diatomic system
[code] 
    import numpy as np
    
    # Calcualte bond energy of He dimers for a series of bond 
    # distances using ADF
    
    # type of atoms
    atom1 = 'He'
    atom2 = 'He'
    
    # interatomic distance values
    dmin = 2.2
    dmax = 4.2
    step = 0.2
    
    # create a list with interatomic distances
    distances = np.arange(dmin,dmax,step)
    
    # calculation parameters (single point, TZP/PBE+GrimmeD3)
    sett = Settings()
    sett.input.ams.task = 'SinglePoint'
    sett.input.adf.basis.type = 'TZP'
    sett.input.adf.xc.gga = 'PBE'
    sett.input.adf.xc.dispersion = 'Grimme3'
    
    energies = []
    for d in distances:
        mol = Molecule()
        mol.add_atom(Atom(symbol=atom1, coords=(0.0, 0.0, 0.0)))
        mol.add_atom(Atom(symbol=atom2, coords=(  d, 0.0, 0.0)))
        job = AMSJob(molecule=mol, settings=sett, name=f'dist_{d:.2f}')
        job.run()
        energies.append(job.results.get_energy(unit='kcal/mol'))
    
    # print
    print('== Results ==')
    print('d[A]    E[kcal/mol]')
    for d,e in zip(distances, energies):
        print(f'{d:.2f}    {e:.3f}')
    
[/code]

Don’t worry if something in the above code is incomprehensible or confusing. Everything you need to know to understand how PLAMS works and how to write your own scripts is explained in next chapters of this documentation.

When executed, the above script creates an uniquely named working folder, then runs 10 independent ADF single point calculations, each in a separate subfolder of the working folder. All the files created by each run are saved in the corresponding subfolder for future reference. Finally, the following table describing the potential energy curve of the He dimer is written to the standard output:
[code] 
    == Results ==
    d[A]    E[kcal/mol]
    2.20     0.230
    2.40    -0.054
    2.60    -0.127
    2.80    -0.122
    3.00    -0.094
    3.20    -0.066
    3.40    -0.045
    3.60    -0.030
    3.80    -0.020
    4.00    -0.013
    
[/code]

## What PLAMS is _not_¶

It should be stressed here that PLAMS is not a _program_ , it’s a _library_. That means it’s not a standalone tool, it doesn’t run or do anything by itself. To work properly, it needs both an external binary on one side and a properly written Python script on the other. Being a library means that PLAMS is in fact just a collection of commands and objects that can be used from within a regular Python script to perform common molecular modeling tasks.

Because of the above, PLAMS won’t take your hand and guide you, it won’t detect and warn you if you are about to do something stupid and it won’t do anything except the things you explicitly asked for. You have to understand what you are doing, you have to know how to use the binary you want PLAMS to work with and you have to have at least some basic knowledge of Python programming language.

## About this documentation¶

This documentation tries to be a combination of a tutorial and API reference. Whenever possible, discussed concepts are explained in a “know-how” manner, with example code snippets illustrating practical aspects and possible applications of a particular class or method. On the other hand, an introduction of each object is followed by a rigorous description of its semantics: attributes, methods, arguments taken etc. We believe that this way the right balance between comprehensiveness and intelligibility can be achieved.

The documentation was written keeping in mind users with various level of technical expertise, from programming newcomers to professional developers. Therefore some readers will find some parts trivial and redundant, while for others some parts will appear mysterious and incomprehensible. Please do not get discouraged by this fact, reading and understanding every single line of this document is not necessary for the majority of users.

The following special boxes appear within this documentation:

Note

Usually used to stress some important piece of information that user needs to keep in mind while using a particular object or mechanism.

Warning

Information absolutely critical for correct and secure work of the whole library. You should never violate rules given here.

Technical

More detailed technical explanation of some part of the code aimed at users with better technical background. Understanding it may require advanced Python knowledge. These parts can be safely skipped without a harm to general comprehension.

It is assumed that the reader has some basic understanding of Python programming language. Gentle introduction to Python can be found in the excellent [Python Tutorial](https://docs.python.org/3.8/tutorial/index.html#tutorial-index "\(in Python v3.8\)") and other parts of the official Python documentation.

Majority of examples presented within this document use external programs from the Amsterda Modeling Suite. Please refer to the corresponding program’s manual if some clarification is needed.

The last section presents a collection of real life example scripts that cover various possible applications of PLAMS. Due to early stage of the project this section is not yet too extensive. Users are warmly welcome to help with enriching it, as well as to provide any kind of feedback regarding either PLAMS itself or this documentation to [support@scm.com](mailto:support%40scm.com) or directly on PLAMS [GitHub page](https://github.com/SCM-NV/PLAMS).

[Next ](started.html "Getting started") [ Previous](general.html "General")

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
