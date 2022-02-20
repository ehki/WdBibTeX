import os
import pathlib
import re


class Bbl():
    def __init__(
            self,
            auxdir='.aux',
            targetbasename='wdbibtex'
            ):
        self.__cwd = pathlib.Path(os.getcwd())
        self.__auxdir = self.__cwd / auxdir
        self.__auxdir.mkdir(exist_ok=True)
        self.__targetbasename = targetbasename

    def reference_text(self, replacer=None):
        """Returns reference plain text to incert word file.
        """
        if replacer is None:
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
        return ret_text

    def read_bbl(self):
        """Read .bbl file.
        """
        with open(self.__auxdir / (self.__targetbasename + '.bbl'), 'r') as f:
            self.__bbldata = f.readlines()
