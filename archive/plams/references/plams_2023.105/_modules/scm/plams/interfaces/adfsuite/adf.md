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
  * scm.plams.interfaces.adfsuite.adf

# Source code for scm.plams.interfaces.adfsuite.adf
[code]
    import numpy as np
    import warnings
    
    from subprocess import CalledProcessError
    
    from .scmjob import SCMJob, SCMResults
    from ...core.errors import ResultsError
    from ...core.settings import Settings
    from ...core.functions import config, log
    from ...tools.units import Units
    from ...tools.periodic_table import PT
    
    __all__ = ['ADFJob', 'ADFResults']
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults)class ADFResults(SCMResults):
        """A specialized |SCMResults| subclass for accessing the results of |ADFJob|."""
        _kfext = '.t21'
        _rename_map = {'TAPE{}'.format(i) : '$JN.t{}'.format(i) for i in range(10,100)}
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_properties)    def get_properties(self):
            """get_properties()
            Return a dictionary with all the entries from ``Properties`` section in the main KF file (``$JN.t21``).
            """
            ret = {}
            for sec,var in self._kf:
                if sec == 'Properties':
                    ret[var] = self.readkf(sec,var)
            return ret
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_main_molecule)    def get_main_molecule(self):
            """get_main_molecule()
            Return a |Molecule| instance based on the ``Geometry`` section in the main KF file (``$JN.t21``).
    
            For runs with multiple geometries (geometry optimization, transition state search, intrinsic reaction coordinate) this is the **final** geometry. In such a case, to access the initial (or any intermediate) coordinates please use :meth:`get_input_molecule` or extract coordinates from section ``History``, variables ``xyz 1``, ``xyz 2`` and so on. Mind the fact that all coordinates written by ADF to ``History`` section are in bohr and internal atom order::
    
                mol = results.get_molecule(section='History', variable='xyz 1', unit='bohr', internal=True)
            """
            return self.get_molecule(section='Geometry', variable='xyz InputOrder', unit='bohr')
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_input_molecule)    def get_input_molecule(self):
            """get_input_molecule()
            Return a |Molecule| instance with initial coordinates.
    
            All data used by this method is taken from ``$JN.t21`` file. The ``molecule`` attribute of the corresponding job is ignored.
            """
            if ('History', 'nr of geometries') in self._kf:
                return self.get_molecule(section='History', variable='xyz 1', unit='bohr', internal=True)
            return self.get_main_molecule()
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_energy)    def get_energy(self, unit='au'):
            """get_energy(unit='au')
            Return final bond energy, expressed in *unit*.
            """
            return self._get_single_value('Energy', 'Bond Energy', unit)
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_dipole_vector)    def get_dipole_vector(self, unit='au'):
            """get_dipole_vector(unit='au')
            Return the dipole vector, expressed in *unit*.
            """
            prop = self.get_properties()
            if 'Dipole' in prop:
                return Units.convert(prop['Dipole'], 'au', unit)
            raise ResultsError("'Dipole' not present in 'Properties' section of {}".format(self._kfpath()))
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_gradients)    def get_gradients(self, energy_unit='au', dist_unit='bohr', eUnit=None, lUnit=None):
            """get_gradients(energy_unit='au', dist_unit='bohr')
            Return the cartesian gradients from the 'Gradients_InputOrder' field of the 'GeoOpt' Section in the kf-file, expressed in given units. Returned value is a numpy array with shape (nAtoms,3).
            """
            if eUnit:
                log("Deprecated Keyword eUnit used in ADFResults.get_gradients, update your script! Overwriting energy_unit with the given argument.", 1)
                warnings.warn("eUnit is deprecated, use energy_unit instead.", category=DeprecationWarning)
                energy_unit = eUnit
            if lUnit:
                log("Deprecated Keyword lUnit used in ADFResults.get_gradients, update your script! Overwriting energy_unit with the given argument.", 1)
                warnings.warn("lUnit is deprecated, use dist_unit instead.", category=DeprecationWarning)
                dist_unit = lUnit
            gradients = np.array(self.readkf('GeoOpt','Gradients_InputOrder'))
            gradients.shape = (-1,3)
            gradients *= (Units.conversion_ratio('au',energy_unit) / Units.conversion_ratio('bohr',dist_unit))
            return gradients
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults._extract_hessian)    def _extract_hessian(self, section, variable, internal_order):
            """_extract_hessian(section, variable, internal_order)
            Extract Hessian from *section*/*variable* of the TAPE21 file. Reorder from internal to input order, if *internal_order* is ``True``.
            """
            hess_int = np.array(self.readkf(section, variable))
            n = int((len(hess_int)/9 + 1)**0.5)
            hess_int.shape = (3*n,3*n)
            if internal_order:
                hess_inp = np.zeros(hess_int.shape)
                mapping = self._int2inp()
                for i in range(n):
                    for j in range(n):
                        ii,jj = mapping[i]-1, mapping[j]-1
                        hess_inp[3*i:3*i+3, 3*j:3*j+3] = hess_int[3*ii:3*ii+3, 3*jj:3*jj+3]
                return hess_inp
            return hess_int
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_hessian)    def get_hessian(self):
            """get_hessian()
            Try extracting Hessian, either analytical or numerical, whichever is present in the TAPE21 file, in the input order. Returned value is a square numpy array of size 3*nAtoms.
            """
            if ('Hessian', 'Analytical Hessian') in self._kf:
                return self._extract_hessian('Hessian', 'Analytical Hessian', True)
            if ('Freq', 'Hessian_complete') in self._kf:
                return self._extract_hessian('Freq', 'Hessian_complete', True)
            raise ResultsError('auto_hessian: Hessian does not seem to be present in t21 file.')
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_energy_decomposition)    def get_energy_decomposition(self, unit='au'):
            """get_energy(unit='au')
            Return a dictionary with energy decomposition terms, expressed in *unit*.
    
            The following keys are present in the returned dictionary: ``Electrostatic``, ``Kinetic``, ``Coulomb``, ``XC``. The sum of all the values is equal to the value returned by :meth:`get_energy`.
            Note that additional contributions might be included, those are up to now: ``Dispersion``.
            """
            ret = {}
            ret['Electrostatic'] = self._get_single_value('Energy', 'Electrostatic Energy', unit)
            ret['Kinetic'] = self._get_single_value('Energy', 'Kinetic Energy', unit)
            ret['Coulomb'] = self._get_single_value('Energy', 'Elstat Interaction', unit)
            ret['XC'] = self._get_single_value('Energy', 'XC Energy', unit)
            if ('Energy', 'Dispersion Energy') in self._kf:
                ret['Dispersion'] = self._get_single_value('Energy', 'Dispersion Energy', unit)
            return ret
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_frequencies)    def get_frequencies(self, unit='cm^-1'):
            """get_frequencies(unit='cm^-1')
            Return a numpy array of vibrational frequencies, expressed in *unit*.
            """
            freqs = np.array(self.readkf('Freq', 'Frequencies'))
            return freqs * Units.conversion_ratio('cm^-1', unit)
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.get_timings)    def get_timings(self):
            """get_timings()
    
            Return a dictionary with timing statistics of the job execution. Returned dictionary contains keys ``cpu``, ``system`` and ``elapsed``. The values are corresponding timings, expressed in seconds.
            """
            last = self.grep_output(' Total Used : ')[-1].split()
            ret = {}
            ret['elapsed'] = float(last[-1])
            ret['system'] = float(last[-3])
            ret['cpu'] = float(last[-5])
            return ret
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults._atomic_numbers_input_order)    def _atomic_numbers_input_order(self):
            """_atomic_numbers_input_order()
            Return a list of atomic numbers, in the input order.
            """
            n = self.readkf('Geometry', 'nr of atoms')
            tmp = self.readkf('Geometry', 'atomtype').split()
            atomtypes = {i+1 : PT.get_atomic_number(tmp[i]) for i in range(len(tmp))}
            atomtype_idx = self.readkf('Geometry', 'fragment and atomtype index')[-n:]
            atnums = [atomtypes[i] for i in atomtype_idx]
            return self.to_input_order(atnums)
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults._int2inp)    def _int2inp(self):
            """_int2inp()
            Get mapping from the internal atom order to the input atom order.
            """
            aoi = self.readkf('Geometry', 'atom order index')
            n = len(aoi)//2
            return aoi[:n]
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.recreate_molecule)    def recreate_molecule(self):
            """Recreate the input molecule for the corresponding job based on files present in the job folder. This method is used by |load_external|.
            """
            if self._kfpresent():
                return self.get_input_molecule()
            return None
    
    [[docs]](../../../../../interfaces/adf.html#scm.plams.interfaces.adfsuite.adf.ADFResults.recreate_settings)    def recreate_settings(self):
            """Recreate the input |Settings| instance for the corresponding job based on files present in the job folder. This method is used by |load_external|.
            """
            if self._kfpresent():
                if ('General', 'Input') in self._kf:
                    tmp = self.readkf('General', 'Input')
                    user_input = '\n'.join([tmp[i:160+i].rstrip() for i in range(0,len(tmp),160)])
                else:
                    user_input = self.readkf('General', 'user input')
                try:
                    from scm.libbase import InputParser, InputError
                    inp = InputParser().to_settings('adf', user_input)
                except InputError:
                    from scm.input_parser import convert_legacy_input
                    new_input = convert_legacy_input(user_input, program='adf')
                    try:
                        inp = InputParser().to_settings('adf', new_input)
                    except:
                        log('Failed to recreate input settings from {}'.format(self._kf.path), 5)
                        return None
                except:
                    log('Failed to recreate input settings from {}'.format(self._kf.path), 5)
                    return None
    
                s = Settings()
                s.input = inp
                del s.input.atoms
                s.soft_update(config.job)
                return s
            return None
    
    class ADFJob(SCMJob):
        _result_type = ADFResults
        _command = 'adf'
    
        def _serialize_mol(self):
            for i,atom in enumerate(self.molecule):
                smb = self._atom_symbol(atom)
                suffix = ''
                if 'adf' in atom.properties and 'fragment' in atom.properties.adf:
                    suffix += 'f={fragment} '
                if 'adf' in atom.properties and 'block' in atom.properties.adf:
                    suffix += 'b={block}'
    
                self.settings.input.atoms['_'+str(i+1)] = ('{:>5}'.format(i+1)) + atom.str(symbol=smb, suffix=suffix, suffix_dict=atom.properties.adf)
    
        def _remove_mol(self):
            if 'atoms' in self.settings.input:
                del self.settings.input.atoms
    
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
