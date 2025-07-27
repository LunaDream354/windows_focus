set "SOFTWARE=window focus"
set "SOURCE=dist"
set "SIGN_TOOL=C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
rmdir /s /q "%CD%\%SOURCE%"
rmdir /s /q "%CD%\build"

del /f /q "%CD%\%SOFTWARE%.exe"

pyinstaller --onefile --name "%SOFTWARE%" main.py

move "%CD%\%SOURCE%\%SOFTWARE%.exe" "%CD%"

rmdir /s /q "%CD%\%SOURCE%"
rmdir /s /q "%CD%\build"
del /f /q "%CD%\%SOFTWARE%.spec"
