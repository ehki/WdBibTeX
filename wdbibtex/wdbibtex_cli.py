import sys
import argparse

import wdbibtex

def main():
    parser = argparse.ArgumentParser(
        description='WdBibTeX is a BibTeX citation formatter for MS word.'
    )
    parser.add_argument(
        'file',
        type=str,
        help=(
            'File to BibTeX format.'
        )
    )
    parser.add_argument(
        '--bibliographystyle',
        type=str,
        default=None,
        help=(
            'Select BibTeX style file. '
            'Default: .bst in directory where target file belogns to.'
        )
    )
    parser.add_argument(
        '--bibliographyfiles',
        type=str,
        default=None,
        help=(
            'Select bibliography file. '
            'Default: all .bib in directory where target file belogns to.'
        )
    )
    parser.add_argument(
        '--keeptmpdir',
        action='store_true',
        help=(
            'Keep temporary files after run. '
            'Default: False(= clean temporary directory)'
        )
    )
    args = parser.parse_args()
    wb = wdbibtex.WdBibTeX(args.file)
    wb.compile()
    wb.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
