import pathlib
import os


class AuxParser():
    def __init__(
            self,
            auxdir='.aux',
            targetbasename='wdbibtex',
            dashstarts=3,
            ):
        assert dashstarts in (2, 3), (
            'Invalid dashstarts. Only integer 2 or 3 is allowed.'
            )
        self.__cwd = pathlib.Path(os.getcwd())
        self.__auxdir = self.__cwd / auxdir
        self.__auxdir.mkdir(exist_ok=True)
        self.__targetbasename = targetbasename
        self.__dashstarts = dashstarts
        self.citation = []
        self.bibstyle = None
        self.bibdata = None
        self.bibcite = {}
        self.conversion_dict = {}

    def build_conversion_dict(self):
        for cite in self.citation:
            cite_nums = [self.bibcite[c] for c in cite.split(',')]
            self.conversion_dict.update(
                {cite: self.get_dashed_range(cite_nums)}
                )

    def get_dashed_range(self, nums):
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
        with open(self.__auxdir / (self.__targetbasename + '.aux'), 'r') as f:
            self.__auxdata = f.readlines()
        for line in self.__auxdata:
            self.parse_line(line)
        self.build_conversion_dict()

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
