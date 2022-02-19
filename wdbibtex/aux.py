import pathlib
import os


class AuxParser():
    def __init__(
            self,
            auxdir='.aux',
            targetbasename='wdbibtex',
            ):
        self.__cwd = pathlib.Path(os.getcwd())
        self.__auxdir = self.__cwd / auxdir
        self.__auxdir.mkdir(exist_ok=True)
        self.__targetbasename = targetbasename
        self.citation = []
        self.bibstyle = None
        self.bibdata = None
        self.bibcite = {}

    def parse_aux(self):
        with open(self.__auxdir / (self.__targetbasename + '.aux'), 'r') as f:
            self.__auxdata = f.readlines()
        for line in self.__auxdata:
            self.parse_line(line)

    def parse_line(self, line):
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
