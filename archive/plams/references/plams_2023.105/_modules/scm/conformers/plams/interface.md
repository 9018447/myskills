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
  * scm.conformers.plams.interface

# Source code for scm.conformers.plams.interface
[code]
    from os.path import join as opj
    
    from scm.plams import SingleJob, Results, Molecule, KFFile, AMSJob, AMSResults, Settings, Units
    from scm.plams.core.basejob import Job
    from typing import List
    import math
    
    from ..conformers.conformers_rotamers import Conformers
    
    __all__ = ["ConformersJob", "ConformersResults"]
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults)class ConformersResults(Results):
        """
        A specialized |Results| subclass for accessing the results of ConformersJob.
        Conformers are sorted by energy, from lowest to highest.
        """
    
        rkfname = "conformers.rkf"
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.__init__)    def __init__(self, *args, **kwargs):
            Results.__init__(self, *args, **kwargs)
            self._conformers = None
            self.rkf = None
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.rkfpath)    def rkfpath(self) -> str:
            """Absolute path to the 'conformers.rkf' results file"""
            return opj(self.job.path, self.rkfname)
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.get_lowest_conformer)    def get_lowest_conformer(self) -> Molecule:
            """Return the conformer with the lowest energy"""
            return self._conformers.get_molecule(0)
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.get_conformers)    def get_conformers(self) -> List[Molecule]:
            """
            Return a list containing all conformers found.
            The conformers are sorted according to their energy, the first element being the lowest energy conformer.
            """
            return self._conformers.get_conformers()
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.get_relative_energies)    def get_relative_energies(self, unit="au") -> List[float]:
            """
            Return the relative energies of the conformers i.e. the energy of the conformer minus the energy of the lowest conformer found.
            This list is sorted according to the energy of the conformers, the first element corresponding to the lowest energy conformer.
            So, by definition, the first element will have an energy of 0.
            """
            e = self._conformers.get_energies()
            return Units.convert(e, "kcal/mol", unit)
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.get_energies)    def get_energies(self, unit="au") -> List[float]:
            """
            Return the energies of the conformers.
            This list is sorted according to the energy of the conformers, the first element corresponding to the lowest energy conformer.
            """
            e = self._conformers.get_all_energies()
            return Units.convert(e, "kcal/mol", unit)
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.get_lowest_energy)    def get_lowest_energy(self, unit="au") -> float:
            """Return the energy of the lowest-energy conformer."""
            return Units.convert(self._conformers.energies[0], "kcal/mol", unit)
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.get_boltzmann_distribution)    def get_boltzmann_distribution(self, temperature) -> List[float]:
            """
            Return the Boltzmann distribution at a given temperature: exp^(E_i/kB*temperature) / (sum_j exp^(E_j/kB*temperature)), where E_i is the energy of conformer i.
            This list is sorted according to the energy of the conformers, the first element corresponding to the lowest energy (and highest probability) conformer.
            The temperature is in Kelvin.
            """
            if temperature <= 0:
                raise ValueError(f"temperature ({temperature}) should be a positive number.")
            kB = 3.166819e-6  # Hartree / Kelvin
            weights = [math.exp(-e / (kB * temperature)) for e in self.get_relative_energies()]
            denominator = sum(weights)
            dist = [w / denominator for w in weights]
            return dist
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.__str__)    def __str__(self):
            return str(self._conformers)
    
        def get_energy_landscape(self):
            el = AMSResults.EnergyLandscape(None)
            for energy, mol in zip(self.get_energies(), self.get_conformers()):
                state = AMSResults.EnergyLandscape.State(el, None, energy, mol, 1, False)
                el._states.append(state)
            return el
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersResults.collect)    def collect(self):
            """Collect files present in the job folder.
    
            Use parent method from |Results| to get a list of all files in the results folder.
            Then instantiate ``self.rkf`` to be a |KFFile| instance for the main ``conformers.rkf`` output file.
            Also instantiate ``self._conformers`` to be a Conformers instance built from it.
    
            This method is called automatically during the final part of the job execution and there is no need to call it manually.
            """
            Results.collect(self)
    
            if self.rkfname in self.files:
                rkf_path = opj(self.job.path, self.rkfname)
                self.rkf = KFFile(rkf_path)
                self._conformers = Conformers()
                self._conformers.prepare_state(Molecule(rkf_path))
                self._conformers.read(rkf_path, reorder=False, filetype="rkf")
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersJob)class ConformersJob(SingleJob):
    
        _result_type = ConformersResults
        _command = "conformers"
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersJob.__init__)    def __init__(self, name="conformers", molecule=None, **kwargs):
            Job.__init__(self, name=name, **kwargs)
    
            if molecule is None:
                self.molecule = None
            elif isinstance(molecule, Molecule):
                self.molecule = molecule.copy()
            else:
                raise NotImplementedError("TODO: Implement multiple molecules input.")
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersJob.check)    def check(self):
            return True
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersJob.get_input)    def get_input(self):
            sett = self.settings.copy()
    
            # If there are references to ConformersResults in the settings, expand them into full paths:
            def expand_results_into_paths(s):
                for k, v in s.items():
                    if isinstance(v, Settings):
                        expand_results_into_paths(v)
                    elif isinstance(v, ConformersResults):
                        s[k] = v.rkfpath()
                    elif isinstance(v, list) and any([isinstance(x, ConformersResults) for x in v]):
                        s[k] = [x.rkfpath() if isinstance(x, ConformersResults) else x for x in v]
    
            expand_results_into_paths(sett)
    
            return AMSJob(settings=sett, molecule=self.molecule).get_input()
    
    [[docs]](../../../../interfaces/conformers.html#scm.conformers.ConformersJob.get_runscript)    def get_runscript(self):
            ret = ""
            if "preamble_lines" in self.settings.runscript:
                for line in self.settings.runscript.preamble_lines:
                    ret += f"{line}\n"
            ret += 'AMS_JOBNAME="{}" AMS_RESULTSDIR=. $AMSBIN/conformers'.format(self.name)
            if "nproc" in self.settings.runscript:
                ret += " -n {}".format(self.settings.runscript.nproc)
            ret += ' <"{}"'.format(self._filename("inp"))
            if self.settings.runscript.stdout_redirect:
                ret += ' >"{}"'.format(self._filename("out"))
            ret += "\n\n"
            return ret
    
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
