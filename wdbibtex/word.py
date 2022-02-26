import os
import pathlib
import shutil
import win32com.client as client

import wdbibtex


class WdBibTeX:
    """MS Word's BibTeX toolkit.
    
    WdBibTeX is a MS Word wrapper for BibTeX citation conversion.

    Parameters
    ----------
    file : str
        Target word file with .docx extension.
    copy_suffix : str, default '_bib'
        Appended text to a copied word file.
        WdBibTeX operates the copied file.
    workdir : '.tmp'
        Working directory of latex process.
        The working directory will be removed by WdBibTeX.clean().
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
        self.__ltx = wdbibtex.LaTeX(workdir=self.__workdir)

    def close(self, cleanup=False):
        """Close word file and word application.

        Close word file after saving.
        If no other file opened, quit Word application too.

        Parameters
        ----------
        cleanup : bool, default False
            If True, remove working directory of latex process.
        """

        # Save document
        self.__dc.Save()

        # Close document
        self.__dc.Close()

        #  Quit Word application if no other opened document
        if len(self.__ap.Documents) == 0:
            self.__ap.Quit()

        if cleanup:
            shutil.rmtree(self.__ltx.workdir)

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

        self.open_doc()
        self.__cites = self.find_all('\\\\cite\\{*\\}')
        self.__thebibliographies = self.find_all('\\\\thebibliography')

        # Build latex document
        context = '\n'.join([cite for cite, _, _ in self.__cites])
        self.__ltx.write(context, bibfile=bib, bibstyle=bst)
        self.__ltx.compile()

        # Replace \thebibliography
        for _, start, end in self.__thebibliographies[::-1]:
            rng = self.__dc.Range(Start=start, End=end)
            rng.Delete()
            rng.InsertAfter(self.__ltx.thebibliography_text)

        # Replace \cite{*}
        for key, val in self.__ltx.get_replacer().items():
            if 'thebibliography' in key:
                continue
            self.replace_all(key, val)

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
        return sorted(found, key=lambda x: x[1])

    def open_doc(self):
        """Open copied word document.

        Copy word file with appending suffix.
        Then open the file.
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
