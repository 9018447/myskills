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
  * scm.plams.core.settings

# Source code for scm.plams.core.settings
[code]
    import textwrap
    import contextlib
    import re
    from functools import wraps
    
    __all__ = ['Settings']
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings)class Settings(dict):
        """Automatic multi-level dictionary. Subclass of built-in class :class:`dict`.
    
        The shortcut dot notation (``s.basis`` instead of ``s['basis']``) can be used for keys that:
    
        *   are strings
        *   don't contain whitespaces
        *   begin with a letter or an underscore
        *   don't both begin and end with two or more underscores.
    
        Iteration follows lexicographical order (via :func:`sorted` function)
    
        Methods for displaying content (:meth:`~object.__str__` and :meth:`~object.__repr__`) are overridden to recursively show nested instances in easy-readable format.
    
        Regular dictionaries (also multi-level ones) used as values (or passed to the constructor) are automatically transformed to |Settings| instances::
    
            >>> s = Settings({'a': {1: 'a1', 2: 'a2'}, 'b': {1: 'b1', 2: 'b2'}})
            >>> s.a[3] = {'x': {12: 'q', 34: 'w'}, 'y': 7}
            >>> print(s)
            a:
              1:    a1
              2:    a2
              3:
                x:
                  12:   q
                  34:   w
                y:  7
            b:
              1:    b1
              2:    b2
    
        """
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__init__)    def __init__(self, *args, **kwargs):
            dict.__init__(self, *args, **kwargs)
            cls = type(self)
    
            for k, v in self.items():
                if isinstance(v, dict) and type(v) is not cls:
                    self[k] = cls(v)
                if isinstance(v, list):
                    self[k] = [cls(i) if (isinstance(i, dict) and type(i) is not cls) else i for i in v]
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.copy)    def copy(self):
            """Return a new instance that is a copy of this one. Nested |Settings| instances are copied recursively, not linked.
    
            In practice this method works as a shallow copy: all "proper values" (leaf nodes) in the returned copy point to the same objects as the original instance (unless they are immutable, like ``int`` or ``tuple``). However, nested |Settings| instances (internal nodes) are copied in a deep-copy fashion. In other words, copying a |Settings| instance creates a brand new "tree skeleton" and populates its leaf nodes with values taken directly from the original instance.
    
            This behavior is illustrated by the following example::
    
                >>> s = Settings()
                >>> s.a = 'string'
                >>> s.b = ['l','i','s','t']
                >>> s.x.y = 12
                >>> s.x.z = {'s','e','t'}
                >>> c = s.copy()
                >>> s.a += 'word'
                >>> s.b += [3]
                >>> s.x.u = 'new'
                >>> s.x.y += 10
                >>> s.x.z.add(1)
                >>> print(c)
                a:  string
                b:  ['l', 'i', 's', 't', 3]
                x:
                  y:    12
                  z:    set([1, 's', 'e', 't'])
                >>> print(s)
                a:  stringword
                b:  ['l', 'i', 's', 't', 3]
                x:
                  u:    new
                  y:    22
                  z:    set([1, 's', 'e', 't'])
    
            This method is also used when :func:`python3:copy.copy` is called.
            """
            cls = type(self)
            ret = cls()
            for name in self:
                if isinstance(self[name], Settings):
                    ret[name] = self[name].copy()
                else:
                    ret[name] = self[name]
            return ret
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.soft_update)    def soft_update(self, other):
            """Update this instance with data from *other*, but do not overwrite existing keys. Nested |Settings| instances are soft-updated recursively.
    
            In the following example ``s`` and ``o`` are previously prepared |Settings| instances::
    
                >>> print(s)
                a:  AA
                b:  BB
                x:
                  y1:   XY1
                  y2:   XY2
                >>> print(o)
                a:  O_AA
                c:  O_CC
                x:
                  y1:   O_XY1
                  y3:   O_XY3
                >>> s.soft_update(o)
                >>> print(s)
                a:  AA        #original value s.a not overwritten by o.a
                b:  BB
                c:  O_CC
                x:
                  y1:   XY1   #original value s.x.y1 not overwritten by o.x.y1
                  y2:   XY2
                  y3:   O_XY3
    
            *Other* can also be a regular dictionary. Of course in that case only top level keys are updated.
    
            Shortcut ``A += B`` can be used instead of ``A.soft_update(B)``.
            """
            for name in other:
                if isinstance(other[name], Settings):
                    if name not in self:
                        self[name] = other[name].copy()
                    elif isinstance(self[name], Settings):
                        self[name].soft_update(other[name])
                elif name not in self:
                    self[name] = other[name]
            return self
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.update)    def update(self, other):
            """Update this instance with data from *other*, overwriting existing keys. Nested |Settings| instances are updated recursively.
    
            In the following example ``s`` and ``o`` are previously prepared |Settings| instances::
    
                >>> print(s)
                a:  AA
                b:  BB
                x:
                  y1:   XY1
                  y2:   XY2
                >>> print(o)
                a:  O_AA
                c:  O_CC
                x:
                  y1:   O_XY1
                  y3:   O_XY3
                >>> s.update(o)
                >>> print(s)
                a:  O_AA        #original value s.a overwritten by o.a
                b:  BB
                c:  O_CC
                x:
                  y1:   O_XY1   #original value s.x.y1 overwritten by o.x.y1
                  y2:   XY2
                  y3:   O_XY3
    
            *Other* can also be a regular dictionary. Of course in that case only top level keys are updated.
            """
            for name in other:
                if isinstance(other[name], Settings):
                    if name not in self or not isinstance(self[name], Settings):
                        self[name] = other[name].copy()
                    else:
                        self[name].update(other[name])
                else:
                    self[name] = other[name]
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.merge)    def merge(self, other):
            """Return new instance of |Settings| that is a copy of this instance soft-updated with *other*.
    
            Shortcut ``A + B`` can be used instead of ``A.merge(B)``.
            """
            ret = self.copy()
            ret.soft_update(other)
            return ret
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.find_case)    def find_case(self, key):
            """Check if this instance contains a key consisting of the same letters as *key*, but possibly with different case. If found, return such a key. If not, return *key*.
            """
            if not isinstance(key, str):
                return key
            lowkey = key.lower()
            for k in self:
                try:
                    if k.lower() == lowkey:
                        return k
                except (AttributeError, TypeError):
                    pass
            return key
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.get)    def get(self, key, default=None):
            """Like regular ``get``, but ignore the case."""
            return dict.get(self, self.find_case(key), default)
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.pop)    def pop(self, key, *args):
            """Like regular ``pop``, but ignore the case."""
            # A single positional argument can be supplied `*args`,
            # functioning as a default return value in case `key` is not present in this instance
            return dict.pop(self, self.find_case(key), *args)
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.popitem)    def popitem(self, key):
            """Like regular ``popitem``, but ignore the case."""
            return dict.popitem(self, self.find_case(key))
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.setdefault)    def setdefault(self, key, default=None):
            """Like regular ``setdefault``, but ignore the case and if the value is a dict, convert it to |Settings|."""
            cls = type(self)
            if isinstance(default, dict) and type(default) is not cls:
                default = cls(default)
            return dict.setdefault(self, self.find_case(key), default)
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.as_dict)    def as_dict(self):
            """Return a copy of this instance with all |Settings| replaced by regular Python dictionaries.
            """
            d = {}
            for k, v in self.items():
                if isinstance(v, Settings):
                    d[k] = v.as_dict()
                elif isinstance(v, list):
                    d[k] = [i.as_dict() if isinstance(i, Settings) else i for i in v]
                else:
                    d[k] = v
    
            return d
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.suppress_missing)    @classmethod
        def suppress_missing(cls):
            """A context manager for temporary disabling the :meth:`.Settings.__missing__` magic method: all calls now raising a :exc:`KeyError`.
    
            As a results, attempting to access keys absent from an arbitrary |Settings| instance will raise a :exc:`KeyError`, thus reverting to the default dictionary behaviour.
    
            .. note::
                The :meth:`.Settings.__missing__` method is (temporary) suppressed at the class level to ensure consistent invocation by the Python interpreter.
                See also `special method lookup`_.
    
            Example:
    
            .. code:: python
    
                >>> s = Settings()
    
                >>> with s.suppress_missing():
                ...     s.a.b.c = True
                KeyError: 'a'
    
                >>> s.a.b.c = True
                >>> print(s.a.b.c)
                True
    
            .. _`special method lookup`: https://docs.python.org/3/reference/datamodel.html#special-method-lookup
    
            """
            return SuppressMissing(cls)
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.get_nested)    def get_nested(self, key_tuple, suppress_missing=False):
            """Retrieve a nested value by, recursively, iterating through this instance using the keys in *key_tuple*.
    
            The :meth:`.Settings.__getitem__` method is called recursively on this instance until all keys in key_tuple are exhausted.
    
            Setting *suppress_missing* to ``True`` will internally open the :meth:`.Settings.suppress_missing` context manager, thus raising a :exc:`KeyError` if a key in *key_tuple* is absent from this instance.
    
            .. code:: python
    
                >>> s = Settings()
                >>> s.a.b.c = True
                >>> value = s.get_nested(('a', 'b', 'c'))
                >>> print(value)
                True
            """
            s = self
            with contextlib.suppress() if not suppress_missing else s.suppress_missing():
                for k in key_tuple:
                    s = s[k]
            return s
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.set_nested)    def set_nested(self, key_tuple, value, suppress_missing=False):
            """Set a nested value by, recursively, iterating through this instance using the keys in *key_tuple*.
    
            The :meth:`.Settings.__getitem__` method is called recursively on this instance, followed by :meth:`.Settings.__setitem__`, until all keys in key_tuple are exhausted.
    
            Setting *suppress_missing* to ``True`` will internally open the :meth:`.Settings.suppress_missing` context manager, thus raising a :exc:`KeyError` if a key in *key_tuple* is absent from this instance.
    
            .. code:: python
    
                >>> s = Settings()
                >>> s.set_nested(('a', 'b', 'c'), True)
                >>> print(s)
                a:
                  b:
                    c: 	True
            """
            s = self
            with contextlib.suppress() if not suppress_missing else s.suppress_missing():
                for k in key_tuple[:-1]:
                    s = s[k]
            s[key_tuple[-1]] = value
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.flatten)    def flatten(self, flatten_list=True):
            """Return a flattened copy of this instance.
    
            New keys are constructed by concatenating the (nested) keys of this instance into tuples.
    
            Opposite of the :meth:`.Settings.unflatten` method.
    
            If *flatten_list* is ``True``, all nested lists will be flattened as well. Dictionary keys are replaced with list indices in such case.
    
            .. code-block:: python
    
                >>> s = Settings()
                >>> s.a.b.c = True
                >>> print(s)
                a:
                  b:
                    c: 	True
    
                >>> s_flat = s.flatten()
                >>> print(s_flat)
                ('a', 'b', 'c'): 	True
            """
            if flatten_list:
                nested_type = (Settings, list)
                iter_type = lambda x: x.items() if isinstance(x, Settings) else enumerate(x)
            else:
                nested_type = Settings
                iter_type = Settings.items
    
            def _concatenate(key_ret, sequence):
                # Switch from Settings.items() to enumerate() if a list is encountered
                for k, v in iter_type(sequence):
                    k = key_ret + (k, )
                    if isinstance(v, nested_type) and v:  # Empty lists or Settings instances will return ``False``
                        _concatenate(k, v)
                    else:
                        ret[k] = v
    
            # Changes keys into tuples
            cls = type(self)
            ret = cls()
            _concatenate((), self)
            return ret
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.unflatten)    def unflatten(self, unflatten_list=True):
            """Return a nested copy of this instance.
    
            New keys are constructed by expanding the keys of this instance (*e.g.* tuples) into new nested |Settings| instances.
    
            If *unflatten_list* is ``True``, integers will be interpretted as list indices and are used for creating nested lists.
    
            Opposite of the :meth:`.Settings.flatten` method.
    
            .. code-block:: python
    
                >>> s = Settings()
                >>> s[('a', 'b', 'c')] = True
                >>> print(s)
                ('a', 'b', 'c'): 	True
    
                >>> s_nested = s.unflatten()
                >>> print(s_nested)
                a:
                  b:
                    c: 	True
            """
            cls = type(self)
            ret = cls()
            for key, value in self.items():
                s = ret
                for k1, k2 in zip(key[:-1], key[1:]):
                    if not unflatten_list:
                        s = s[k1]
                        continue
    
                    if isinstance(k2, int) and not isinstance(s[k1], list):
                        s[k1] = []
                    if isinstance(k1, int):  # Apply padding to s
                        s += [Settings()] * (k1 - len(s) + 1)
                    s = s[k1]
                s[key[-1]] = value
    
            return ret
    
        #=======================================================================
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__iter__)    def __iter__(self):
            """Iteration through keys follows lexicographical order. All keys are sorted as if they were strings."""
            return iter(sorted(self.keys(), key=str))
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__missing__)    def __missing__(self, name):
            """When requested key is not present, add it with an empty |Settings| instance as a value.
    
            This method is essential for automatic insertions in deeper levels. Without it things like::
    
                >>> s = Settings()
                >>> s.a.b.c = 12
    
            will not work.
    
            The behaviour of this method can be suppressed by initializing the :class:`.Settings.suppress_missing` context manager.
            """
            cls = type(self)
            self[name] = cls()
            return self[name]
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__contains__)    def __contains__(self, name):
            """Like regular ``__contains`__``, but ignore the case."""
            return dict.__contains__(self, self.find_case(name))
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__getitem__)    def __getitem__(self, name):
            """Like regular ``__getitem__``, but ignore the case."""
            return dict.__getitem__(self, self.find_case(name))
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__setitem__)    def __setitem__(self, name, value):
            """Like regular ``__setitem__``, but ignore the case and if the value is a dict, convert it to |Settings|."""
            cls = type(self)
            if isinstance(value, dict) and type(value) is not cls:
                value = cls(value)
            dict.__setitem__(self, self.find_case(name), value)
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__delitem__)    def __delitem__(self, name):
            """Like regular ``__detitem__``, but ignore the case."""
            return dict.__delitem__(self, self.find_case(name))
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__getattr__)    def __getattr__(self, name):
            """If name is not a magic method, redirect it to ``__getitem__``."""
            if (name.startswith('__') and name.endswith('__')):
                return dict.__getattribute__(self, name)
            return self[name]
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__setattr__)    def __setattr__(self, name, value):
            """If name is not a magic method, redirect it to ``__setitem__``."""
            if name.startswith('__') and name.endswith('__'):
                dict.__setattr__(self, name, value)
            else:
                self[name] = value
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__delattr__)    def __delattr__(self, name):
            """If name is not a magic method, redirect it to ``__delitem__``."""
            if name.startswith('__') and name.endswith('__'):
                dict.__delattr__(self, name)
            else:
                del self[name]
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings._str)    def _str(self, indent):
            """Print contents with *indent* spaces of indentation. Recursively used for printing nested |Settings| instances with proper indentation."""
            ret = ''
            for key, value in self.items():
                ret += ' '*indent + str(key) + ': \t'
                if isinstance(value, Settings):
                    if len(value) == 0:
                        ret += '<empty Settings>\n'
                    else:
                        ret += '\n' + value._str(indent+len(str(key))+1)
                else:  # Apply consistent indentation at every '\n' character
                    indent_str = ' ' * (2 + indent + len(str(key))) + '\t'
                    ret += textwrap.indent(str(value), indent_str)[len(indent_str):] + '\n'
            return ret if ret else '<empty Settings>'
    
    [[docs]](../../../../components/settings.html#scm.plams.core.settings.Settings.__str__)    def __str__(self):
            return self._str(0)
    
        __repr__ = __str__
        __iadd__ = soft_update
        __add__ = merge
        __copy__ = copy
    
    class SuppressMissing(contextlib.AbstractContextManager):
        """A context manager for temporary disabling the :meth:`.Settings.__missing__` magic method. See :meth:`Settings.suppress_missing` for more details."""
        def __init__(self, obj: type):
            """Initialize the :class:`SuppressMissing` context manager."""
            # Ensure that obj is a class, not a class instance
            self.obj = obj if isinstance(obj, type) else type(obj)
            self.missing = obj.__missing__
    
        def __enter__(self):
            """Enter the :class:`SuppressMissing` context manager: delete :meth:`.Settings.__missing__` at the class level."""
            @wraps(self.missing)
            def __missing__(self, name): raise KeyError(name)
    
            # The __missing__ method is replaced for as long as the context manager is open
            setattr(self.obj, '__missing__', __missing__)
    
        def __exit__(self, exc_type, exc_value, traceback):
            """Exit the :class:`SuppressMissing` context manager: reenable :meth:`.Settings.__missing__` at the class level."""
            setattr(self.obj, '__missing__', self.missing)
    
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
