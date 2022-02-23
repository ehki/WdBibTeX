import os
import shutil
import win32com.client as client

import wdbibtex


class WordBibTeX:
    def __init__(
            self,
            file,
            copy_suffix='_bib',
            workdir='.tmp',
    ):
        self.__origin_file = file
        self.__origin_file = os.path.abspath(self.__origin_file)
        dn, fn = os.path.split(self.__origin_file)
        bn, ex = os.path.splitext(fn)
        self.__target_file = os.path.join(dn, bn+copy_suffix+ex)
        self.__ltx = wdbibtex.LaTeXHandler(workdir=workdir)

    def close(self):

        # Save document
        self.__dc.Save()

        # Close document
        self.__dc.Close()

        #  Quit Word application if no other opened document
        if len(self.__ap.Documents) == 0:
            self.__ap.Quit()

    def compile(self):
        self.open_doc()
        self.cites = self.find_all('\\\\cite\\{*\\}')
        self.thebibliographies = self.find_all('\\\\thebibliography')

        # Build latex document
        context = '\n'.join([cite for cite, _, _ in self.cites])
        self.__ltx.write(context)
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
        self.__ap = client.Dispatch('Word.Application')
        self.__ap.Visible = True

        # Copy original file to operatinf file for safety.
        try:
            shutil.copy2(self.__origin_file, self.__target_file)
        except PermissionError:
            self.close_docx_file(self.__target_file, save=True)
            shutil.copy2(self.__origin_file, self.__target_file)

        self.__dc = self.__ap.Documents.Open(self.__target_file)
        self.__sl = self.__ap.Selection

    def replace_all(self, key, val):
        self.__fi = self.__sl.Find
        self.__fi.ClearFormatting()
        self.__fi.Highlight = 1
        self.__fi.MatchFuzzy = False
        self.__fi.Execute(
            key, False, False, True, False, False, True, 1, False, val, 2
        )
