@REM Example of how to install a collection of python externals
@REM into a project directory 

@REM set python install destination 

set FILEDEST=%~dp0_public/python-libs

@REM pip install commands for the python version for TouchDesigner
@REM This assumes we've already installed the coresponding version of python
@REM on Windows

py -3.9 -m pip install -r requirements.txt -t %FILEDEST%