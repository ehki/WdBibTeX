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
        ltx = wdbibtex.LaTeXHandler()
        ltx.write('Test contents', bibstyle='ieeetr')
        # The size will 137 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.tex'), 137)
        # Clear working directory
        shutil.rmtree('.tmp')

    def test_compile(self):
        ltx = wdbibtex.LaTeXHandler()
        ltx.write('Test contents', bibstyle='ieeetr')
        ltx.compile()
        # The .tex size will 137 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.tex'), 137)
        # The .aux size will 61 B
        self.assertEqual(os.path.getsize('.tmp/wdbib.aux'), 61)
        # Clear working directory
        shutil.rmtree('.tmp')

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
        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)
