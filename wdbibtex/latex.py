import locale
import pathlib
import os
import re


class LaTeXHandler:
    """LaTeX related contents and commands.

    Parameters
    ----------
    workdir : str, default .tmp
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

    Attributes
    ----------
    bibcite : str
        The mapping of citation-key and citation-number. This field is
        generated in second latex command of general compile routine
        of latex -> bibtex -> latex -> latex -> dvipdfmx.
    bibdata : str
        The bibliography data given in tex file. Although BibTeX command use
        this field, AuxParser class does not use.
    bibstyle : str
        The bibliographystyle of tex file. Although BibTeX command use this
        field, AuxParser class does not use.
    citation : list
        Citation keys written in tex file. For example, in case two citation
        commands of \\cite{ref1,ref2,ref3} and \\cite{ref4} are in the Word
        file, citation will become ['ref1,ref2,ref3', 'ref4'].
    conversion_dict : dict
        Conversion mapping from citation keys to numbers. For example,
        {'ref1,ref2,ref3': '1-3', 'ref4': '4'}
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

        # Set automatically selected values
        if texcmd is None:
            if True in ['en' in loc for loc in locale.getlocale()]:
                texcmd = 'latex'
            elif True in ['ja' in loc for loc in locale.getlocale()]:
                texcmd = 'uplatex'
        if texopts is None:
            texopts = '-interaction=nonstopmode -file-line-error'
        if bibtexcmd is None:
            if True in ['en' in loc for loc in locale.getlocale()]:
                bibtexcmd = 'bibtex'
            elif True in ['ja' in loc for loc in locale.getlocale()]:
                bibtexcmd = 'upbibtex'
        if bibtexopts is None:
            bibtexopts = ''
        if preamble is None:
            preamble = (
                '\\documentclass[latex]{article}\n'
                '\\usepackage{cite}\n'
            )

        # Store settings in internal attributes.
        self.__cwd = pathlib.Path(os.getcwd())
        self.__workdir = self.__cwd / workdir
        self.__targetbasename = targetbasename
        self.__texcmd = texcmd
        self.__texopts = texopts
        self.__bibtexcmd = bibtexcmd
        self.__bibtexopts = bibtexopts
        self.__preamble = preamble
        self.__dashstarts = dashstarts
        self.citation = []
        self.bibstyle = None
        self.bibdata = None
        self.bibcite = {}
        self.conversion_dict = {}

        # Makedir working directory if not exist.
        self.__workdir.mkdir(exist_ok=True)

        if autostart:
            self.write()
            self.compile()

    def write(self, contents, bibfile=None, bibstyle=None):
        """Write .tex file.

        Parameters
        ----------
        contents : str
            String data to be written in .tex file.
        bibfile : str or None
            Bibliography library file(s). If None, use all .bib files in cwd.
        bibstyle : str or None
            Bibliography style. If None, use .bst file in cwd.

        Raises
        ------
        ValueError
            If bibstyle is None and there is no or multiple .bst files in cwd.
        """
        import glob

        if bibfile is None:
            # Use only root name (file name without extension).
            # As .tex, .aux, .bbl are placed in temporary directory,
            # relative path to .bib is one layer above from .tex file.
            bibfile = ''.join(
                ['../' + os.path.splitext(b)[0] for b in glob.glob('*.bib')]
            )
            print(bibfile)

        if bibstyle is None:
            bibstyle = glob.glob('*.bst')
            if len(bibstyle) > 1:
                raise ValueError(
                    'More than two .bst files found in working directory.'
                )
            elif len(bibstyle) == 0:
                raise ValueError(
                    'No .bst files found in working directory.'
                )
            else:
                bibstyle = '../' + bibstyle[0]

        with open(self.__workdir / (self.__targetbasename + '.tex'), 'w') as f:
            f.writelines(
                self.__preamble
                + '\\bibliographystyle{%s}\n' % bibstyle
                + '\\begin{document}\n'
                + contents
                + '\\bibliography{%s}\n' % bibfile
                + '\\end{document}\n'
            )

    def compile(self):
        """Compile LaTeX related files.

        Compile LaTeX files in old-style four steps (without PDF generation).
        1. latex: to generate .aux from .tex
        2. bibtex: to generate .bbl and update .aux from .aux and .bst.
        3. latex: to update .aux.
        4. latex: to complete .aux.
        """
        import subprocess
        cwd = os.getcwd()
        os.chdir(self.__workdir)
        latexcmd = ' '.join(filter(None, [
            self.__texcmd, self.__texopts,
            self.__targetbasename + '.tex'
        ]))
        bibtexcmd = ' '.join(filter(None, [
            self.__bibtexcmd, self.__bibtexopts,
            self.__targetbasename,
        ]))
        subprocess.call(latexcmd, shell=True)
        subprocess.call(bibtexcmd, shell=True)
        subprocess.call(latexcmd, shell=True)
        subprocess.call(latexcmd, shell=True)
        os.chdir(cwd)

    def get_thebibliography_text(self):
        """Returns thebibliography plain text to incert word file.
        """
        replacer = {}
        replacer.update({
            r'\n  ': ' ',
            r'\{\\em (.*)\}': r'\1',
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
        ret_text = ''.join(self.__bbldata[thebib_begin: thebib_end])
        for k, v in replacer.items():
            ret_text = re.sub(k, v, ret_text)
        for k, v in self.bibcite.items():
            ret_text = re.sub('\\\\bibitem{%s}\n' % k, '[%s]\t' % v, ret_text)
        return ret_text

    def read_bbl(self):
        """Read .bbl file.
        """
        with open(self.__workdir / (self.__targetbasename + '.bbl'), 'r') as f:
            self.__bbldata = f.readlines()

    def build_conversion_dict(self):
        r"""Prepare replaing citation keys with dashed range strings.
        Generate dictionary of such as {'refa,refb,refc,refe,refg': '1-3,5,7'}.
        """
        for cite in self.citation:
            cite_nums = [self.bibcite[c] for c in cite.split(',')]
            self.conversion_dict.update(
                {cite: self.get_dashed_range(cite_nums)}
                )

    def get_dashed_range(self, nums):
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

    def parse_aux(self):
        r"""Parse entire .aux file.
        """
        with open(self.__workdir / (self.__targetbasename + '.aux'), 'r') as f:
            self.__auxdata = f.readlines()
        for line in self.__auxdata:
            self.parse_line(line)
        self.build_conversion_dict()

    def parse_line(self, line):
        r"""Parse one line of .aux
        \\citation{citation_key} will appended to the citation key as
        str(citation_key).
        \\bibstyle{style_file} will be saved as bibstyle attribute.
        \\bibdata{path_to_data} will be saved as bibdata attribute.
        \\bibcite{one_citation_key}{citation_number} will be saved as
        dictionary of {one_citation_key: citation_number} to decide how
        replace citation_keys of such as 'key1,key2,key3' to dashed citation
        numbers of such as '2-4'.

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
