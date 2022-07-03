@REM Increment versions in
@REM wdbibtex/__init__.py
@REM docsrc/conf.py
@REM
git checkout -b release/v0.2.4
cd ../
call %USERPROFILE%\Miniconda3\Scripts\activate.bat
call conda remove -n wdbibtex-v0.2.4 --all -y
call conda create -n wdbibtex-v0.2.4 python=3.9.6 -y
call conda activate wdbibtex-v0.2.4
call conda install pywin32 -y
rm -rf dist build wdbibtex.egg-info debug.log
python setup.py sdist
python setup.py bdist_wheel
pip install dist\wdbibtex-0.2.4-py3-none-any.whl
pip install pytest
python -m pytest
pause
pip install sphinx numpydoc pydata_sphinx_theme sphinx-argparse
rm -rf docs
sphinx-build docsrc docs
sphinx-build -M latexpdf docsrc docsrc/_build
mv docsrc/_build/latex/manual.pdf ./
pip install twine
pause
@REM The following commands should be executed manually`
twine upload --repository testpypi dist/*
pause
start "" https://test.pypi.org/project/wdbibtex
pause
pip uninstall wdbibtex -y
pip --no-cache-dir install --index-url https://test.pypi.org/simple/ wdbibtex
pause
twine upload --repository pypi dist/*
pause
start "" https://pypi.org/project/wdbibtex
pause
pip uninstall wdbibtex -y
pip --no-cache-dir install wdbibtex
pause
@REM Check current branch
git branch --contains
pause
git add docs docsrc manual.pdf wdbibtex
git commit -m "version 0.2.4"
pause