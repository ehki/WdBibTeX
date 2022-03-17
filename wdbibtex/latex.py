import codecs
import locale
import pathlib
import os
import re


class Cite:
    """Citation package emurating contents and commands.

    Parameters
    ----------
    citeleft : str, default '['
        Left delimiter of list.
    citeright : str, default ']'
        Right delimiter of list.
    use_cite_package : bool, default False
        If False, emulate LaTeX's use_cite_package citation handling.
        If True, emulate cite package's behavior.
    """
    def __init__(
        self,
        citeleft='[',
        citeright=']',
        targetbasename='wdbib',
        use_cite_package=False,
        workdir='.tmp',
    ):
        """Costructor of Cite.
        """

        # Store settings in internal attributes.
        if os.path.isabs(workdir):
            self.workdir = pathlib.Path(workdir)
        else:
            self.workdir = (
                pathlib.Path(os.getcwd()) / workdir
            ).resolve()

        self._targetbasename = targetbasename

        self._replacer = None
        self._citation = []
        self._bibstyle = None
        self._bibdata = None
        self._bibcite = {}
        self._conversion_dict = {}

        self._citation_labels = dict()
        self._citeleft = citeleft
        self._citeright = citeright
        self.use_cite_package = use_cite_package
        self.citation_keys_in_context = []

    @property
    def citeleft(self):
        r"""Left delimiter of list. Default '['.

        Returns
        -------
        str
            Left delimiter of list.

        Examples
        --------
        >>> import wdbibtex
        >>> c = wdbibtex.Cite()
        >>> c.citation_labels = {'key1': 1, 'key2': 2, 'key3': 3}
        >>> c.citeleft
        '['
        >>> c.cite('\\cite{key1}')
        '[1]'
        >>> c.cite('\\cite{key2,key3}')
        '[2,3]'
        >>> c.cite('\\cite{key3,key2,key1}')
        '[3,2,1]'
        >>> c.citeleft = '('
        >>> c.citeleft
        '('
        >>> c.cite('\\cite{key1}')
        '(1]'
        >>> c.cite('\\cite{key2,key3}')
        '(2,3]'
        >>> c.cite('\\cite{key3,key2,key1}')
        '(3,2,1]'
        """
        return self._citeleft

    @citeleft.setter
    def citeleft(self, s):
        if not isinstance(s, str):
            TypeError(
                'expected string object but '
                '%s object given.' % type(s))
        self._citeleft = s

    @property
    def citeright(self):
        r"""Right delimiter of list. Default ']'.

        Returns
        -------
        str
            Right delimiter of list.

        Examples
        --------
        >>> import wdbibtex
        >>> c = wdbibtex.Cite()
        >>> c.citation_labels = {'key1': 1, 'key2': 2, 'key3': 3}
        >>> c.citeright
        ']'
        >>> c.cite('\\cite{key1}')
        '[1]'
        >>> c.cite('\\cite{key2,key3}')
        '[2,3]'
        >>> c.cite('\\cite{key3,key2,key1}')
        '[3,2,1]'
        >>> c.citeright = ')'
        >>> c.citeright
        ')'
        >>> c.cite('\\cite{key1}')
        '[1)'
        >>> c.cite('\\cite{key2,key3}')
        '[2,3)'
        >>> c.cite('\\cite{key3,key2,key1}')
        '[3,2,1)'
        """
        return self._citeright

    @citeright.setter
    def citeright(self, s):
        if not isinstance(s, str):
            TypeError(
                'expected string object but '
                '%s object given.' % type(s))
        self._citeright = s

    @property
    def citation_labels(self):
        """Key to number map of citations.

        Returns
        -------
        dict
            Citation key to citation number map.
        """
        return self._citation_labels

    @citation_labels.setter
    def citation_labels(self, d):
        if not isinstance(d, str):
            TypeError(
                'expected dictionary object but '
                '%s object given.' % type(d))
        self._citation_labels = d

    @property
    def use_cite_package(self):
        """If Cite class emulate cite package's behavior.

        Returns
        -------
        bool
            If True, emulate cite package's behavior.
            If False, emulrate LaTeX's original citation mechanism.

        Raises
        ------
        TypeError
            If non-bool value is given to setter.
        """
        return self._use_cite_package

    @use_cite_package.setter
    def use_cite_package(self, b):
        if isinstance(b, bool):
            self._use_cite_package = b
        else:
            raise TypeError(
                'use_cite_package attribute must be bool.'
            )

    def parse_context(self, c):
        r"""Find all citation keys from context written to .tex file.

        Find all citation keys from context written to .tex file.
        Found keys are stores to citation_keys_in_context attribute.

        Parameters
        ----------
        c : str
            Parsed texts.

        Examples
        --------
        >>> import wdbibtex
        >>> ct = wdbibtex.Cite()
        >>> ct.parse_context(
        ...     'Some citation \\cite{key}. Some example \\cite{key1,key2}'
        ... )
        >>> ct.citation_keys_in_context
        ['key', 'key1,key2']
        """
        found_keys = re.findall(r'\\+cite\{(.*?)\}', c)
        for k in found_keys:
            self.citation_keys_in_context.append(k)

    @property
    def citation_keys_in_context(self):
        return self._citation_keys_in_context

    @citation_keys_in_context.setter
    def citation_keys_in_context(self, lis):
        if isinstance(lis, list):
            self._citation_keys_in_context = lis
        else:
            raise TypeError(
                'citation_keys_in_context must be a list.'
            )

    @property
    def citation(self):
        """[Read only] Returns citation key(s) found in aux file.
        """
        return self._citation

    @property
    def bibstyle(self):
        """[Read only] Returns bibliography style string written in aux file.
        """
        return self._bibstyle

    @property
    def bibdata(self):
        """[Read only] Returns bibliography data file(s) written in aux file.
        """
        return self._bibdata

    @property
    def bibcite(self):
        """[Read only] Returns citation key and citation number dictionary
        """
        return self._bibcite

    def read_aux(self):
        r"""Read .aux file.

        Aux file will be read line-by-line.
        Following four types of the line will be
        interpreted and stored to the LaTeX attributes.

        - \\citation{keys}
           Appended to the citation attribute
           (list object) key as string.
        - \\bibstyle{s}
           Stored as bibstyle string attribute.
        - \\bibdata{d}
           Stored as bibdata string attribute.
        - \\bibcite{k}{n}
           Added to bibcite attribute
           (dictionary) as {k: n}.
        """
        fn = self.workdir / (self._targetbasename + '.aux')
        with codecs.open(fn, 'r', 'utf-8') as f:
            self._auxdata = f.readlines()
        for line in self._auxdata:
            self._parse_line(line)
        self._build_conversion_dict()
        self._citation_labels.update(self._bibcite)
        self._get_replacer()

    def _parse_line(self, line):
        r"""Parse one line of .aux

        Parameters
        ----------
        line : str
            One line of .aux file to parse.
        """
        if line.startswith('\\citation'):
            self._citation.append(line[len('\\citation{'): -len('}\n')])
        elif line.startswith('\\bibstyle'):
            self._bibstyle = line[len('\\bibstyle{'): -len('}\n')]
        elif line.startswith('\\bibdata'):
            self._bibdata = line[len('\\bibdata{'): -len('}\n')]
        elif line.startswith('\\bibcite'):
            key, value = line[len('\\bibcite{'): -len('}\n')].split('}{')
            value = int(value)
            self._bibcite.update({key: value})

    def _get_replacer(self):
        """Get key and value for replace word document.
        """
        replacer = dict()
        for k, v in self._conversion_dict.items():
            replacer.update({'\\\\cite\\{%s\\}' % k: '[%s]' % v})
        self._replacer = replacer

    def _build_conversion_dict(self):
        r"""Prepare replaing citation keys with dashed range strings.

        Generate dictionary of such as {'refa,refb,refc,refe,refg': '1-3,5,7'}.
        """
        for cite in self._citation:
            cite_nums = [self._bibcite[c] for c in cite.split(',')]
            self._conversion_dict.update(
                {cite: self._compress(cite_nums)}
                )
        for cite in self.citation_keys_in_context:
            cite_nums = [self._bibcite[c] for c in cite.split(',')]
            if self.use_cite_package:
                self._conversion_dict.update(
                    {cite: self._compress(sorted(cite_nums))}
                )
            else:
                self._conversion_dict.update(
                    {cite: ','.join(str(c) for c in cite_nums)}
                    )

    def cite(self, s):
        r"""Do \cite command formatting.

        Returns formated text from citation commands such as
        \cite{key1} and \cite{key1,key2,key3}, etc.
        By default, if there are three or more consecutive numbers,
        they are compressed into a range using an en-dash.
        Citation numbers are also sorted in the default condition.

        Parameters
        ----------
        s : str
            Raw string to be formatted.
            For example, \\cite{key1} or \\cite{key2,key3}.

        Examples
        --------
        >>> import wdbibtex
        >>> c = wdbibtex.Cite()
        >>> c.citation_labels = {'key1': 1, 'key2': 2, 'key3': 3}
        >>> c.cite('\\cite{key1}')
        '[1]'
        >>> c.cite('\\cite{key2,key3}')
        '[2,3]'
        >>> c.cite('\\cite{key3,key2,key1}')
        '[3,2,1]'

        >>> import wdbibtex
        >>> c = wdbibtex.Cite(use_cite_package=True)
        >>> c.citation_labels = {'key1': 1, 'key2': 2, 'key3': 3}
        >>> c.cite('\\cite{key1}')
        '[1]'
        >>> c.cite('\\cite{key2,key3}')
        '[2,3]'
        >>> c.cite('\\cite{key3,key2,key1}')
        '[1\u20133]'

        Note \\u2013 is en-dash.
        """
        p = re.compile(r'\\+cite\{(.*)\}')
        if p.match(s):
            keys = p.match(s).group(1).split(',')
            if len(keys) == 1:
                key = keys[0]
                return (
                    self._citeleft
                    + str(self._citation_labels[key])
                    + self._citeright
                )
            if len(keys) > 1:
                if self.use_cite_package:
                    nums = sorted(
                        [self._citation_labels[key] for key in keys]
                    )
                    return (
                        self._citeleft
                        + self._compress(nums)
                        + self._citeright
                    )
                else:
                    nums = [str(self._citation_labels[key]) for key in keys]
                    return (
                        self._citeleft
                        + ','.join(nums)
                        + self._citeright
                    )
        else:
            ValueError(
                'no citation pattern matched.'
            )

    def _compress(self, nums, sep=u'\u2013'):
        r"""Compress groups of three or more consecutive numbers into a range.

        Compress poor list of positive integers with three or more
        consecutive numbers into a range using a separating character.
        For example, a list ``[1,2,3,6]`` will be converted into ``[1-3,6]``.

        Parameters
        ----------
        nums : list of positive integers
            Multiple integers to convert dashed range string.
            A list of single element integer is also allowd.
        sep : str, default en-dash(U+2013)
            A character inserted betwen start and end of range.
        """
        seq = []
        final = []
        last = 0

        for index, val in enumerate(nums):

            if last + 1 == val or index == 0:
                seq.append(val)
                last = val
            else:
                if len(seq) > 2:
                    final.append(str(seq[0]) + sep + str(seq[len(seq)-1]))
                elif len(seq) == 2:
                    final.append(str(seq[0]) + ',' + str(seq[len(seq)-1]))
                else:
                    final.append(str(seq[0]))
                    seq = []
                    seq.append(val)
                    last = val

            if index == len(nums) - 1:
                if len(seq) > 2:
                    final.append(str(seq[0]) + sep + str(seq[len(seq)-1]))
                elif len(seq) == 2:
                    final.append(str(seq[0]) + ',' + str(seq[len(seq)-1]))
                else:
                    final.append(str(seq[0]))

        final_str = ','.join(map(str, final))
        return final_str


class Bibliography:
    """LaTeX bbl file related contents and commands.

    Parameters
    ----------
    targetbasename : str, default 'wdbib'
        Base name of LaTeX related files.
    workdir : str or path object, default '.tmp'
        Temporal working directory to store LaTeX contents.

    Examples
    --------
    >>> import wdbibtex
    >>> bb = wdbibtex.Bibliography()
    >>> bb.read_bbl()  # doctest: +SKIP
    """
    def __init__(
        self,
        targetbasename='wdbib',
        workdir='.tmp',
    ):
        """Cunstructor of Bibliography
        """

        # Store settings in internal attributes.
        if os.path.isabs(workdir):
            self.workdir = pathlib.Path(workdir)
        else:
            self.workdir = (
                pathlib.Path(os.getcwd()) / workdir
            ).resolve()

        self.__targetbasename = targetbasename

    @property
    def thebibliography(self):
        r"""Plain text to replace \\thebibliography in word file.

        A plain text of LaTeX-processed bibliography list.
        An tab string is inserted between each citenum and citation string.
        Example in IEEE format follows:

        .. code-block:: text

            [1]\\tF. Author, S. Author, "Paper Title," Journal Name, vol. 1, no. 1, p. 1, march 2022.
            [2]\\tG. Name, F. Name, "Title," Journal, vol. 2, no. 2, pp. 1-10, 2020.

        Returns
        -------
        str
            Plain text of the thebibliography.

        Raises
        ------
        ValueError
            If thebibliography text is not set.
        """  # noqa E501
        if self.__thebibtext is None:
            raise ValueError(
                'Thebibliography text is not set yet.'
            )
        return self.__thebibtext

    def read_bbl(self):
        """Read .bbl file.

        Read .bbl file to extract formatted thebibliography text.

        Examples
        --------
        >>> import wdbibtex
        >>> bb = wdbibtex.Bibliography()
        >>> bb.read_bbl()  # doctest: +SKIP
        """
        fn = self.workdir / (self.__targetbasename + '.bbl')
        with codecs.open(fn, 'r', 'utf-8') as f:
            self.__bbldata = f.readlines()
        self.__make_thebibliography_text()

    def __make_thebibliography_text(self):
        """Generate thebibliography plain text to incert word file.
        """
        replacer = {}
        replacer.update({
            r'\n  ': ' ',
            r'\{\\em (.*)\}': r'\1',
            r'\\emph\{(.*)\}': r'\1',
            r'\\BIBforeignlanguage\{(.*)\}\{(.*)\}': r'\2',
            r'~': ' ',
            r'--': u'\u2014',
            r'``': '“',
            r"''": '”',
            r'\n\n': '\n'
            })
        thebib_begin = None
        for i, line in enumerate(self.__bbldata):
            if line.startswith('\\bibitem') and thebib_begin is None:
                thebib_begin = i
            if line.startswith('\\end{thebibliography}'):
                thebib_end = i
        thebibtext = ''.join(self.__bbldata[thebib_begin: thebib_end])
        for k, v in replacer.items():
            thebibtext = re.sub(k, v, thebibtext)
        for c, m in enumerate(re.findall('\\\\bibitem{(.*)}\n', thebibtext)):
            thebibtext = re.sub(
                '\\\\bibitem{%s}\n' % m, '[%s]\t' % (c+1), thebibtext
            )
        self.__thebibtext = thebibtext


class LaTeX(Cite):
    """LaTeX related contents and commands.

    Run LaTeX and BibTeX commands. Write .tex files.
    Read and parse .aux and .bbl files.
    Prepare conversion LaTeX keys in Word file into BibTeX processed texts.

    Parameters
    ----------
    bibtexcmd : str or None, default None
        BibTeX command.
        If None, automatically selected accorting to system locale.
    bibtexopts : str or None, default None
        BibTeX command options.
        If None, automatically selected according to system locale.
    preamble : str or None, default None
        Preamble of .tex file.
        If None, automatically selected.
    targetbasename : str, default 'wdbib'
        Base name of LaTeX related files.
    texcmd : str or None, default None
        LaTeX command.
        If None, automatically selected according to system locale.
    texopts : str or None, default None
        LaTeX command options.
        If None, automatically selected accorgin to system locale.
    workdir : str or path object, default '.tmp'
        Temporal working directory to store LaTeX contents.
    """
    def __init__(
            self,
            bibtexcmd=None,
            bibtexopts=None,
            preamble=None,
            targetbasename='wdbib',
            texcmd=None,
            texopts=None,
            workdir='.tmp',
    ):

        super(LaTeX, self).__init__()

        self.__locale = self.__default_locale()

        # Set automatically selected values
        if texcmd is None:
            if self.__locale == 'en':
                texcmd = 'latex'
            elif self.__locale == 'ja':
                texcmd = 'uplatex'
        if texopts is None:
            texopts = '-interaction=nonstopmode -file-line-error'
        if bibtexcmd is None:
            if self.__locale == 'en':
                bibtexcmd = 'bibtex'
            elif self.__locale == 'ja':
                bibtexcmd = 'upbibtex'
        if bibtexopts is None:
            bibtexopts = ''

        # Store settings in internal attributes.
        if os.path.isabs(workdir):
            self.workdir = pathlib.Path(workdir)
        else:
            self.workdir = (
                pathlib.Path(os.getcwd()) / workdir
            ).resolve()
        self.__targetbasename = targetbasename
        self.__texcmd = texcmd
        self.__texopts = texopts
        self.__bibtexcmd = bibtexcmd
        self.__bibtexopts = bibtexopts
        self.__packages = None
        self.__bibliographystyle = None
        self.__documentclass = None
        self.__package_list = []
        self.preamble = preamble

        # Makedir working directory if not exist.
        self.workdir.mkdir(exist_ok=True)

    @property
    def documentclass(self):
        """LaTeX documentclass string."""
        return self.__documentclass

    @documentclass.setter
    def documentclass(self, documentclass):
        if not documentclass.startswith('\\'):
            raise ValueError(
                'Invalid documentclass.'
            )
        self.__documentclass = documentclass

        # Update preamble
        self.__update_preamble()

    def set_documentclass(self, documentclass, *options):
        """Documentclass setter.

        Parameters
        ----------
        documentclass
            Documentclass
        *options
            Documentclass options.
        """
        if documentclass.startswith('\\'):
            self.__documentclass = documentclass
        else:
            if bool(options):
                opts = '[%s]' % ','.join(options)
            self.__documentclass = \
                '\\documentclass%s{%s}' % (opts, documentclass)

        # Update preamble
        self.__update_preamble()

    @property
    def bibliographystyle(self):
        """Bibliographystyle string.

        Raises
        ------
        ValueError
            If bst is None and there is no or multiple .bst files in cwd.
        """
        return self.__bibliographystyle

    @bibliographystyle.setter
    def bibliographystyle(self, bibliographystyle):
        import glob
        if bibliographystyle:
            self.__bibliographystyle = bibliographystyle

        else:
            bibliographystile = glob.glob('*.bst')
            if len(bibliographystile) > 1:
                raise ValueError(
                    'More than two .bst files found in working directory.'
                )
            elif len(bibliographystile) == 0:
                raise ValueError(
                    'No .bst files found in working directory.'
                )
            else:
                bibliographystile = bibliographystile[0]
                self.set_bibliographystyle(bibliographystile)

    def set_bibliographystyle(self, bst):
        """Bibliographystyle setter.

        Parameters
        ----------
        bst : str
            Bibliography style
        """
        self.__bibliographystyle = '\\bibliographystyle{%s}' % bst

        # Update preamble
        self.__update_preamble()

    @property
    def packages(self):
        r"""Returns used LaTeX packages.

        Returns
        -------
        str
            Multi-line LaTeX \\usepackage[options]{package} string.

        Examples
        --------
        >>> import wdbibtex
        >>> tx = wdbibtex.LaTeX()
        >>> tx.add_package('cite')
        >>> print(tx.packages)
        \usepackage{cite}
        >>> tx.add_package('graphicx', 'dvipdfmx')
        >>> print(tx.packages)
        \usepackage{cite}
        \usepackage[dvipdfmx]{graphicx}
        """
        return self.__packages

    def __update_packages(self):
        pkgs = []
        for pkg, *opts in self.__package_list:
            if bool(opts):
                pkgs.append('\\usepackage[%s]{%s}' % (','.join(opts), pkg))
            else:
                pkgs.append('\\usepackage{%s}' % pkg)

        self.__packages = '\n'.join(pkgs)

    def add_package(self, package, *options):
        """Add a package to the package list

        Add a package to the package list of package_list.
        The package can have option.
        The package will used in the preamble attribute.

        Parameters
        ----------
        package : str
            Package name.
        *options
            Options of the package.
        """

        # Overwrite duplicated package
        for i, (p, *o) in enumerate(self.__package_list):
            if p == package:
                self.__package_list.pop(i)
                break
        self.__package_list.append(
            [package, *options]
        )

        # Update package string.
        self.__update_packages()

        # Update preamble
        self.__update_preamble()

    def is_package_used(self, p):
        r"""Returns if the package is used.

        Returns False if the package is not used
        while True if the package is used without option.
        If the package is used with option(s), returns List of option(s).

        Parameters
        ----------
        p : str
            Package name to find.

        Returns
        -------
        bool or list
            False if the package is not used.
            True if the package is used without option.
            List of option(s) if the package is used with option(s).

        Examples
        --------
        >>> import wdbibtex
        >>> tx = wdbibtex.LaTeX()
        >>> tx.add_package('cite')
        >>> tx.is_package_used('cite')
        True
        >>> tx.add_package('graphicx', 'dvipdfmx')
        >>> tx.is_package_used('graphicx')
        ['dvipdfmx']
        >>> tx.is_package_used('xcolor')
        False
        >>> print(tx.packages)
        \usepackage{cite}
        \usepackage[dvipdfmx]{graphicx}
        """
        for package in self.__package_list:
            if package[0] == p:
                if len(package) == 1:
                    return True
                else:
                    return package[1:]
        else:
            return False

    def write(self, c, bib=None):
        r"""Write .tex file.

        Write minimal .tex file into workdir.
        TeX file contains only citation contents,
        pre-defined (at constructor of LaTeX object) preamble,
        \\bibliography, and \\bibliographystyle.

        Parameters
        ----------
        c : str
            String data to be written in .tex file.
        bib : str or None, default None
            Bibliography library file(s). If None, use all .bib files in cwd.
        """
        import glob

        if bib is None:
            # Use only root name (file name without extension).
            bib = ''.join(
                [os.path.splitext(b)[0] for b in glob.glob('*.bib')]
            )

        fn = self.workdir / (self.__targetbasename + '.tex')
        with codecs.open(fn, 'w', 'utf-8') as f:
            f.writelines(
                '\n'.join([
                    self.preamble,
                    '\\begin{document}',
                    c,
                    '\\bibliography{%s}' % bib,
                    '\\end{document}',
                    '',
                ])
            )

    def build(self):
        """Build LaTeX related files.

        Build LaTeX files in old-style four steps (without PDF generation).

        1. latex: to generate .aux from .tex
        2. bibtex: to generate .bbl and update .aux from .aux and .bst.
        3. latex: to update .aux.
        4. latex: to complete .aux.

        Firstly the current directory is switched to the working directory.
        Secondly the above four steps are invoked.
        Thirdly read .bbl and .aux files are parsed.
        Finally, the current directory is switched
        to the original working directory.
        """
        import subprocess
        cwd = os.getcwd()  # Save original working directory.
        os.chdir(self.workdir)
        latexcmd = ' '.join(filter(None, [
            self.__texcmd,
            self.__texopts,
            self.__targetbasename + '.tex'
        ]))
        bibtexcmd = ' '.join(filter(None, [
            self.__bibtexcmd,
            self.__bibtexopts,
            self.__targetbasename,
        ]))

        # Four steps to complete build LaTeX project.
        subprocess.call(latexcmd, shell=True)
        subprocess.call(bibtexcmd, shell=True)
        subprocess.call(latexcmd, shell=True)
        subprocess.call(latexcmd, shell=True)

        os.chdir(cwd)  # Back to original working directory.

    @property
    def preamble(self):
        r"""Returns latex preamble text.

        A text to be used as LaTeX preamble. Note that not all latex-compatible
        preamble is used in WdBibTeX package. LaTeX class accepts None
        for preamble attribute. In this case, the following default preamble
        text is used according to system locale.
        Note BST is replaced a bibliography style file
        placed in the project directory.

        .. code-block:: text

            \documentclass[latex]{article}
            \bibliographystyle{BST}

        .. code-block:: text

            \documentclass[uplatex]{jsarticle}
            \bibliographystyle{BST}

        Returns
        -------
        str
            Preamble text.
        """

        return self.__preamble

    @preamble.setter
    def preamble(self, s):
        if s is None:
            if self.__locale == 'en':
                self.set_documentclass('article')
            elif self.__locale == 'ja':
                self.set_documentclass('jsarticle', 'uplatex')
        elif isinstance(s, str):
            self.__parse_preamble(s)
        else:
            raise ValueError(
                'Invalid preamble. '
                'Only None or str is allowed.'
            )

    def __update_preamble(self):

        contents = [
            self.documentclass,
            self.packages,
            self.bibliographystyle,
        ]
        self.__preamble = '\n'.join(
            [c for c in contents if c is not None]
        )

    def __parse_preamble(self, preamble):
        detect_documentclass = False
        for ln in preamble.split('\n'):
            if ln.startswith('%') and not detect_documentclass:
                pass

            elif re.match(r'.*documentclass.*', ln):
                detect_documentclass = True
                m = re.match(r'.*documentclass(\[(.*)\])*\{(.*)\}', ln)
                documentclass_opt = []
                if m.group(1) is not None:
                    documentclass_opt = m.group(2).replace(' ', '').split(',')
                documentclsass = m.group(3)

                self.set_documentclass(documentclsass, *documentclass_opt)

            elif re.match(r'.*usepackage.*', ln):
                m = re.match(r'.*usepackage(\[(.*)\])*\{(.*)\}', ln)
                package_opt = []
                if m.group(1) is not None:
                    package_opt = m.group(2).replace(' ', '').split(',')
                package = m.group(3)

                self.add_package(package, *package_opt)

            elif re.match(r'.*bibliographystyle.*', ln):
                m = re.match(r'.*bibliographystyle\{(.*)\}', ln)
                bibliographystyle = m.group(1)

                self.set_bibliographystyle(bibliographystyle)

            elif re.match(r'.*renewcommand\\citeleft.*', ln):
                m = re.match(r'.*renewcommand\\citeleft\{(.*)\}', ln)
                self.citeleft = m.group(1)

            elif re.match(r'.*renewcommand\\citeright.*', ln):
                m = re.match(r'.*renewcommand\\citeright\{(.*)\}', ln)
                self.citeright = m.group(1)

            else:
                pass

    @property
    def locale(self):
        """Returns system locale

        Locale string to decide which latex commands used.
        Currently english(en) and japanese(ja) are supported.
        If locale is manually set, returns the local as is.
        Else, determined using locale.getlocale().

        Returns
        -------
        str
            Locale text in two characters for example 'en' or 'ja'.
        """

        return self.__locale

    @locale.setter
    def locale(self, s):
        if isinstance(s, str) and len(s) == 2:
            self.__locale = s
        else:
            raise ValueError(
                'Invalid locale string. '
                'Only 2-characters string is allowed.'
            )

    def __default_locale(self):
        loca, locb = locale.getlocale()
        if 'en' in loca or 'en' in locb:
            return 'en'
        elif 'English' in loca or 'English' in locb:
            return 'en'
        elif 'ja' in loca or 'ja' in locb:
            return 'ja'
        elif 'Japanese' in loca or 'Japanese' in locb:
            return 'ja'
        else:
            raise ValueError('Unhandled locale %s' % locale.getlocale())
