import glob
import os
import pathlib
import shutil
import win32com.client as client

import wdbibtex


class WdBibTeX:
    """BibTeX toolkit for MS Word.

    WdBibTeX is a MS Word wrapper for BibTeX citation conversion.
    WdBibTeX extracts LaTeX and BibTeX commands from a Word file,
    and copies them to dummy .tex file in working directory.
    By building LaTeX project with old-style LaTeX+BibTeX process,
    WdBibTeX obtain BibTeX-processed bibliography texts
    and citation numbers.
    Finally, WdBibTeX replaces original LaTeX and BibTeX commands
    in Word file with BibTeX-processed bibliography textx
    and citation numbers.

    Parameters
    ----------
    file : str or path object
        Target word file with .docx extension.
    copy_suffix : str, default '_bib'
        Appended text to a copied word file.
        WdBibTeX operates the copied file for safety.
    workdir : str or path object, default '.tmp'
        Working directory of latex process.
        The working directory will be removed by WdBibTeX.clear().

    Examples
    --------
    >>> from wdbibtex import WdBibTeX
    >>> wd = WdBibTeX('sample.docx')  # doctest: +SKIP
    >>> wd.build()  # doctest: +SKIP
    >>> wd.close()  # doctest: +SKIP
    """

    def __init__(
            self,
            file,
            copy_suffix='_bib',
            workdir='.tmp',
    ):
        """Costructor of WdBibTeX.
        """
        self.__origin_file = file
        self.__origin_file = (pathlib.Path.cwd() / file).resolve()
        self.__docxdir = self.__origin_file.parent
        self.__target_file = self.__docxdir / (
            str(self.__origin_file.stem)
            + copy_suffix
            + str(self.__origin_file.suffix)
        )
        self.__workdir = self.__docxdir / workdir

    @property
    def original_file(self):
        """[Read only] Returns original word file.
        """
        return self.__target_file

    @property
    def target_file(self):
        """[Read only] Returns operating word file.
        """
        return self.__target_file

    @property
    def workdir(self):
        """[Read only] Returns LaTeX working directory.
        """
        return self.__workdir

    def clear(self):
        """Clear auxiliary files on working directory.
        """
        shutil.rmtree(self.workdir)

    def close(self, clear=False):
        """Close word file and word application.

        Close word file after saving.
        If no other file opened, quit Word application too.

        Parameters
        ----------
        clear : bool, default False
            If True, remove working directory of latex process.

        See also
        --------
        open : Open word file.
        """

        # Save document
        self.__dc.Save()

        # Close document
        self.__dc.Close()

        #  Quit Word application if no other opened document
        if len(self.__ap.Documents) == 0:
            self.__ap.Quit()

        # Clean working directory
        if clear:
            self.clear()

    def exportpdf(self):
        """Export current docx file to pdf.
        """
        fn = os.path.splitext(self.__target_file)[0] + '.pdf'
        self.__dc.SaveAs2(fn, 17)  # 17: wdFormatPDF

    def build(self, bib=None, bst=None):
        r"""Build word file with latex citations.

        Build word file with latex citation key of \\cite{} and \\thebibliography.
        This is realized by the following five steps:

        1. Find latex citations and thebibliography key.
        2. Generate dummy LaTeX file.
        3. Build LaTeX project.
        4. Parse LaTeX artifacts of aux and bbl.
        5. Replace LaTeX keys in word file.

        Parameters
        ----------
        bib : str or None, default None
            Bibliography file to be used. If None, all .bib files placed in the same directory of target .docx file will be used.
        bst : str or None, default None
            Bibliography style. If None, .bst file placed in the same directory of target .docx file is used.
        """  # noqa E501

        self.open()
        os.makedirs(self.__workdir, exist_ok=True)
        for b in glob.glob(os.path.join(self.__docxdir, '*.bst')):
            shutil.copy(b, self.__workdir)
        for b in glob.glob(os.path.join(self.__docxdir, '*.bib')):
            shutil.copy(b, self.__workdir)
        tx = wdbibtex.LaTeX(workdir=self.__workdir)
        tx.preamble = self.read_preamble()

        if bst:
            # Overwrite preamble in docx with given command line artument.
            tx.bibliographystyle = bst
        else:
            # Try setting default bibliographystyle=None.
            # Try find .bst in th project directory.
            tx.bibliographystyle = tx.bibliographystyle

        self.__cites = self.find_all('\\\\cite\\{*\\}')
        self.__thebibliographies = self.find_all('\\\\thebibliography')

        # Build latex document
        context = '\n'.join([cite for cite, _, _ in self.__cites])
        tx.write(context, bib=bib)
        tx.build()
        tx.read_aux()
        tx.read_bbl()

        # Replace \thebibliography
        for _, start, end in self.__thebibliographies[::-1]:
            rng = self.__dc.Range(Start=start, End=end)
            rng.Delete()
            rng.InsertAfter(tx.thebibliography)

        # Replace \cite{*}
        # for key, val in ct.cnd.items():
        superscript = (
            isinstance(tx.is_package_used('cite'), list)
            and (
                'superscript' in tx.is_package_used('cite')
                or 'super' in tx.is_package_used('cite')
            )
        )
        for key, start, end in self.__cites[::-1]:
            if superscript:
                rng = self.__dc.Range(Start=start, End=end)
                rng.Font.Superscript = True
            key_escaped = key.replace('\\', '\\\\')
            key_escaped = key_escaped.replace('{', '\\{')
            key_escaped = key_escaped.replace('}', '\\}')
            self.replace_all(key_escaped, tx.cite(key))

        # Replace from \begin{preamble} to \end{preamble}^13
        # Note ^13 corresponds carriage return.
        self.replace_all(
            '\\\\begin\\{preamble\\}*\\\\end\\{preamble\\}^13',
            ''
        )

    def find_all(self, key):
        """Find all keys from word file.

        Find all keys in word document.
        Searching starts from current selection and wrapped
        if reach document end.
        MatchFuzzy search is disabled.

        Parameters
        ----------
        key : str
            A text to search in word document.

        Returns
        -------
        list
            A list of list. Each list element is
            [found text in str, start place in int, end place in int].
            The list is sorted by second key (i.e. start place).

        See Also
        --------
        replace_all : Replace found keys.
        """

        self.__fi = self.__sl.Find
        self.__fi.ClearFormatting()
        self.__fi.MatchFuzzy = False
        found = []
        while True:
            self.__fi.Execute(
                key,  # FindText
                False,  # MatchCase
                False,  # MatchWholeWord
                True,  # MatchWildcards
                False,  # MatchSoundsLike
                False,  # MatchAllWordForms
                True,  # Forward
                1,  # Wrap
                False,  # Format
                '',  # ReplaceWith
                0,  # Replace, 0: wdReplaceNone
            )
            line = [
                str(self.__sl.Range),
                self.__sl.Range.Start,
                self.__sl.Range.End
            ]
            if line in found:
                break
            found.append(line)

        for i in range(self.__dc.Shapes.Count):
            self.__dc.Shapes(i+1).Select()
            wholeshpe = self.__sl.Range
            self.__fi = self.__sl.Find
            self.__fi.ClearFormatting()
            self.__fi.MatchFuzzy = False
            searched = []
            while True:
                self.__fi.Execute(
                    key,  # FindText
                    False,  # MatchCase
                    False,  # MatchWholeWord
                    True,  # MatchWildcards
                    False,  # MatchSoundsLike
                    False,  # MatchAllWordForms
                    True,  # Forward
                    1,  # Wrap
                    False,  # Format
                    '',  # ReplaceWith
                    0,  # Replace, 0: wdReplaceNone
                )
                line = [
                    str(self.__sl.Range),
                    self.__sl.Range.Start,
                    self.__sl.Range.End
                ]
                if line in searched:
                    break
                else:
                    searched.append(line)
                if line in found:
                    break
                if line[0] == '':
                    continue
                if line[0] == str(wholeshpe):
                    continue
                found.append(line)

        self.__sl.HomeKey(6)
        if len(found) >= 2:
            try:
                found.remove(['', 0, 0])
            except ValueError:
                pass
        return sorted(found, key=lambda x: x[1])

    def open(self):
        """Open copied word document.

        Firstly copy word file with appending suffix.
        Then open the file.

        See also
        --------
        close : Close document and application.
        """

        self.__ap = client.Dispatch('Word.Application')
        self.__ap.Visible = True

        # Copy original file to operating file for safety.
        try:
            shutil.copy2(self.__origin_file, self.__target_file)
        except PermissionError:
            for d in self.__ap.Documents:
                docpath = str(os.path.join(d.Path, d.Name))
                if docpath == str(self.__target_file):
                    d.Close(SaveChanges=-1)  # wdSaveChanges
                    break
            shutil.copy2(self.__origin_file, self.__target_file)

        self.__dc = self.__ap.Documents.Open(str(self.__target_file))
        self.__sl = self.__ap.Selection

    def read_preamble(self):
        r"""Read preamble contents if exists.

        WdBibTeX detects special command of \begin{preamble} and \end{preamble}
        commands from target .docx file. Contents written in the two commands
        will be copied to the preamble of .tex file. If these commands did not
        be found, the following default preamble is used.

        .. code-block:: text

            \documentclass[latex]{article}
            \usepackage{cite}

        Returns
        -------
        None or str
            None if no preamble texts exists, str if preamble exists.

        Raises
        ------
        ValueError
            If only one of \begin{preamble} or \end{preamble} found in file.
            Or, if two or more \begin{preamble} or \end{preamble} found.
        """
        bgn_pa = self.find_all("\\\\begin\\{preamble\\}")
        end_pa = self.find_all("\\\\end\\{preamble\\}")
        if bgn_pa == [['', 0, 0]] and end_pa == [['', 0, 0]]:
            return None
        elif bgn_pa == [['', 0, 0]] or end_pa == [['', 0, 0]]:
            raise ValueError(
                'One of \\begin{preamble} or \\end{preamble} not found.'
            )
        elif (len(bgn_pa) > 1 or len(end_pa) > 1):
            raise ValueError(
                'Two or more \\begin{preamble} or \\end{preamble} found.'
            )
        pa = self.__dc.Range(
            Start=bgn_pa[0][2],
            End=end_pa[0][1]
        )
        return str(pa).replace('\r', '\n')

    def replace_all(self, key, val):
        """Replace all keys in document with value.

        Replace all keys in word document with value.
        Searching starts from current selection and wrapped
        if reach document end.
        MatchFuzzy search is disabled.

        Parameters
        ----------
        key : str
            Original text.
        val : str
            Replacing text.

        See Also
        --------
        find_all : Find all keys in the document.
        """
        self.__fi = self.__sl.Find
        self.__fi.ClearFormatting()
        self.__fi.MatchFuzzy = False
        self.__fi.Execute(
            key,  # FindText
            False,  # MatchCase
            False,  # MatchWholeWord
            True,  # MatchWildcards
            False,  # MatchSoundsLike
            False,  # MatchAllWordForms
            True,  # Forward
            1,  # Wrap, 1: wdFindContinue
            False,  # Format
            val,  # ReplaceWith
            2,  # Replace, 2: wdReplaceAll
        )
        for i in range(self.__dc.Shapes.Count):
            self.__dc.Shapes(i+1).Select()
            self.__fi = self.__sl.Find
            self.__fi.ClearFormatting()
            self.__fi.MatchFuzzy = False
            self.__fi.Execute(
                key,  # FindText
                False,  # MatchCase
                False,  # MatchWholeWord
                True,  # MatchWildcards
                False,  # MatchSoundsLike
                False,  # MatchAllWordForms
                True,  # Forward
                1,  # Wrap, 1: wdFindContinue
                False,  # Format
                val,  # ReplaceWith
                2,  # Replace, 2: wdReplaceAll
            )
