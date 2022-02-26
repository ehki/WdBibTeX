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
        '--bibstyle',
        type=str,
        default=None,
        help=(
            'BibTeX style file. '
            'Default: .bst in target file directory'
        )
    )
    parser.add_argument(
        '--bibfile',
        type=str,
        default=None,
        help=(
            'Bibliography file. '
            'Default: all .bib in target file directory'
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
    wb.compile(bibfile=args.bibfile, bibstyle=args.bibstyle)
    wb.close(cleanup=not args.keeptmpdir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
