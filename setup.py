from setuptools import setup, find_packages
from codecs import open

import wdbibtex

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wdbibtex',
    version=wdbibtex.__version__,
    url='http://pypi.python.org/pypi/pyjjy/',
    author='Haruki EJIRI',
    author_email='0y35.ejiri.vmqewyhw@gmail.com',
    description='WdBibTeX is a BibTeX toolkit for MS Word.',
    license='MIT',
    python_requires='>=3.6',
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft'
        'Topic :: Text Editors :: Documentation',
        'Topic :: Text Editors :: Word Processors',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],
)
