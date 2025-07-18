@echo off
setlocal

:: Set URLs for the installers (update if needed)
set GIT_URL=https://github.com/git-for-windows/git/releases/latest/download/Git-2.43.0-64-bit.exe
set PYTHON_URL=https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe

:: Set installer filenames
set GIT_INSTALLER=git-installer.exe
set PYTHON_INSTALLER=python-installer.exe

:: Download Git
echo Downloading Git...
curl -L %GIT_URL% -o %GIT_INSTALLER%

:: Install Git silently
echo Installing Git...
%GIT_INSTALLER% /VERYSILENT /NORESTART

:: Download Python
echo Downloading Python...
curl -L %PYTHON_URL% -o %PYTHON_INSTALLER%

:: Install Python silently with pip and add to PATH
echo Installing Python...
%PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

:: Refresh environment variables
echo Refreshing PATH...
setx PATH "%PATH%;C:\Program Files\Python312\Scripts;C:\Program Files\Python312"

:: Install PyInstaller via pip
echo Installing PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller

echo All done!
pause
