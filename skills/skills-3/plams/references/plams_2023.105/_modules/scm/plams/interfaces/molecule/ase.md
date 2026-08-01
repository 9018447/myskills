[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../../../../../_static/plams_logo.png) ](../../../../../index.html)

  * 

Table of contents

  * [General](../../../../../general.html)
  * [Introduction](../../../../../intro.html)
  * [Getting started](../../../../../started.html)
  * [Components overview](../../../../../components/components.html)
  * [Interfaces](../../../../../interfaces/interfaces.html)
  * [Examples](../../../../../examples/examples.html)
  * [Cookbook](../../../../../cookbook/cookbook.html)
  * [Citations](../../../../../citations.html)

  * [FAQ](../../../../../FAQ.html)

__[PLAMS](../../../../../index.html)

  * [Documentation](../../../../../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../../../../../index.html)/
  * [Module code](../../../../index.html)/
  * scm.plams.interfaces.molecule.ase

# Source code for scm.plams.interfaces.molecule.ase
[code]
    from ...core.functions import add_to_class
    from ...mol.molecule import Molecule
    from ...mol.atom import Atom
    from numpy import zeros as npz
    from numpy import array as npa
    
    __all__ = ['toASE', 'fromASE']
    ase_present = False
    
    try:
        from ase import Atom as aseAtom
        from ase import Atoms as aseAtoms
        ase_present = True
    except ImportError:
        __all__ = []
    
    @add_to_class(Molecule)
    def readase(self, f, **other):
        """Read Molecule using ASE engine
    
        The ``read`` function of the |Molecule| class passes a file descriptor into here, so in this case you must specify the *format* to be read by ASE::
    
            mol = Molecule('file.cif', inputformat='ase', format='cif')
    
        The ASE Atoms object then gets converted to a PLAMS Molecule and returned.
        All *other* options are passed to ``ASE.io.read()``.
        See https://wiki.fysik.dtu.dk/ase/ase/io/io.html on how to use it.
    
        .. note::
    
            The nomenclature of PLAMS and ASE is incompatible for reading multiple geometries, make sure that you only read single geometries with ASE! Reading multiple geometries is not supported, each geometry needs to be read individually.
    
        """
        try:
            from ase import io as aseIO
        except ImportError:
            raise MoleculeError('Asked for ASE IO engine but could not load ASE.io module')
    
        aseMol = aseIO.read(f, **other)
        mol = fromASE(aseMol)
        #update self with the molecule read without overwriting e.g. settings
        self += mol
        #lattice does not survive soft update
        self.lattice = mol.lattice
        return
    
    @add_to_class(Molecule)
    def writease(self, f, **other):
        """Write molecular coordinates using ASE engine.
    
        The ``write`` function of the |Molecule| class passes a file descriptor into here, so in this case you must specify the *format* to be written by ASE.
        All *other* options are passed to ``ASE.io.write()``.
        See https://wiki.fysik.dtu.dk/ase/ase/io/io.html on how to use it.
    
        These two write the same content to the respective files::
    
            molecule.write('filename.anyextension', outputformat='ase', format='gen')
            molecule.writease('filename.anyextension', format='gen')
    
        """
        aseMol = toASE(self)
        aseMol.write(f, **other)
        return
    
    if ase_present:
        Molecule._readformat['ase'] = Molecule.readase
        Molecule._writeformat['ase'] = Molecule.writease
    
    [[docs]](../../../../../components/mol_ase.html#scm.plams.interfaces.molecule.ase.toASE)def toASE(molecule, set_atomic_charges=False):
        """Convert a PLAMS |Molecule| to an ASE molecule (``ase.Atoms`` instance). Translate coordinates, atomic numbers, and lattice vectors (if present). The order of atoms is preserved.
        
        set_atomic_charges: bool
            If True, set_initial_charges() will be called with the average atomic charge (taken from molecule.properties.charge). The purpose is to preserve the total charge, not to set any reasonable initial charges.
        """
        aseMol = aseAtoms()
    
        #iterate over PLAMS atoms
        for atom in molecule:
    
            #check if coords only consists of floats or ints
            if not all(isinstance(x, (int,float)) for x in atom.coords):
                raise ValueError("Non-Number in Atomic Coordinates, not compatible with ASE")
    
            #append atom to aseMol
            aseMol.append(aseAtom(atom.atnum, atom.coords))
    
        #get lattice info if any
        lattice = npz((3,3))
        pbc = [False,False,False]
        for i,vec in enumerate(molecule.lattice):
    
            #check if lattice only consists of floats or ints
            if not all(isinstance(x, (int,float)) for x in vec):
                raise ValueError("Non-Number in Lattice Vectors, not compatible with ASE")
    
            pbc[i] = True
            lattice[i] = npa(vec)
    
        #save lattice info to aseMol
        if any(pbc):
            aseMol.set_pbc(pbc)
            aseMol.set_cell(lattice)
    
        if set_atomic_charges:
            charge = molecule.properties.get('charge', 0)
            if not charge:
                atomic_charges = [0.0]*len(molecule)
            else:
                atomic_charges = [float(charge)] + [0.0]*(len(molecule)-1)
    
            aseMol.set_initial_charges(atomic_charges)
    
        return aseMol
    
    [[docs]](../../../../../components/mol_ase.html#scm.plams.interfaces.molecule.ase.fromASE)def fromASE(molecule, properties=None, set_charge=False):
        """Convert an ASE molecule to a PLAMS |Molecule|. Translate coordinates, atomic numbers, and lattice vectors (if present). The order of atoms is preserved.
    
        Pass a |Settings| instance through the ``properties`` option to inherit them to the returned molecule.
        """
        plamsMol = Molecule()
    
        #iterate over ASE atoms
        for atom in molecule:
            #add atom to plamsMol
            plamsMol.add_atom(Atom(atnum=atom.number, coords=tuple(atom.position)))
    
        #add Lattice if any
        if any(molecule.get_pbc()):
            lattice = []
            #loop over three booleans
            for i,boolean in enumerate(molecule.get_pbc().tolist()):
                if boolean:
                    lattice.append(tuple(molecule.get_cell()[i]))
    
            #write lattice to plamsMol
            plamsMol.lattice = lattice.copy()
    
        if properties:
            plamsMol.properties.update(properties)
        if (properties and 'charge' not in properties or not properties) and set_charge:
            plamsMol.properties.charge = sum(molecule.get_initial_charges())
            if 'charge'  in molecule.info:
                plamsMol.properties.charge += molecule.info['charge']
        return plamsMol
    
[/code]

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
