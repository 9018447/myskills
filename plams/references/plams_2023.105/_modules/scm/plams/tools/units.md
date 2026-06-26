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
  * scm.plams.tools.units

# Source code for scm.plams.tools.units
[code]
    import collections
    import math
    import numpy as np
    
    from ..core.errors import UnitsError
    
    __all__ = ['Units']
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.units.Units)class Units:
        """A singleton class for unit converter.
    
        All values are based on `2014 CODATA recommended values <http://physics.nist.gov/cuu/Constants>`_.
    
        The following constants and units are supported:
    
        *   constants:
    
            -   ``speed_of_light`` (also ``c``)
            -   ``electron_charge`` (also ``e``)
            -   ``Avogadro_constant`` (also ``NA``)
            -   ``Bohr_radius``
    
        *   distance:
    
            -   ``Angstrom``, ``A``
            -   ``Bohr``, ``au``, ``a.u.``
            -   ``nm``
            -   ``pm``
    
        *   reciprocal distance:
    
            -   ``1/Angstrom``, ``1/A``, ``Angstrom^-1``, ``A^-1``,
            -   ``1/Bohr``, ``Bohr^-1``
    
        *   angle:
    
            -    ``degree``, ``deg``,
            -    ``radian``, ``rad``,
            -    ``grad``
            -    ``circle``
    
        *   energy:
    
            -   ``au``, ``a.u.``, ``Hartree``
            -   ``eV``
            -   ``kcal/mol``
            -   ``kJ/mol``
            -   ``cm^-1``, ``cm-1``
            -   ``K``, ``Kelvin``
    
        *   dipole moment:
    
            -   ``au``, ``a.u.``
            -   ``Cm``
            -   ``Debye``, ``D``
    
        *   forces:
    
            -   All energy units divided by angstrom or bohr, for example 
            -   ``eV/angstrom``
            -   ``hartree/bohr``
    
        *   hessian:
    
            -   All energy units divided by angstrom^2 or bohr^2, for example 
            -   ``eV/angstrom^2``
            -   ``hartree/bohr^2``
    
        *   pressure:
    
            -   All energy units divided by angstrom^3 or bohr^3, for example 
            -   ``eV/angstrom^3``
            -   ``hartree/bohr^3``
            -   And some more:
            -   ``Pa``
            -   ``GPa``
            -   ``bar``
            -   ``atm``
    
        Example::
    
            >>> print(Units.constants['speed_of_light'])
            299792458
            >>> print(Units.constants['e'])
            1.6021766208e-19
            >>> print(Units.convert(123, 'angstrom', 'bohr'))
            232.436313431
            >>> print(Units.convert([23.32, 145.0, -34.7], 'kJ/mol', 'kcal/mol'))
            [5.573613766730401, 34.655831739961755, -8.293499043977056]
            >>> print(Units.conversion_ratio('kcal/mol', 'kJ/mol'))
            4.184
    
        """
    
        constants = {}
        constants['Bohr_radius']                         =  0.529177210903  #http://physics.nist.gov/cgi-bin/cuu/Value?bohrrada0
        constants['Avogadro_constant'] = constants['NA'] =  6.022140857e23   #http://physics.nist.gov/cgi-bin/cuu/Value?na
        constants['speed_of_light'] = constants['c']     =  299792458   #http://physics.nist.gov/cgi-bin/cuu/Value?c
        constants['electron_charge'] = constants['e']    =  1.6021766208e-19   #http://physics.nist.gov/cgi-bin/cuu/Value?e
        constants['Boltzmann'] = constants['k_B'] = 1.380649e-23 #J/K
    
        distance = {}
        distance['A'] = distance['Angstrom']                 =  1.0
        distance['Bohr'] = distance['a.u.'] = distance['au'] =  1.0 / constants['Bohr_radius']
        distance['nm']                                       = distance['A'] / 10.0
        distance['pm']                                       = distance['A'] * 100.0
        distance['m']                                        = distance['A'] * 1e-10
    
        rec_distance = {}
        rec_distance['1/A'] = rec_distance['1/Ang'] = rec_distance['1/Angstrom'] = rec_distance['A^-1'] = rec_distance['Ang^-1'] = rec_distance['Angstrom^-1'] = 1.0
        rec_distance['1/m'] = rec_distance['m^-1'] = 1e10
        rec_distance['1/Bohr'] = rec_distance['Bohr^-1'] = constants['Bohr_radius']
    
        energy = {}
        energy['au'] = energy['a.u.'] = energy['Hartree'] = energy['Ha'] =  1.0
        energy['eV']                                                     =  27.211386245988   #http://physics.nist.gov/cgi-bin/cuu/Value?hrev
        energy['kJ/mol']                                                 =  4.359744650e-21 * constants['NA']  #http://physics.nist.gov/cgi-bin/cuu/Value?hrj
        energy['J']                                                      =  4.359744650e-18
        energy['kcal/mol']                                               =  energy['kJ/mol'] / 4.184
        energy['cm^-1'] = energy['cm-1']                                 =  219474.6313702   #http://physics.nist.gov/cgi-bin/cuu/Value?hrminv
        energy['K'] = energy['J'] / constants['k_B']
    
        mass = {}
        mass['au'] = mass['a.u.'] = mass['amu'] = 1.0
        mass['kg'] = 1.66053906660e-27
        mass['g'] = mass['kg'] * 1e3
    
        time = {}
        time['s']                 = 1.0
        time['ms']                = time['s'] * 1e3
        time['us']                = time['s'] * 1e6
        time['ns']                = time['s'] * 1e9
        time['ps']                = time['s'] * 1e12
        time['fs']                = time['s'] * 1e15
        time['au'] = time['a.u.'] = time['s'] / 2.4188843265857e-17 #https://physics.nist.gov/cgi-bin/cuu/Value?aut
    
        angle = {}
        angle['degree'] =  angle['deg'] = 1.0
        angle['radian'] =  angle['rad'] = math.pi / 180.0
        angle['grad']   =  100.0 / 90.0
        angle['circle'] =  1.0 / 360.0
    
        dipole = {}
        dipole['au'] = dipole['a.u.'] =  1.0
        dipole['Cm']                  =  constants['e'] * constants['Bohr_radius'] * 1e-10
        dipole['Debye'] = dipole['D'] =  dipole['Cm'] * constants['c']* 1e21
    
        forces = {}
        hessian = {}
        stress = {}
        for k,v in energy.items():
            forces[k+'/Angstrom'] = forces[k+'/Ang'] = forces[k+'/A'] = v * rec_distance['1/Angstrom']
            hessian[k+'/Angstrom^2'] = hessian[k+'/Ang^2'] = hessian[k+'/A^2'] = v  * rec_distance['1/Angstrom']**2
            stress[k+'/Angstrom^3'] = stress[k+'/Ang^3'] = stress[k+'/A^3'] = v  * rec_distance['1/Angstrom']**3
            forces[k+'/bohr'] = forces[k+'/au'] = forces[k+'/a.u.'] = v * rec_distance['1/Bohr']
            hessian[k+'/bohr^2'] = hessian[k+'/au^2'] = hessian[k+'/a.u.^2'] = v * rec_distance['1/Bohr']**2
            stress[k+'/bohr^3'] = stress[k+'/au^3'] = stress[k+'/a.u.^3'] = v * rec_distance['1/Bohr']**3
            forces[k+'/m'] = v * rec_distance['1/m']
            hessian[k+'/m^2'] = v  * rec_distance['1/m']**2
            stress[k+'/m^3'] = v  * rec_distance['1/m']**3
        forces['au'] = forces['a.u.'] = forces['Ha/bohr']
        hessian['au'] = hessian['a.u.'] = hessian['Ha/bohr^2']
        stress['au'] = stress['a.u.'] = stress['Ha/bohr^3']
        stress['Pa'] = stress['J/m^3']
        stress['GPa'] = stress['Pa'] * 1e-9
        stress['bar'] = stress['Pa'] * 1e-5
        stress['atm'] = stress['bar'] / 1.01325
    
        dicts = {}
        dicts['distance'] = distance
        dicts['energy'] = energy
        dicts['mass'] = mass
        dicts['time'] = time
        dicts['angle'] = angle
        dicts['dipole'] = dipole
        dicts['reciprocal distance'] = rec_distance
        dicts['forces'] = forces
        dicts['hessian'] = hessian
        dicts['stress'] = stress
    
        # Precompute a dict mapping lowercased unit names to quantityName:conversionFactor pairs
        quantities_for_unit = {}
        for quantity in dicts:
            for unit, factor in dicts[quantity].items():
                unit = unit.lower()
                if unit not in quantities_for_unit:
                    quantities_for_unit[unit] = {}
                quantities_for_unit[unit][quantity] = factor
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.units.Units.__init__)    def __init__(self):
            raise UnitsError('Instances of Units cannot be created')
    
        @classmethod
        def find_unit(cls, unit):
            ret = {}
            u = unit.lower()
            quantities = cls.quantities_for_unit.get(u, {})
            for quantity in quantities:
                for k in cls.dicts[quantity]:
                    if k.lower() == u:
                        ret[quantity] = k
                        break
            return ret
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.units.Units.conversion_ratio)    @classmethod
        def conversion_ratio(cls, inp, out):
            """Return conversion ratio from unit *inp* to *out*."""
            if inp == out: return 1.0
            inps = cls.quantities_for_unit.get(inp.lower(), {})
            outs = cls.quantities_for_unit.get(out.lower(), {})
            common = set(inps.keys()) & set(outs.keys())
            if len(common) > 0:
                quantity = common.pop()
                return outs[quantity]/inps[quantity]
            else:
                if len(inps) == 0 and len(outs) == 0:
                    raise UnitsError("Unsupported units: '{}' and '{}'".format(inp, out))
                if len(inps) > 0 and len(outs) > 0:
                    raise UnitsError("Invalid unit conversion: '{}' is a unit of {} and '{}' is a unit of {}".format(inp, ', '.join(list(inps.keys())), out, ', '.join(list(outs.keys()))))
                else: #exactly one of (inps,outs) empty
                    invalid, nonempty = (out,inps) if len(inps) else (inp,outs)
                    if len(nonempty) == 1:
                        quantity = list(nonempty.keys())[0]
                        raise UnitsError("Invalid unit conversion: {} is not supported. Supported units for {}: {}".format(invalid, quantity, ', '.join(list(cls.dicts[quantity].keys()))))
                    else:
                        raise UnitsError("Invalid unit conversion: {} is not a supported unit for {}".format(invalid, ', '.join(list(nonempty.keys()))))
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.units.Units.convert)    @classmethod
        def convert(cls, value, inp, out):
            """Convert *value* from unit *inp* to *out*.
    
            *value* can be a single number or a container (list, tuple, numpy.array etc.). In the latter case a container of the same type and length is returned. Conversion happens recursively, so this method can be used to convert, for example, a list of lists of numbers, or any other hierarchical container structure. Conversion is applied on all levels, to all values that are numbers (also numpy number types). All other values (strings, bools etc.) remain unchanged.
            """
            if value is None or isinstance(value, (bool, str)) or inp == out:
                return value
            if isinstance(value, collections.abc.Iterable):
                t = type(value)
                if t == np.ndarray:
                    t = np.array
                v = [cls.convert(i, inp, out) for i in value]
                return t(v)
            if isinstance(value, (int, float, np.generic)):
                return value * cls.conversion_ratio(inp,out)
            return value
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.units.Units.ascii2unicode)    @classmethod
        def ascii2unicode(cls, string):
            """
            Converts '^2' to '²' etc., for prettier printing of units.
            """
            if string is None:
                return ''
            ret = string.replace('^-1', '⁻¹').replace('angstrom', 'Å').replace('^2','²').replace('^3','³').replace('degree', '°').replace('deg.', '°')
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
