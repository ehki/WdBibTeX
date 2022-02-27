import codecs
import locale
import pathlib
import os
import re


class LaTeX:
    """LaTeX related contents and commands.

    Run LaTeX and BibTeX commands. Write .tex files.
    Read and parse .aux and .bbl files.
    Prepare conversion LaTeX keys in Word file into BibTeX processed texts.

    Parameters
    ----------
    workdir : str | pathlib.Path, default '.tmp'
        Temporal working directory to store LaTeX contents.
    targetbasename : str, default wdbib
        Base name of LaTeX related files.
    bibtexcmd : str or None, default None
        BibTeX command. If None, automatically selected.
    bibtexopts : str or None, default None
        BibTeX command options. If None, automatically selected.
    preamble : str or None, default None
        Preamble of .tex file. if None, automatically selected.
    texcmd : str or None, default None
        LaTeX command. If None, automatically selected.
    texopts : str or None, default None
        LaTeX command options. If None, automatically selected.
    """
    def __init__(
            self,
            workdir='.tmp',
            targetbasename='wdbib',
            texcmd=None,
            texopts=None,
            bibtexcmd=None,
            bibtexopts=None,
            preamble=None,
            autostart=False,
            dashstarts=3,
    ):
        # Argument check
        assert dashstarts in (2, 3), (
            'Invalid dashstarts. Only integer 2 or 3 is allowed.'
        )

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
        if preamble is None:
            preamble = (
                '\\documentclass[latex]{article}\n'
                '\\usepackage{cite}\n'
            )

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
        self.__preamble = preamble
        self.__dashstarts = dashstarts
        self.__thebibtext = None
        self.__replacer = None
        self.citation = []
        self.bibstyle = None
        self.bibdata = None
        self.bibcite = {}
        self.conversion_dict = {}

        # Makedir working directory if not exist.
        self.workdir.mkdir(exist_ok=True)

        if autostart:
            self.write()
            self.compile()

    def write(self, c, bib=None, bst=None):
        r"""Write .tex file.

        Write minimal .tex file into workdir.
        TeX file contains only citation contents,
        pre-defined (at constructor of LaTeX object) preamble,
        \\bibliography, and \\bibliographystyle.

        Parameters
        ----------
        c : str
            String data to be written in .tex file.
        bib : str or None
            Bibliography library file(s). If None, use all .bib files in cwd.
        bst : str or None
            Bibliography style. If None, use .bst file in cwd.

        Raises
        ------
        ValueError
            If bst is None and there is no or multiple .bst files in cwd.
        """
        import glob

        if bib is None:
            # Use only root name (file name without extension).
            bib = ''.join(
                [os.path.splitext(b)[0] for b in glob.glob('*.bib')]
            )

        if bst is None:
            bst = glob.glob('*.bst')
            if len(bst) > 1:
                raise ValueError(
                    'More than two .bst files found in working directory.'
                )
            elif len(bst) == 0:
                raise ValueError(
                    'No .bst files found in working directory.'
                )
            else:
                bst = bst[0]

        fn = self.workdir / (self.__targetbasename + '.tex')
        with codecs.open(fn, 'w', 'utf-8') as f:
            f.writelines(
                self.__preamble
                + '\\bibliographystyle{%s}\n' % bst
                + '\\begin{document}\n'
                + c
                + '\\bibliography{%s}\n' % bib
                + '\\end{document}\n'
            )

    def build(self):
        """Build LaTeX related files.

        Build LaTeX files in old-style four steps (without PDF generation).

        1. latex: to generate .aux from .tex

        2. bibtex: to generate .bbl and update .aux from .aux and .bst.

        3. latex: to update .aux.

        4. latex: to complete .aux.

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

        self.read_aux()
        self.read_bbl()
        self.__make_thebibliography_text()
        self.__get_replacer()

        os.chdir(cwd)  # Back to original working directory.

    @property
    def cnd(self):
        r"""Returns citation key to replacement number dictionary.

        Citation to Number Dictionary will be used to replace
        citation text in word file such as \\cite{key1} to
        number such ash [1].

        Returns
        -------
        dict
            Search key and replacement value.
        """
        return self.__replacer

    @property
    def tbt(self):
        r"""Plain text for replacement of bibliography list.

        A plain text of LaTeX-processed bibliography list.
        An tab string is inserted between each citenum and citation string.
        For example in IEEE format:

        | [1]\\tF. Author, S. Author, "Paper Title," Journal Name, vol. 1, no. 1, p. 1, march 2022.
        | [2]\\tG. Name, F. Name, "Title," Journal, vol. 2, no. 2, pp. 1-10, 2020.

        Returns
        -------
        str
            Plain text of the thebibliography.
        """  # noqa E501
        if self.__thebibtext is None:
            raise ValueError(
                'Thebibliography text is not set yet.'
            )
        return self.__thebibtext

    def __get_replacer(self):
        """Get key and value for replace word document.
        """
        replacer = dict()
        for k, v in self.conversion_dict.items():
            replacer.update({'\\\\cite\\{%s\\}' % k: '[%s]' % v})
        self.__replacer = replacer

    def read_bbl(self):
        """Read .bbl file.

        Read .bbl file to extract formatted thebibliography text.
        """
        fn = self.workdir / (self.__targetbasename + '.bbl')
        with codecs.open(fn, 'r', 'utf-8') as f:
            self.__bbldata = f.readlines()

    def __build_conversion_dict(self):
        r"""Prepare replaing citation keys with dashed range strings.

        Generate dictionary of such as {'refa,refb,refc,refe,refg': '1-3,5,7'}.
        """
        for cite in self.citation:
            cite_nums = [self.bibcite[c] for c in cite.split(',')]
            self.conversion_dict.update(
                {cite: self.__get_dashed_range(cite_nums)}
                )

    def __get_dashed_range(self, nums):
        r"""Convert multiple integers to dashed range string.

        Multiple integers are such as 1,2,3,6.
        And dashed rang strings are such as 1-3,6.

        Parameters
        ----------
        nums : list
            Multiple integers to convert dashed range string.
            A list of single element integer is also allowd.
        """
        seq = []
        final = []
        last = 0

        for index, val in enumerate(nums):

            if last + 1 == val or index == 0:
                seq.append(val)
                last = val
            else:
                if len(seq) > 2 and self.__dashstarts == 3:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq)-1]))
                elif len(seq) == 2 and self.__dashstarts == 3:
                    final.append(str(seq[0]) + ',' + str(seq[len(seq)-1]))
                elif len(seq) > 1 and self.__dashstarts == 2:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq)-1]))
                else:
                    final.append(str(seq[0]))
                    seq = []
                    seq.append(val)
                    last = val

            if index == len(nums) - 1:
                if len(seq) > 2 and self.__dashstarts == 3:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq)-1]))
                elif len(seq) == 2 and self.__dashstarts == 3:
                    final.append(str(seq[0]) + ',' + str(seq[len(seq)-1]))
                elif len(seq) > 1 and self.__dashstarts == 2:
                    final.append(str(seq[0]) + '-' + str(seq[len(seq)-1]))
                else:
                    final.append(str(seq[0]))

        final_str = ','.join(map(str, final))
        return final_str

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
        fn = self.workdir / (self.__targetbasename + '.aux')
        with codecs.open(fn, 'r', 'utf-8') as f:
            self.__auxdata = f.readlines()
        for line in self.__auxdata:
            self.__parse_line(line)
        self.__build_conversion_dict()

    def __parse_line(self, line):
        r"""Parse one line of .aux

        Parameters
        ----------
        line : str
            One line of .aux file to parse.
        """
        if line.startswith('\\citation'):
            self.citation.append(line[len('\\citation{'): -len('}\n')])
        elif line.startswith('\\bibstyle'):
            self.bibstyle = line[len('\\bibstyle{'): -len('}\n')]
        elif line.startswith('\\bibdata'):
            self.bibdata = line[len('\\bibdata{'): -len('}\n')]
        elif line.startswith('\\bibcite'):
            key, value = line[len('\\bibcite{'): -len('}\n')].split('}{')
            value = int(value)
            self.bibcite.update({key: value})

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
        for k, v in self.bibcite.items():
            thebibtext = re.sub(
                '\\\\bibitem{%s}\n' % k, '[%s]\t' % v, thebibtext
            )
        self.__thebibtext = thebibtext

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
