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
            texopts='',
            preamble=defaultbegindocument,
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

    def write(self):
        pass

    def compile(self):
        pass
