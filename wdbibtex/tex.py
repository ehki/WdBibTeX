import locale
import pathlib
import os


class TeXWrite:
    """TeX contents and commands.

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
            autostart=False):

        # Set automatically selected values
        if texcmd is None:
            if 'en' in locale.getlocale():
                texcmd = 'latex'
            elif 'ja' in locale.getlocale():
                texcmd = 'uplatex'
        if texopts is None:
            texopts = '-interaction=nonstopmode -file-line-error'
        if bibtexcmd is None:
            if 'en' in locale.getlocale():
                bibtexcmd = 'bibtex'
            elif 'ja' in locale.getlocale():
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

        # Makedir working directory if not exist.
        self.__workdir.mkdir(exist_ok=True)

        if autostart:
            self.write()
            self.compile()

    def write(self, contents):
        """Write .tex file.

        Parameters
        ----------
        contents : str
            String data to be written in .tex file.
        """
        with open(self.__workdir / (self.__targetbasename + '.tex'), 'w') as f:
            f.writelines(
                self.__preamble + '\\begin{document}\n'
                + contents + '\\end{document}\n'
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
        latexcmd = ' '.join(filter('', [
            self.__texcmd, self.__texopts,
            self.__targetbasename + '.tex'
        ]))
        bibtexcmd = ' '.join(filter('', [
            self.__bibtexcmd, self.__bibtexopts,
            self.__targetbasename,
        ]))
        subprocess.call(latexcmd, shell=True)
        subprocess.call(bibtexcmd, shell=True)
        subprocess.call(latexcmd, shell=True)
        subprocess.call(latexcmd, shell=True)
        os.chdir(cwd)
