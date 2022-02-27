import argparse
import sys

import wdbibtex


def getparser():
    parser = argparse.ArgumentParser(
        description="WdBibTeX is a MS Word's BibTeX toolkit."
    )
    parser.add_argument(
        'file',
        type=str,
        help=(
            'File to BibTeX format.'
        )
    )
    parser.add_argument(
        '--bst',
        type=str,
        default=None,
        help=(
            'BibTeX style file. '
            'Default: .bst in target file directory'
        )
    )
    parser.add_argument(
        '--bib',
        type=str,
        default=None,
        help=(
            'Bibliography file. '
            'Default: all .bib in target file directory'
        )
    )
    parser.add_argument(
        '--keeptexdir',
        action='store_true',
        help=(
            'Keep LaTeX files and directory after run. '
            'Default: False(= clean LaTeX files/directory)'
        )
    )
    return parser


def main():
    parser = getparser()
    args = parser.parse_args()
    wb = wdbibtex.WdBibTeX(args.file)
    wb.build(bib=args.bib, bst=args.bst)
    wb.close(clear=not args.keeptmpdir)
    return 0


if __name__ == '__main__':
    sys.exit(wdbibtex.word.main())
