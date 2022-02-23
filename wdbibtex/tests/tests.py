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
        ltx.write('Test contents')
        # The size will 94 kB
        self.assertEqual(os.path.getsize('.tmp/wdbib.tex'), 94)
        # Clear working directory
        shutil.rmtree('.tmp')

    def test_compile(self):
        ltx = wdbibtex.LaTeXHandler()
        ltx.write('Test contents')
        ltx.compile()
        # The size will 94 kB
        self.assertEqual(os.path.getsize('.tmp/wdbib.tex'), 94)
        # Clear working directory
        shutil.rmtree('.tmp')
