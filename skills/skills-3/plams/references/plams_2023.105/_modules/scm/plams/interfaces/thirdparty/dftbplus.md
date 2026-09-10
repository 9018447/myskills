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
  * scm.plams.interfaces.thirdparty.dftbplus

# Source code for scm.plams.interfaces.thirdparty.dftbplus
[code]
    """
    Run DFTB+ with plams
    contributed by Patrick Melix
    based on code from Michal Handzlik
    
    see documentation for an example
    """
    from os.path import join as opj
    
    from ...core.basejob import SingleJob
    from ...core.settings import Settings
    from ...core.results import Results
    from ...tools.units import Units
    from ...core.errors import MoleculeError
    from ...mol.molecule import Molecule
    
    __all__ = ['DFTBPlusJob', 'DFTBPlusResults']
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusResults)class DFTBPlusResults(Results):
        """A Class for handling DFTB+ Results."""
        _outfile = 'detailed.out'
        _xyzout = 'geo_end.xyz'
        _genout = 'geo_end.gen'
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusResults.get_molecule)    def get_molecule(self):
            """get_molecule()
            Return the molecule from the 'geo_end.gen' file. If there is an Error, try to read the 'geo_end.xyz' file.
            """
            try:
                #The .gen file contains the cell, ASE can read it
                mol = Molecule(self[self._genout], inputformat='ase')
            except MoleculeError:
                #Fallback if no ASE found
                mol = Molecule(filename=self[self._xyzout])
            except:
                mol = Molecule()
            return mol
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusResults.get_energy)    def get_energy(self, string='Total energy', unit='au'):
            """get_energy(string='Total energy', unit='au')
            Return the energy given in the output with the description *string*, expressed in *unit*. Defaults to ``Total energy`` and ``au``.
            """
            try:
                energy = float(self.grep_file(self._outfile, pattern=string+':')[0].split()[2])
                energy = Units.convert(energy, 'au', unit)
            except:
                energy = float('nan')
            return energy
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusResults.get_atomic_charges)    def get_atomic_charges(self):
            """get_atomic_charges()
            Returns a dictonary with atom numbers and their charges, ordering is the same as in the input.
            """
            try:
                atomic_charges = {}
                string = self.awk_file(self._outfile,script='/Net atomic charges/{do_print=1} NF==0 {do_print=0 }do_print==1 {print}')
                for line in string:
                    if string[0] == line or string[1] == line:
                        continue
                    l = line.split()
                    atomic_charges[l[0]] = float(l[1])
            except:
                atomic_charges = {}
            return atomic_charges
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusJob)class DFTBPlusJob(SingleJob):
        """A class representing a single computational job with DFTB+.
           Only supports molecular coordinates, no support for lattice yet."""
        _result_type = DFTBPlusResults
        _filenames = {'inp':'dftb_in.hsd', 'run':'$JN.run', 'out':'$JN.out', 'err': '$JN.err', 'gen': '$JN.gen'}
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusJob.get_input)    def get_input(self):
          """Transform all contents of ``setting.input`` branch into string with blocks, keys and values.
    
          Automatic handling of ``molecule`` can be disabled with ``settings.ignore_molecule = True``.
          """
          def parse(key, value, indent=''):
              if value is True:
                  value = ''
    
              ret = indent + key
              if key != '' and value != '':
                  ret += ' ='
    
              if isinstance(value, Settings):
                  if '_h' in value:
                      ret += ' ' + value['_h']
                  ret += ' {\n'
    
                  i = 1
                  while ('_'+str(i)) in value:
                      ret += parse('', value['_'+str(i)], indent+'  ')
                      i += 1
    
                  for el in value:
                      if not el.startswith('_'):
                          ret += parse(el, value[el], indent+'  ')
                  ret += indent + '}'
              else:
                  ret += ' ' + str(value)
              ret += '\n'
              return ret
    
          inp = ''
          use_molecule = ('ignore_molecule' not in self.settings) or (self.settings.ignore_molecule == False)
          if use_molecule:
              self._parsemol()
    
          for item in self.settings.input:
              inp += parse(item, self.settings.input[item])
    
          if use_molecule:
              self._removemol()
          return inp
    
        def _parsemol(self):
            #use ASE to write molecule if available
            if 'ase' in Molecule._writeformat:
                filename = opj(self.path, self._filename('gen'))
                self.molecule.write(filename, outputformat='ase', format='gen')
                self.settings.input.geometry._h = 'GenFormat'
                self.settings.input.geometry._1 = '<<< '+self._filename('gen')
    
            else:
                #Old way of handling gen-format ourselves, delete if ASE becomes obligatory
                atom_types = {}
                n = 1
                atoms_line = ''
                for atom in self.molecule:
                    if atom.symbol not in atom_types:
                        atoms_line += atom.symbol + ' '
                        atom_types[atom.symbol] = n
                        n += 1
    
                #check PBC
                lattice = []
                geomType = 'C'
                for vec in self.molecule.lattice:
                    if not all(isinstance(x, (int,float)) for x in vec):
                        raise ValueError("Non-Number in Lattice Vectors, not compatible with DFTBPlus")
    
                    lattice.append(vec)
                    geomType = 'S'
    
                self.settings.input.geometry._h = 'GenFormat'
                self.settings.input.geometry._1 = '%i %s'%(len(self.molecule),geomType)
                self.settings.input.geometry._2 = atoms_line
                self.settings.input.geometry._3 = ''
    
                for i,atom in enumerate(self.molecule):
                    self.settings.input.geometry['_'+str(i+4)] = ('%5i'%(i+1)) + atom.str(symbol=str(atom_types[atom.symbol]))
    
                if len(vec) > 0:
                    j = i + 1
                    #origin
                    self.settings.input.geometry['_'+str(j+4)] = '0.0 0.0 0.0'
                    j += 1
                    for i, vec in enumerate(lattice):
                        self.settings.input.geometry['_'+str(i+j+4)] = '%f %f %f'%(vec)
    
        def _removemol(self):
            if 'geometry' in self.settings.input:
                del self.settings.input.geometry
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusJob.get_runscript)    def get_runscript(self):
            """dftb+ has to be in your $PATH!"""
            ret = 'dftb+ '
            if self.settings.runscript.stdout_redirect:
                ret += ' >' + self._filename('out')
            ret += '\n\n'
            return ret
    
    [[docs]](../../../../../interfaces/dftbplus.html#scm.plams.interfaces.thirdparty.dftbplus.DFTBPlusJob.check)    def check(self):
            """Returns true if 'ERROR!' is not found in the output."""
            s = self.results.grep_output('ERROR!')
            return len(s) == 0
    
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
