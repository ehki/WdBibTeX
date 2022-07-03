# WdBibTeX
WdBibTeX is a BibTeX toolkit for MS Word.

## Installation

Binary installers for the latest released version are available at the [Python Package Index (PyPI)](https://pypi.org/project/wdbibtex).

You can install wdbibtex package via pip command.

```sh
pip install -U wdbibtex
```

## Dependencies

- Windows OS, for pywin32
- pywin32>=302, for operating MS Word
- regex>=2022.6.2, for converting LaTeX string to text
- TeX Live 2022, for building LaTeX file

## Usage

Let target Word file name be `file.docx`.

0. Confirm you can build LaTeX project with basic `latex->bibtex->latex->latex` scheme. (This is out of scope of this project.)
1. Copy your `.bib` and `.bst` to same directory with `file.docx`.
2. Write your docx file with LaTeX citations keys of `\cite{key}` and `\thebibliography` label.
3. On the shell, change directory to the `file.docx`'s directory.
4. Execute:
```sh
$ python -m wdbibtex file.docx
```
5. If wdbibtex works correctly, you can see `file_bib.docx`. LaTeX citation keys of `\cite{key}` and `\thebibliography` will be converted to [1] and [1] A. Name, "Title", Journal, vol... (for example).

## Documentation
The official documentation is hosted on GitHub Pages: https://ehki.github.io/WdBibTeX

## License
WdBibTeX is distributed undert [MIT License](https://github.com/ehki/WdBibTeX/blob/bdf05337ae3f0659b2cca09986facd9aa7ad8a06/LICENSE).
