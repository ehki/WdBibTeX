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
            texname='wdbibtex.tex',
            texcmd='latex',
            texopts='-interaction=nonstopmode -file-line-error',
            preamble=defaultpreamble,
            autostart=False):
        self.__cwd = pathlib.Path(os.getcwd())
        self.__auxdir = self.__cwd / auxdir
        self.__auxdir.mkdir(exist_ok=True)
        self.__texname = texname
        self.__texcmd = texcmd
        self.__texopts = texopts
        self.__preamble = preamble

        if autostart:
            self.write()
            self.compile()

    def write(self, contents):
        with open(self.__auxdir / self.__texname, 'w') as f:
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
                str(self.__auxdir / self.__texname),
            ])
        subprocess.call(cmd, shell=True)
        os.chdir(cwd)
