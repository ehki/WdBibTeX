# WdBibTeX
WdBibTeX is a MS Word's BibTeX toolkit.

## Installation

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/wdbibtex).

```sh
pip install wdbibtex
```

## Dependencies

- Windows OS, for pywin32
- pywin32, for operating MS Word
- TeX Live 2021, for building LaTeX file.

## Usage

Let target Word file name is `file.docx`.

0. Confirm you can build LaTeX project with basic `latex->bibtex->latex->latex` scheme. (This is out of scope of this project.)
1. Copy your `.bib` to same directory with `file.docx`.
2. Copy your `.bst` to same directory with `file.docx`.
3. Write your docx file with LaTeX citations keys of `\cite{key}` and `\thebibliography` label.
3. On the shell, change directory to the `file.docx`'s directory.
4. Execute:
```sh
$ python -m wdbibtex file.docx
```
5. If works correctly, you can see `file_bib.docx`. LaTeX citation keys of `\cite{key}` and `\thebibliography` will be converted to [1] and [1] A. Name, "Title", Journal, vol... (for example).

## Documentation
The official documentation is hosted on GitHub Pages: https://ehki.github.io/WdBibTeX

## License
WdBibTeX is distributed undert [MIT License](https://github.com/ehki/WdBibTeX/blob/bdf05337ae3f0659b2cca09986facd9aa7ad8a06/LICENSE).
