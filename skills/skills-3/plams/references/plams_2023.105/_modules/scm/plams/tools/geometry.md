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
  * scm.plams.tools.geometry

# Source code for scm.plams.tools.geometry
[code]
    import numpy as np
    try:
        from scipy.spatial.distance import cdist
        scipy_present = True
    except ImportError:
        scipy_present = False
    
    from .units import Units
    
    __all__ = ['rotation_matrix', 'axis_rotation_matrix', 'distance_array', 'angle','dihedral','cell_shape','cellvectors_from_shape']
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.geometry.rotation_matrix)def rotation_matrix(vec1, vec2):
        """
        Calculate the rotation matrix rotating *vec1* to *vec2*. Vectors can be any containers with 3 numerical values. They don't need to be normalized. Returns 3x3 numpy array.
        """
        vec1, vec2 = np.array(vec1), np.array(vec2)
        a = vec1/np.linalg.norm(vec1)
        b = vec2/np.linalg.norm(vec2)
    
        # avoid division by zero in case of antiparallel vectors
        if abs(1+np.dot(a,b)) < 1E-8:
            return -np.eye(3)
        
        v1,v2,v3 = np.cross(a,b)
        M = np.array([[0, -v3, v2], [v3, 0, -v1], [-v2, v1, 0]])
        return (np.identity(3) + M + np.dot(M,M)/(1+np.dot(a,b)))
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.geometry.axis_rotation_matrix)def axis_rotation_matrix(vector, angle, unit='radian'):
        """
        Calculate the rotation matrix rotating along the *vector* by *angle* expressed in *unit*.
    
        *vector* can be any container with 3 numerical values. They don't need to be normalized. A positive angle denotes counterclockwise rotation, when looking along *vector*. Returns 3x3 numpy array.
        """
    
        vector /= np.linalg.norm(vector)
        v0, v1, v2 = vector
    
        W = np.array([[0, -v2, v1],
                      [v2, 0, -v0],
                      [-v1, v0, 0]])
    
        angle = Units.convert(angle, unit, 'radian')
        a1 = np.sin(angle)
        a2 = 1.0 - np.cos(angle)
    
        return np.identity(3) + a1 * W + a2 * W@W
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.geometry.distance_array)def distance_array(array1, array2):
        """Calculates distance between each pair of points in *array1* and *array2*. Returns 2D ``numpy`` array.
    
        Uses fast ``cdist`` function if ``scipy`` is present, otherwise falls back to slightly slower ``numpy`` loop. Arguments should be 2-dimensional ``numpy`` arrays with the same second dimension. If *array1* is A x N and *array2* is B x N, the returned array is A x B.
        """
        return cdist(array1, array2) if scipy_present else np.array([np.linalg.norm(i - array2, axis=1) for i in array1])
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.geometry.angle)def angle(vec1, vec2, result_unit='radian'):
        """Calculate an angle between vectors *vec1* and *vec2*.
    
        *vec1* and *vec2* should be iterable containers of length 3 (for example: tuple, list, numpy array). Values stored in them are expressed in Angstrom. Returned value is expressed in *result_unit*.
    
        This method requires all atomic coordinates to be numerical values, :exc:`~exceptions.TypeError` is raised otherwise.
        """
        vec1 = np.array([*vec1], dtype=float)
        vec2 = np.array([*vec2], dtype=float)
    
        num = np.dot(vec1, vec2)
        den = np.sqrt(((vec1)**2).sum()) * np.sqrt(((vec2)**2).sum())
        return Units.convert(np.arccos(num/den), 'radian', result_unit)
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.geometry.dihedral)def dihedral(p1, p2, p3, p4, unit='radian'):
        """Calculate the value of diherdal angle formed by points *p1*, *p2*, *p3* and *p4* in a 3D space. Arguments can be any containers with 3 numerical values, also instances of |Atom|. Returned value is always non-negative, measures the angle clockwise (looking along *p2-p3* vector) and is expressed in *unit*."""
        p1 = np.array([*p1], dtype=float)
        p2 = np.array([*p2], dtype=float)
        p3 = np.array([*p3], dtype=float)
        p4 = np.array([*p4], dtype=float)
    
        b0 = p1 - p2
        b1 = p3 - p2
        b2 = p4 - p3
    
        b1 /= np.linalg.norm(b1)
        v = b0 - np.dot(b0, b1)*b1
        w = b2 - np.dot(b2, b1)*b1
    
        x = np.dot(v, w)
        y = np.dot(np.cross(b1, v), w)
        ret = np.arctan2(y, x)
        ret = 2*np.pi+ret if ret < 0 else ret
        return Units.convert(ret, 'radian', unit)
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.geometry.cell_shape)def cell_shape (lattice) :
        """
        Converts lattice vectors to lengths and angles (in radians)
        Sets internal cell size data, based on set of cell vectors.
    
        *cellvectors* is list containing three cell vectors (a 3x3 matrix)
        """
        lattice = np.asarray(lattice)
        a,b,c = np.sqrt((lattice**2).sum(axis=1))
    
        if a == 0. and b == 0. and c == 0. :
                return
    
        alpha,beta,gamma = (90.,90.,90.)
    
        if c != 0 :
                alpha = angle (lattice[1],lattice[2])
                beta  = angle (lattice[0],lattice[2])
        if b != 0 :
                gamma = angle (lattice[0],lattice[1])
    
        return [a,b,c,alpha,beta,gamma]
    
    def cell_lengths(lattice, unit='angstrom'):
        """Return the lengths of the lattice vector. Returns a list with the same length as the number of lattice vector."""
    
        if lattice is None or len(lattice) == 0:
            raise ValueError('Cannot calculate cell_lengths for nonperiodic system')
        lattice = np.asarray(lattice)
        ret = np.sqrt((lattice**2).sum(axis=1)) * Units.conversion_ratio('angstrom', unit)
        return ret.tolist()
    
    def cell_angles(lattice, unit='degree'):
        """Return the angles between lattice vectors.
    
        unit : str
            output unit
    
        For 2D systems, returns a list [gamma]
    
        For 3D systems, returns a list [alpha, beta, gamma]
        """
        ndim = len(lattice)
    
        if ndim < 2:
            raise ValueError('Cannot calculate cell_angles for fewer than 2 lattice vectors. Tried with {} lattice vectors'.format(ndim))
    
        gamma = angle(lattice[0], lattice[1], result_unit=unit)
    
        if ndim == 2:
            return [gamma]
    
        if ndim >= 3:
            alpha = angle(lattice[1], lattice[2], result_unit=unit)
            beta = angle(lattice[0], lattice[2], result_unit=unit)
            return [alpha, beta, gamma]
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.geometry.cellvectors_from_shape)def cellvectors_from_shape (box) :
        """
        Converts lengths and angles (in radians) of lattice vectors to the lattice vectors 
        """
        a = box[0]
        b = box[1]
        c = box[2]
        alpha, beta, gamma = 90., 90., 90
        if len(box) == 6 :
            alpha = box[3]#*np.pi/180.
            beta = box[4]#*np.pi/180.
            gamma = box[5]#*np.pi/180.
    
        va = [a,0.,0.]
        vb = [b*np.cos(gamma),b*np.sin(gamma),0.]
    
        cx = c*np.cos(beta)
        cy = (np.cos(alpha) - np.cos(beta)*np.cos(gamma)) * c / np.sin(gamma)
        volume = 1 - np.cos(alpha)**2 - np.cos(beta)**2 - np.cos(gamma)**2
        volume += 2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma)
        volume = np.sqrt(volume)
        cz = c * volume / np.sin(gamma)
        vc = [cx,cy,cz]
    
        lattice = [va,vb,vc]
    
        return lattice
    
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
