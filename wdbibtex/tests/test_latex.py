import itertools
import glob
import os
import pathlib
import pytest
import shutil
import subprocess
import time
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
        os.chdir(os.path.join(exampledir, 'first'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp')

        tx = wdbibtex.LaTeX()
        tx.set_bibliographystyle('ieeetr')

        tx.write('Test contents')

        # File check
        correct = [
            '\\bibliographystyle{ieeetr}\n',
            '\\begin{document}\n',
            'Test contents\n',
            '\\bibliography{library}\n',
            '\\end{document}\n',
        ]
        with open('.tmp/wdbib.tex', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents[1:]):
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
        os.chdir(os.path.join(exampledir, 'first'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp/')

        tx = wdbibtex.LaTeX()
        tx.set_bibliographystyle('ieeetr')

        tx.write('Test contents')
        tx.build()

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
        """Pass if LaTeX could build .tex with citation.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'first'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp/')

        tx = wdbibtex.LaTeX()
        tx.set_bibliographystyle('ieeetr')

        tx.write(
            'Test contents with one citation \\cite{enArticle1}.'
        )
        tx.build()

        # File check
        correct = [
            '\\bibliographystyle{ieeetr}\n',
            '\\begin{document}\n',
            'Test contents with one citation \\cite{enArticle1}.\n',
            '\\bibliography{library}\n',
            '\\end{document}\n',
        ]
        with open('.tmp/wdbib.tex', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents[1:]):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            '\\relax \n',
            '\\bibstyle{ieeetr}\n',
            '\\citation{enArticle1}\n',
            '\\bibdata{library}\n',
            '\\bibcite{enArticle1}{1}\n',
            '\\gdef \\@abspage@last{1}\n',
        ]
        with open('.tmp/wdbib.aux', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            '\\begin{thebibliography}{1}\n',
            '\n',
            '\\bibitem{enArticle1}\n',
            "I.~Yamada, J.~Yamada, S.~Yamada, and S.~Yamada, ``Title1,'' {\\em Japanese\n",   # noqa #E501
            '  Journal}, vol.~15, pp.~20--30, march 2019.\n',
            '\n',
            '\\end{thebibliography}\n',
        ]
        with open('.tmp/wdbib.bbl', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Parse test for aux file.
        tx.read_aux()
        self.assertEqual(
            tx.cite('\\cite{enArticle1}'),
            '[1]'
        )

        # Parse bbl file.
        bb = wdbibtex.Bibliography()
        bb.read_bbl()
        self.assertEqual(
            bb.thebibliography,
            u"[1]\tI. Yamada, J. Yamada, S. Yamada, and S. Yamada, "
            u"“Title1,” Japanese Journal, vol. 15, pp. 20\u201430, "
            u"march 2019.\n"
        )
        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)

    def test_multiple_citations_compile_citation(self):
        """Pass if multiple citations are collectly converted.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'ieejtran'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp/')

        tx = wdbibtex.LaTeX()
        tx.set_bibliographystyle('ieeetr')
        # tx.add_package('cite')

        contents = (
            'Test contents with one citation \\cite{enArticle1}.\n'
            'Another citation \\cite{enArticle2}.\n'
            'Multiple citations in one citecommand '
            '\\cite{enArticle1,enArticle3}'
        )
        tx.write(contents)
        tx.parse_context(contents)

        tx.build()

        # File check
        correct = [
            # '\\usepackage{cite}\n',
            '\\bibliographystyle{ieeetr}\n',
            '\\begin{document}\n',
            'Test contents with one citation \\cite{enArticle1}.\n',
            'Another citation \\cite{enArticle2}.\n',
            'Multiple citations in one citecommand \\cite{enArticle1,enArticle3}\n',   # noqa #E501
            '\\bibliography{library}\n',
            '\\end{document}\n',
        ]
        with open('.tmp/wdbib.tex', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents[1:]):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            '\\relax \n',
            '\\bibstyle{ieeetr}\n',
            '\\citation{enArticle1}\n',
            '\\citation{enArticle2}\n',
            '\\citation{enArticle1}\n',
            '\\citation{enArticle3}\n',
            '\\bibdata{library}\n',
            '\\bibcite{enArticle1}{1}\n',
            '\\bibcite{enArticle2}{2}\n',
            '\\bibcite{enArticle3}{3}\n',
            '\\gdef \\@abspage@last{1}\n',
        ]
        with open('.tmp/wdbib.aux', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            "\\begin{thebibliography}{1}\n",
            "\n",
            "\\bibitem{enArticle1}\n",
            "I.~Yamada, J.~Yamada, S.~Yamada, and S.~Yamada, ``Title1,'' {\\em Japanese\n",  # noqa #E501
            "  Journal}, vol.~15, pp.~20--30, march 2019.\n",
            "\n",
            "\\bibitem{enArticle2}\n",
            "G.~Yamada and R.~Yamada, ``Title2,'' {\\em Japanese Journal}, vol.~15, p.~21,\n",   # noqa #E501
            "  dec. 2019.\n",
            "\n",
            "\\bibitem{enArticle3}\n",
            "G.~Yamada and R.~Yamada, ``Title2 is true?,'' {\\em IEEE Transactions on Pattern\n",   # noqa #E501
            "  Analysis and Machine Intelligence}, nov 2018.\n",
            "\n",
            "\\end{thebibliography}\n",
        ]
        with open('.tmp/wdbib.bbl', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Parse test for aux file.
        tx.read_aux()
        self.assertEqual(
            tx.cite('\\cite{enArticle1}'),
            '[1]'
        )
        self.assertEqual(
            tx.cite('\\cite{enArticle2}'),
            '[2]'
        )
        self.assertEqual(
            tx.cite('\\cite{enArticle1,enArticle3}'),
            '[1,3]'
        )

        bb = wdbibtex.Bibliography()
        bb.read_bbl()
        self.assertEqual(
            bb.thebibliography,
            (u"[1]\tI. Yamada, J. Yamada, S. Yamada, and S. Yamada, “Title1,” "
             u"Japanese Journal, vol. 15, pp. 20—30, march 2019.\n"
             u"[2]\tG. Yamada and R. Yamada, “Title2,” Japanese Journal, "
             u"vol. 15, p. 21, dec. 2019.\n"
             u"[3]\tG. Yamada and R. Yamada, “Title2 is true?,” "
             u"IEEE Transactions "
             u"on Pattern Analysis and Machine Intelligence, nov 2018.\n")
        )
        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)


class TestBstHandling:
    def test_set_bst(self):
        tx = wdbibtex.LaTeX()
        tx.set_bibliographystyle('ieeetr')
        assert tx.bibliographystyle == 'ieeetr'
        assert tx.formatted_bibliographystyle == r'\bibliographystyle{ieeetr}'

    def test_set_wrong_bst(self):
        tx = wdbibtex.LaTeX()
        with pytest.raises(ValueError):
            tx.set_bibliographystyle(r'\bibliographystyle{ieeetr}')

    def test_set_auto_bst(self, touch_bst):
        tx = wdbibtex.LaTeX()
        tx.bibliographystyle = None
        assert tx.bibliographystyle == 'testbst'

    @pytest.fixture(scope='function')
    def touch_bst(self):
        fb = pathlib.Path('.tmp/testbst.bst')
        fb.touch()
        yield None
        fb.unlink(True)
        dirpath = pathlib.Path('.tmp')
        if dirpath.exists() and dirpath.is_dir():
            shutil.rmtree(dirpath)


class TestExamples:

    def test_gen_first(self, chdir_first):
        p = subprocess.run(['python', 'docxgen.py'])
        assert p.returncode == 0
        time.sleep(0.5)

    def test_run_first(self, chdir_first):
        p = subprocess.run(
            ['python', '-m', 'wdbibtex', 'sample.docx', '--bst', 'ieeetr']
        )
        assert p.returncode == 0
        time.sleep(0.5)

    @pytest.fixture(scope='function')
    def chdir_first(self):
        cwd = os.getcwd()
        os.chdir('examples/first')
        yield None
        os.chdir(cwd)
