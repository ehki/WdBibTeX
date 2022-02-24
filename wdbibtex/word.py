import os
import shutil
import win32com.client as client

import wdbibtex


class WdBibTeX:
    """Word wrapper for BibTeX citation conversion.

    Parameters
    ----------
    file : str
        Target word file with .docx extension.
    copy_suffix : str, default '_bib'
        Appended text to a copied word file.
    workdir : '.tmp'
        Working directory of latex process.
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
        self.__origin_file = os.path.abspath(self.__origin_file)
        dn, fn = os.path.split(self.__origin_file)
        bn, ex = os.path.splitext(fn)
        self.__target_file = os.path.join(dn, bn+copy_suffix+ex)
        self.__ltx = wdbibtex.LaTeXHandler(workdir=workdir)

    def close(self, cleanup=False):
        """Close file after saving. If applicable, quit Word App too.

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

    def compile(self, bibfile=None, bibstyle=None):
        """Compile latex-citations-including word file.

        Firstly, find latex citations and thebibliography key.
        Secondly, make dummy latex file and build.
        Thirdly, replace latex citations and thebibliography
        with latex-processed texts.

        Parameters
        ----------
        bibfile : str | None, default None
            Bibliography file to be used. If None, all .bib files placed in the same directory of target .docx file.
        bibstyle : str | None, default None
        """

        self.open_doc()
        self.cites = self.find_all('\\\\cite\\{*\\}')
        self.thebibliographies = self.find_all('\\\\thebibliography')

        # Build latex document
        context = '\n'.join([cite for cite, _, _ in self.cites])
        self.__ltx.write(context, bibfile=bibfile, bibstyle=bibstyle)
        self.__ltx.compile()

        # Replace \thebibliography
        for _, start, end in self.thebibliographies[::-1]:
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

        Parameters
        ----------
        key : str
            A text to search in word document.

        Returns
        -------
        list
            A list of list whose values are found text, start place, and end place.
        """

        self.__fi = self.__sl.Find
        self.__fi.ClearFormatting()
        self.__fi.Highlight = 1
        self.__fi.MatchFuzzy = False
        found = []
        while True:
            self.__fi.Execute(
                key, False, False, True, False, False, True, 1, False, '', False
            )
            line = [str(self.__sl.Range), self.__sl.Range.Start, self.__sl.Range.End]
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
                if str(os.path.join(d.Path, d.Name)) == str(self.__target_file):
                    d.Close(SaveChanges=-1)  # wdSaveChanges
                    break
            shutil.copy2(self.__origin_file, self.__target_file)

        self.__dc = self.__ap.Documents.Open(self.__target_file)
        self.__sl = self.__ap.Selection

    def replace_all(self, key, val):
        """Replace all key with value.

        Parameters
        ----------
        key : str
            Original text.
        val : str
            Replacing text.
        """

        self.__fi = self.__sl.Find
        self.__fi.ClearFormatting()
        self.__fi.Highlight = 1
        self.__fi.MatchFuzzy = False
        self.__fi.Execute(
            key, False, False, True, False, False, True, 1, False, val, 2
        )
