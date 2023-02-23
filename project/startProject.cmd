@echo off

rem set TouchDesigner build numbers
set TOUCHVERSION=2022.29850

rem set our project file target
set TOEFILE="project.toe"

rem set the rest of our paths for executables
set TOUCHDIR=%PROGRAMFILES%\Derivative\TouchDesigner.%TOUCHVERSION%
set TOUCHEXE=\bin\TouchDesigner.exe

rem combine our elements so we have a single path to our TouchDesigner.exe 
set TOUCHPATH="%TOUCHDIR%%TOUCHEXE%"


if exist %TOUCHPATH% goto :STARTPROJECT
echo There was a problem finding the required build of TouchDesigner.
echo Project Version Specified: %TOUCHVERSION%
echo ...
timeout /t 10 /nobreak
goto :END




:STARTPROJECT
rem killing explorer to get rid of touch gestures and swipe in from right.
taskkill /F /IM explorer.exe

timeout /t 3 /nobreak

rem start our project file with the target TD installation
call %TOUCHPATH% %TOEFILE%

:END
echo "done!"