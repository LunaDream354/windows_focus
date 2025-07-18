set "SOFTWARE=window focus"
set "SOURCE=dist"


rmdir /s /q "%CD%\%SOURCE%"
rmdir /s /q "%CD%\build"

del /f /q "%CD%\%SOFTWARE%.exe"

pyinstaller --onefile --name "%SOFTWARE%" main.py

move "%CD%\%SOURCE%\%SOFTWARE%.exe" "%CD%"

rmdir /s /q "%CD%\%SOURCE%"
rmdir /s /q "%CD%\build"
del /f /q "%CD%\%SOFTWARE%.spec"
