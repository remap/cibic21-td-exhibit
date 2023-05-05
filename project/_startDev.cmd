@echo off
rem turn off echo

rem set TouchDesigner build numbers
set TOUCHVERSION=2022.32120

rem set our project file target
set TOEFILE="project.toe"

rem set the rest of our paths for executables
set TOUCHDIR=%PROGRAMFILES%\Derivative\TouchDesigner.
set TOUCHEXE=\bin\TouchDesigner.exe

rem set dev flag to true
set DEV=TRUE
set PUBLIC=%~dp0_public
set CLOUDRENDERING=False
set OUTPUTDIRECTORY=_outputs/renderings
set CACHEDIRECTORY=_exports/pickle_jar

rem query registry for installed version of touchdesigner
for /f "tokens=2*" %%a in ('reg query "hkcr\TouchDesigner."%TOUCHVERSION%"\shell\open\command" 2^> nul') do (
	set "TOUCHSTARTCOMMAND=%%b"
	goto STARTPROJECT
)
rem if we are in this part of the script, the TD version has not been found in the registry
goto TDVERSIONNOTFOUND

:STARTPROJECT

rem construct our run command - removes cmd arg param, concats toefile
set RUNCOMMAND=%TOUCHSTARTCOMMAND:"%1"=%%TOEFILE%

if %CLOUDRENDERING%==True (
	rem we are rendering in the cloud. Waiting on process finishes...

	echo Running pre-render scripts...
	start /W /B CMD /c %~dp0cloud-scripts/pre-render.cmd


	echo Running render process...

	rem start our project file with the target TD installation
	start /W "" %RUNCOMMAND%

	echo Render process ended.
	echo Running post-render scripts...
	start /W /B CMD /c %~dp0cloud-scripts/post-render.cmd

) else (
	echo Running live mode...
	rem we are rendering live. Run the project normally...

	rem start our project file with the target TD installation
	start "" %RUNCOMMAND%
)

goto END

:TDVERSIONNOTFOUND
echo TouchDesigner.%TOUCHVERSION% not found. 
echo Install it here: https://download.derivative.ca/TouchDesigner.%TOUCHVERSION%.exe
pause
goto END

:END
echo done.

