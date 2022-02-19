import pathlib
import os


class AuxParser():
    """Store contents of aux and connect citation keys with citation numbers.

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
        """Prepare replaing citation keys with dashed range strings.
        Generate dictionary of such as {'refa,refb,refc,refe,refg': '1-3,5,7'}.
        """
        for cite in self.citation:
            cite_nums = [self.bibcite[c] for c in cite.split(',')]
            self.conversion_dict.update(
                {cite: self.get_dashed_range(cite_nums)}
                )

    def get_dashed_range(self, nums):
        """Convert multiple integers to dashed range string.
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
        """Parse entire .aux file.
        """
        with open(self.__auxdir / (self.__targetbasename + '.aux'), 'r') as f:
            self.__auxdata = f.readlines()
        for line in self.__auxdata:
            self.parse_line(line)
        self.build_conversion_dict()

    def parse_line(self, line):
        """Parse one line of .aux
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
