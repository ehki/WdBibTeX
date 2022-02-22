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
            targetbasename='wdbibtex',
            texcmd='latex',
            texopts='-interaction=nonstopmode -file-line-error',
            bibtexcmd='bibtex',
            bibtexopts='',
            preamble=defaultpreamble,
            autostart=False):
        self.__cwd = pathlib.Path(os.getcwd())
        self.__workdir = self.__cwd / workdir
        self.__workdir.mkdir(exist_ok=True)
        self.__targetbasename = targetbasename
        self.__texcmd = texcmd
        self.__bibtexcmd = bibtexcmd
        self.__bibtexopts = bibtexopts
        self.__texopts = texopts
        self.__preamble = preamble

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
