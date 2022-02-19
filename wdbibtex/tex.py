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
    def __init__(
            self,
            auxdir='.aux',
            targetbasename='wdbibtex',
            texcmd='latex',
            texopts='-interaction=nonstopmode -file-line-error',
            bibtexcmd='bibtex',
            bibtexopts='',
            preamble=defaultpreamble,
            autostart=False):
        self.__cwd = pathlib.Path(os.getcwd())
        self.__auxdir = self.__cwd / auxdir
        self.__auxdir.mkdir(exist_ok=True)
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
        with open(self.__auxdir / (self.__targetbasename + '.tex'), 'w') as f:
            f.writelines(
                self.__preamble + '\\begin{document}\n'
                + contents + '\\end{document}\n'
            )

    def compile(self):
        import subprocess
        cwd = os.getcwd()
        os.chdir(self.__auxdir)
        cmd = ' '.join([
                self.__texcmd,
                self.__texopts,
                str(self.__auxdir / (self.__targetbasename + '.tex')),
            ])
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)

    def bibtex(self):
        import subprocess
        cwd = os.getcwd()
        os.chdir(self.__auxdir)
        cmd = ' '.join([
                self.__bibtexcmd,
                self.__bibtexopts,
                self.__targetbasename,
            ])
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)
