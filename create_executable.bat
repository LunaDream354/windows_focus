set "SOFTWARE=windows focus"
set "SOURCE_FOLDER=dist\%SOFTWARE%"

rmdir /s /q "%CD%\dist"
rmdir /s /q "%CD%\build"
rmdir /s /q "%CD%\%SOFTWARE%"
rmdir /s /q "%CD%\__pycache__"

pyinstaller --clean --name="%SOFTWARE%" main.py

move "%SOURCE_FOLDER%" "%CD%"
rmdir /s /q "%CD%\dist"
rmdir /s /q "%CD%\build"
rmdir /s /q "%CD%\__pycache__"
del /f /q "%CD%\%SOFTWARE%.spec"