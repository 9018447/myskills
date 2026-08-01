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
  * scm.plams.trajectories.xyzhistoryfile

# Source code for scm.plams.trajectories.xyzhistoryfile
[code]
    #!/usr/bin/env python
    
    import numpy
    from ..tools.periodic_table import PT
    from ..mol.molecule import Molecule
    from ..mol.atom import Atom
    from ..core.settings import Settings
    from .xyzfile import XYZTrajectoryFile
    from .xyzfile import data_from_xyzcomment
    
    __all__ = ['XYZHistoryFile']
    
    [[docs]](../../../../components/xyz.html#scm.plams.trajectories.xyzhistoryfile.XYZHistoryFile)class XYZHistoryFile (XYZTrajectoryFile) :
            """
            Class representing an XYZ file containing a molecular simulation history with varying numbers of atoms
    
            An instance of this class has the following attributes:
    
            *   ``file_object`` -- A Python :py:class:`file` object, referring to the actual XYZ file
            *   ``position``    -- The frame to which the cursor is currently pointing in the XYZ file
            *   ``mode``        -- Designates whether the file is in read or write mode ('r' or 'w')
            *   ``elements``    -- The elements of the atoms in the system at the current frame
    
            An |XYZHistoryFile| object behaves very similar to a regular file object.
            It has read and write methods (:meth:`read_next` and :meth:`write_next`) 
            that read and write from/to the position of the cursor in the ``file_object`` attribute. 
            If the file is in read mode, an additional method :meth:`read_frame` can be used that moves
            the cursor to any frame in the file and reads from there.
            The amount of information stored in memory is kept to a minimum, as only information from the current frame
            is ever stored.
    
            Reading and writing to and from the files can be done as follows::
    
                >>> from scm.plams import XYZHistoryFile
    
                >>> xyz = XYZHistoryFile('old.xyz')
                >>> mol = xyz.get_plamsmol()
    
                >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
    
                >>> for i in range(xyz.get_length()) :
                >>>     crd,cell = xyz.read_frame(i,molecule=mol)
                >>>     xyzout.write_next(molecule=mol)
    
            The above script reads information from the XYZ file ``old.xyz`` into the |Molecule| object ``mol``
            in a step-by-step manner.
            The |Molecule| object is then passed to the :meth:`write_next` method of the new |XYZHistoryFile|
            object corresponding to the new xyz file ``new.xyz``.
    
            The exact same result can also be achieved by iterating over the instance as a callable
    
                >>> xyz = XYZHistoryFile('old.xyz')
                >>> mol = xyz.get_plamsmol()
    
                >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
    
                >>> for crd,cell in xyz(mol) :
                >>>     xyzout.write_next(molecule=mol)
    
            This procedure requires all coordinate information to be passed to and from the |Molecule| object
            for each frame, which can be time-consuming.
            It is therefore also possible to bypass the |Molecule| object when reading through the frames::
    
                >>> xyz = XYZHistoryFile('old.xyz')
    
                >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
    
                >>> for crd,cell in xyz :
                >>>     xyzout.write_next(coords=crd,elements=xyz.elements)
    
            By default the write mode will create a minimal version of the XYZ file, containing only elements
            and coordinates. 
            Additional information can be written to the file by supplying additional arguments
            to the :meth:`write_next` method. 
            The additional keywords `step` and `energy` trigger the writing of a remark containing
            the molecule name, the step number, the energy, and the lattice vectors.
    
                >>> mol = Molecule('singleframe.xyz')
    
                >>> xyzout = XYZHistoryFile('new.xyz',mode='w')
                >>> xyzout.set_name('MyMol')
    
                >>> xyzout.write_next(molecule=mol, step=0, energy=5.)
            """
    
    [[docs]](../../../../components/xyz.html#scm.plams.trajectories.xyzhistoryfile.XYZHistoryFile.__init__)        def __init__ (self, filename, mode='r', fileobject=None, ntap=None) :
                    """
                    Initiates an XYZHistoryFile object
    
                    * ``filename``   -- The path to the XYZ file
                    * ``mode``       -- The mode in which to open the XYZ file ('r' or 'w')
                    * ``fileobject`` -- Optionally, a file object can be passed instead (filename needs to be set to None)
                    * ``ntap``       -- If the file is in write mode, the number of atoms can be passed here
                    """
                    XYZTrajectoryFile.__init__(self,filename,mode,fileobject,ntap)
    
                    self.input_elements = self.elements[:]
    
            def _is_endoffile (self) :
                    """
                    If the end of file is reached, return coords and cell as None
                    """
                    end = False
                    line = self.file_object.readline()
                    if len(line) == 0 :
                            end = True
                            return end
                    nats = int(line.split()[0])
                    for i in range(nats+1) :
                            line = self.file_object.readline()
                            if len(line) == 0 :
                                    end = True
                                    break
                    for i in range(self.nveclines):
                            line = self.file_object.readline()
                            if len(line) == 0 :
                                    end = True
                                    break
                    return end
    
            def _read_coordinates (self, molecule) :
                    """
                    Read the coordinates at current step
                    """
                    # Find the number of atoms
                    line = self.file_object.readline()
                    if len(line) == 0 :
                            return None, None     # End of file is reached
                    nats = int(line.split()[0])
                    line = self.file_object.readline()
    
                    # Handle the comment line
                    cell = None
                    historydata = data_from_xyzcomment(line)
                    if 'Lattice' in historydata :
                            cell = historydata['Lattice']
                            del historydata['Lattice']
                    if self.include_historydata :
                            self.historydata = historydata
    
                    # Read coordinates and elements
                    coords = []
                    elements = []
                    for i in range(nats) :
                            line = self.file_object.readline() 
                            words = line.split()
                            coords.append([float(w) for w in words[1:4]])
                            elements.append(words[0])
    
                    # If the elements changed, update the molecule
                    if elements != self.elements :
                            self.elements = elements
                            self.coords = numpy.array(coords)
                            # Rebuild the molecule (bonds will disappear for now)
                            if isinstance(molecule,Molecule) :
                                    for at in reversed(molecule.atoms) :
                                            molecule.delete_atom(at)
                                    molecule.properties = Settings()
                                    for el in elements :
                                            atom = Atom(PT.get_atomic_number(el))
                                            molecule.add_atom(atom)
                    else :
                            self.coords[:] = coords
    
                    # Possibly read lattice
                    lattice = []
                    for i in range(self.nveclines):
                            line = self.file_object.readline()
                            words = line.split()
                            lattice.append([float(w) for w in words[1:]])
                    if cell is None and len(lattice)>0:
                            cell = lattice
    
                    # Assign the data to the molecule object
                    if isinstance(molecule,Molecule) :
                            self._set_plamsmol(self.coords,cell,molecule,bonds=None)
    
                    return coords, cell
    
    [[docs]](../../../../components/xyz.html#scm.plams.trajectories.xyzhistoryfile.XYZHistoryFile.write_next)        def write_next (self,coords=None,molecule=None,elements=None,cell=[0.,0.,0.],conect=None,historydata=None) :
                    """ 
                    Write frame to next position in trajectory file
    
                    * ``coords``   -- A list or numpy array of (``ntap``,3) containing the system coordinates
                    * ``molecule`` -- A molecule object to read the molecular data from
                    * ``elements`` -- The element symbols of the atoms in the system
                    * ``cell``     -- A set of lattice vectors or cell diameters
                    * ``energy``   -- An energy value to be written to the remark line
                    * ``conect``   -- A dictionary containing connectivity info (not used)
                    * ``historydata`` -- A dictionary containing additional variables to be written to the comment line
    
                    The ``historydata`` dictionary can contain for example:
                    ('Step','Energy'), the frame number and the energy respectively
    
                    .. note::
    
                            Either ``coords`` and ``elements`` or ``molecule`` are mandatory arguments
                    """
                    if isinstance(molecule,Molecule) :
                            coords, cell, elements = self._read_plamsmol(molecule)[:3]
                    self.elements = elements
                    cell = self._convert_cell(cell)
                            
                    self._write_moldata(coords, cell, historydata)
                    
                    self.position += 1
    
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
