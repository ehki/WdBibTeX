import locale
import pathlib
import os

defaultpreamble = (
    '\\documentclass[10pt, a4paper, dvipdfmx, latex]{article}\n'
    '\\usepackage{cite}\n'
)

defaultbegindocument = (
    '\\begin{document}\n'
)

defaultenddocument = (
    '\\end{document}\n'
)


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
            preamble = defaultpreamble

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
        with open(self.__workdir / (self.__targetbasename + '.tex'), 'w') as f:
            f.writelines(
                self.__preamble + '\\begin{document}\n'
                + contents + '\\end{document}\n'
            )

    def compile(self):
        import subprocess
        cwd = os.getcwd()
        os.chdir(self.__workdir)
        cmd = ' '.join([
                self.__texcmd,
                self.__texopts,
                str(self.__workdir / (self.__targetbasename + '.tex')),
            ])
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)

    def bibtex(self):
        import subprocess
        cwd = os.getcwd()
        os.chdir(self.__workdir)
        cmd = ' '.join([
                self.__bibtexcmd,
                self.__bibtexopts,
                self.__targetbasename,
            ])
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)
