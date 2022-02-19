import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='WdBibTeX is a BibTeX citation formatter for MS word.'
    )
    parser.add_argument(
        '--workingdirectory',
        metavar='Working Directory',
        type=str,
        help=(
            'Select working directory.'
            'Default: current working directory.'
        )
    )
    parser.add_argument(
        '--bibliographystyle',
        metavar='BST file',
        type=str,
        help=(
            'Select BibTeX style file.'
            'Default: IEEEtran.bst in current working directory.'
        )
    )
    parser.add_argument(
        '--bibliography',
        metavar='BIB file',
        type=str,
        help=(
            'Select bibliography file.'
            'Default: library.bib in current working directory.'
        )
    )
    parser.add_argument(
        '--keepaux',
        metavar='Keep AUX files',
        action='store_true',
        help=(
            'Keep AUX files after run.'
            'Default: False(= clean aux files)'
        )
    )
    args = parser.parse_args()
    return 0


if __name__ == '__main__':
    sys.exit(main())
