@REM Increment versions in
@REM wdbibtex/__init__.py
@REM docsrc/conf.py
cd ../
call %USERPROFILE%\Miniconda3\Scripts\activate.bat
call conda remove -n wdbibtex-v0.2.2 --all -y
call conda create -n wdbibtex-v0.2.2 python=3.9.6 -y
call conda activate wdbibtex-v0.2.2
call conda install pywin32 -y
rm -rf dist build wdbibtex.egg-info debug.log
python setup.py sdist
python setup.py bdist_wheel
pip install dist\wdbibtex-0.2.2-py3-none-any.whl
pip install pytest
python -m pytest
pause
pip install sphinx numpydoc pydata_sphinx_theme sphinx-argparse
rm -rf docs
sphinx-build docsrc docs
sphinx-build -M latexpdf docsrc docsrc/_build
mv docsrc/_build/latex/manual.pdf ./
@REM The following commands should be executed manually`
@REM twine upload --repository testpypi dist/*
@REM pause
@REM start "" https://test.pypi.org/project/wdbibtex
@REM pause
@REM pip uninstall wdbibtex -y
@REM pip --no-cache-dir install --index-url https://test.pypi.org/simple/ wdbibtex
@REM twine upload --repository pypi dist/*
@REM pause
@REM start "" https://pypi.org/project/wdbibtex
@REM pause
@REM pip uninstall wdbibtex -y
@REM pip --no-cache-dir install wdbibtex
pause