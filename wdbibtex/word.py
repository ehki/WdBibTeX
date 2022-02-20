import os
import shutil
import win32com.client as client


class WordBibTeX:
    def __init__(
            self, target_file, copy_suffix='_bib', language='en',
            blibfiles=None, temporary_dir=None):
        self.target_file = os.path.abspath(target_file)
        dn, fn = os.path.split(self.target_file)
        bn, ex = os.path.splitext(fn)
        self.operating_file = os.path.join(dn, bn+copy_suffix+ex)
        if temporary_dir is None:
            temporary_dir = '.tmp'
        self.temporary_dir = os.path.join(dn, temporary_dir)
 
    def close_docx_file(self, fn, save=True):
        for d in self.ap.Documents:
            if str(os.path.join(d.Path, d.Name)) == str(fn):
                d.Close(SaveChanges=-1)  # wdSaveChanges
                break

    def compile(self):
        os.mkdir(os.path.basename(self.operating_file))
        self.open_doc()
        self.cites = self.find_latex_key('\\\\cite\\{*\\}')
        self.thebibliographies = self.find_latex_key('\\\\thebibliography')

    def find_latex_key(self, key):
        self.fi = self.sl.Find
        self.fi.ClearFormatting()
        self.fi.Highlight = 1
        self.fi.MatchFuzzy = False
        found = []
        while True:
            self.fi.Execute(
                key, False, False, True, False, False, True, 1, False, '', False
            )
            line = [str(self.sl.Range), self.sl.Range.Start, self.sl.Range.End]
            if line in found:
                break
            found.append(line)
        return sorted(found, key=lambda x: x[1])

    def open_doc(self):
        self.ap = client.Dispatch('Word.Application')
        self.ap.Visible = True

        # Copy original file to operatinf file for safety.
        try:
            shutil.copy2(self.target_file, self.operating_file)
        except PermissionError:
            self.close_docx_file(self.operating_file, save=True)
            shutil.copy2(self.target_file, self.operating_file)

        self.dc = self.ap.Documents.Open(self.operating_file)
        self.sl = self.ap.Selection
