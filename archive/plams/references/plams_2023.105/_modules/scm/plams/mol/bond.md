[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../../../../_static/plams_logo.png) ](../../../../index.html)

  * 

Table of contents

  * [General](../../../../general.html)
  * [Introduction](../../../../intro.html)
  * [Getting started](../../../../started.html)
  * [Components overview](../../../../components/components.html)
  * [Interfaces](../../../../interfaces/interfaces.html)
  * [Examples](../../../../examples/examples.html)
  * [Cookbook](../../../../cookbook/cookbook.html)
  * [Citations](../../../../citations.html)

  * [FAQ](../../../../FAQ.html)

__[PLAMS](../../../../index.html)

  * [Documentation](../../../../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../../../../index.html)/
  * [Module code](../../../index.html)/
  * scm.plams.mol.bond

# Source code for scm.plams.mol.bond
[code]
    import numpy as np
    
    from ..core.errors import MoleculeError
    from ..core.settings import Settings
    from ..tools.units import Units
    
    __all__ = ['Bond']
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond)class Bond:
        """A class representing a bond between two atoms.
    
        An instance of this class has the following attributes:
    
        *   ``atom1`` and ``atom2`` -- two instances of |Atom| that form this bond
        *   ``order`` -- order of the bond. It is either an integer number or the floating point value stored in ``Bond.AR``, indicating an aromatic bond
        *   ``mol`` -- |Molecule| this bond belongs to
        *   ``properties`` -- |Settings| instance storing all other  information about this bond (initially it is populated with *\*\*other*)
    
        .. note::
    
            Newly created bond is **not** added to ``atom1.bonds`` or ``atom2.bonds``. Storing information about |Bond| in |Atom| is relevant only in the context of the whole |Molecule|, so this information is updated by :meth:`~Molecule.add_bond`.
    
        """
        AR = 1.5
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.__init__)    def __init__(self, atom1=None, atom2=None, order=1, mol=None, **other):
            self.atom1 = atom1
            self.atom2 = atom2
            self.order = order
            self.mol = mol
            self.properties = Settings(other)
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.__str__)    def __str__(self):
            """Return a string representation of this bond."""
            return '({})--{:1.1f}--({})'.format(str(self.atom1).strip(), self.order, str(self.atom2).strip())
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.__iter__)    def __iter__(self):
            """Iterate over bonded atoms (``atom1`` first, then ``atom2``)."""
            yield self.atom1
            yield self.atom2
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.is_aromatic)    def is_aromatic(self):
            """Check if this bond is aromatic."""
            return self.order == Bond.AR
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.length)    def length(self, unit='angstrom'):
            """Return bond length, expressed in *unit*."""
            return self.atom1.distance_to(self.atom2, result_unit=unit)
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.as_vector)    def as_vector(self, start=None, unit='angstrom'):
            """Return a vector between two atoms that form this bond. *start* can be used to indicate which atom should be the beginning of that vector. If not specified, ``self.atom1`` is used. Returned value if a tuple of length 3, expressed in *unit*.
            """
            if start:
                if start not in self:
                    raise MoleculeError('Bond.as_vector: given atom is not a part of this bond')
                a,b = start, self.other_end(start)
            else:
                a,b = self.atom1, self.atom2
            return a.vector_to(b, result_unit=unit)
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.other_end)    def other_end(self, atom):
            """Return the atom on the other end of this bond with respect to *atom*. *atom* has to be one of the atoms forming this bond, otherwise an exception is raised.
            """
            if atom is self.atom1:
                return self.atom2
            elif atom is self.atom2:
                return self.atom1
            else:
                raise MoleculeError('Bond.other_end: invalid atom passed')
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.resize)    def resize(self, moving_atom, length, unit='angstrom'):
            """Change the length of this bond to *length* expressed in *unit* by moving *moving_atom*.
    
            *moving_atom* should be one of the atoms that form this bond. This atom is moved along the bond axis in such a way that new bond length equals *length*. If this bond is a part of a |Molecule| the whole part connected to *moving_atom* is moved.
    
            .. note::
    
                Calling this method on a bond that forms a ring within a molecule raises a |MoleculeError|.
    
            """
    
            if self.mol:
                self.mol.resize_bond(self, moving_atom, length, unit)
            else:
                bond_v = np.array(self.as_vector(start=moving_atom))
                trans_v = (1 - length/self.length(unit)) * bond_v
                moving_atom.translate(trans_v)
    
    [[docs]](../../../../components/atombond.html#scm.plams.mol.bond.Bond.rotate)    def rotate(self, moving_atom, angle, unit='radian'):
            """Rotate part of the molecule containing *moving_atom* along axis defined by this bond by an *angle* expressed in *unit*.
    
            Calling this method makes sense only if this bond is a part of a |Molecule|. *moving_atom* should be one of the atoms that form this bond and it indicates which part of the molecule is rotated. A positive value of *angle* denotes counterclockwise rotation (when looking along the bond, from the stationary part of the molecule).
    
            .. note::
    
                Calling this method on a bond that forms a ring raises a |MoleculeError|.
    
            """
            if self.mol:
                self.mol.rotate_bond(self, moving_atom, angle, unit)
    
        def has_cell_shifts(self):
            return 'suffix' in self.properties and \
                   isinstance(self.properties.suffix, str) and \
                   self.properties.suffix != '' and \
                   not self.properties.suffix.isspace()
    
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
