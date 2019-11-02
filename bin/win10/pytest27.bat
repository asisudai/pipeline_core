:: Python pytest 2.7
:: Includes pipeline's environments and libraries.

@ECHO OFF
setlocal enabledelayedexpansion

:: Pipeline Repository:
SET PIPE_REPO=G:/projects/git/pipeline_core
SET PYTHONPATH=%PIPE_REPO%/core;%PIPE_REPO%/python27/win10;%PYTHONPATH%
::SET PYTHONPATH=%PYTHONPATH%;%PIPE_REPO%/python27/win10/_PySide2

:: Python Environments
SET PYTHONDONTWRITEBYTECODE=1

:: Development flag
set args=
for %%x in (%*) do (
  IF [%%x] == [--dev] (
      IF "%PIPE_DEV_REPO%"=="" (
        echo Environment var PIPE_DEV_REPO need to be set first.
      	EXIT /B
      )
      SET SCL_ISDEV=True
      SET PYTHONPATH=%PIPE_DEV_REPO%/python27/win10/_PySide2;%PIPE_DEV_REPO%/core;%PIPE_DEV_REPO%/python27/win10;%PYTHONPATH%
      echo Running using --dev environment: %PIPE_DEV_REPO%
     )
  IF NOT [%%x] == [--dev] (
     set "args=!args! %%x"
     )
)

:: Run
echo run: c:\Python27\python -m pytest %args%
c:\Python27\python -m pytest %args%
