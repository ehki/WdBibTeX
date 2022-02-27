import itertools
import glob
import os
import shutil
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import wdbibtex  # noqa E402


class TestLaTeX(unittest.TestCase):
    """Test cases for LaTeX compile and result extraction.
    """

    def test_write(self):
        """Pass if LaTeX class could correctly write .tex file.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example1'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp')

        ltx = wdbibtex.LaTeX()
        ltx.write('Test contents\n', bst='ieeetr')

        # File check
        correct = [
            '\\documentclass[latex]{article}\n',
            '\\usepackage{cite}\n',
            '\\bibliographystyle{ieeetr}\n',
            '\\begin{document}\n',
            'Test contents\n',
            '\\bibliography{library}\n',
            '\\end{document}\n',
        ]
        with open('.tmp/wdbib.tex', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Clear working directory
        shutil.rmtree('.tmp/')
        os.chdir(cwd)

    def test_build(self):
        """Pass if LaTeX class could build project.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example1'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp/')

        ltx = wdbibtex.LaTeX()
        ltx.write('Test contents\n', bst='ieeetr')
        ltx.build()

        # File check
        correct = [
            '\\relax \n',
            '\\bibstyle{ieeetr}\n',
            '\\bibdata{library}\n',
            '\\gdef \\@abspage@last{1}\n',
        ]
        with open('.tmp/wdbib.aux', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)

    def test_compile_citation(self):
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example1'))
        ltx = wdbibtex.LaTeXHandler()
        ltx.write(
            'Test contents with one citation \\cite{enArticle1}.\n',
            bibstyle='ieeetr')
        ltx.compile()
        # The .tex size will 185 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.tex'), 185)
        # The .aux size will 117 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.aux'), 117)
        # The .bbl size will 191 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.bbl'), 191)
        with open('.tmp/wdbib.tex', 'r') as f:
            print(''.join(f.readlines()))
        with open('.tmp/wdbib.aux', 'r') as f:
            print(''.join(f.readlines()))
        with open('.tmp/wdbib.bbl', 'r') as f:
            print(''.join(f.readlines()))

        # Parse test for aux file.
        ltx.parse_aux()
        ltx.build_conversion_dict()
        self.assertEqual(ltx.conversion_dict['enArticle1'], '1')

        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)

    def test_multiple_citations_compile_citation(self):
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example2'))
        ltx = wdbibtex.LaTeXHandler()
        ltx.write(
            ('Test contents with one citation \\cite{enArticle1}.\n'
             'Another citation \\cite{enArticle2}.\n'
             'Multiple citations in one citecommand '
             '\\cite{enArticle1,enArticle3}\n'),
            bibstyle='ieeetr')
        ltx.compile()
        # The .tex size will 288 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.tex'), 288)
        # The .aux size will 220 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.aux'), 220)
        # The .bbl size will 453 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.bbl'), 453)
        with open('.tmp/wdbib.tex', 'r') as f:
            print(''.join(f.readlines()))
        with open('.tmp/wdbib.aux', 'r') as f:
            print(''.join(f.readlines()))
        with open('.tmp/wdbib.bbl', 'r') as f:
            print(''.join(f.readlines()))

        # Parse test for aux file.
        ltx.parse_aux()
        ltx.build_conversion_dict()
        print(ltx.conversion_dict)
        self.assertEqual(ltx.conversion_dict['enArticle1'], '1')
        self.assertEqual(ltx.conversion_dict['enArticle2'], '2')
        self.assertEqual(ltx.conversion_dict['enArticle1,enArticle3'], '1,3')
        ltx.read_bbl()
        print(ltx.get_thebibliography_text())
        self.assertEqual(len(ltx.get_thebibliography_text()), 318)
        print(ltx.get_replacer())
        self.assertEqual(len(str(ltx.get_replacer())), 463)

        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)
