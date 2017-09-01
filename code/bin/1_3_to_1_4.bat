@setlocal enableextensions
@cd /d "%~dp0"
@echo off

start cmd /k ..\mongodb\bin\mongod.exe --config ..\conf\mongodb.conf

echo Waiting for MongoDB to start...
timeout /t 10

set PYTHONHOME=
..\WinPython-32bit-2.7.6.3\python-2.7.6\python.exe ..\manage.py migrate
..\WinPython-32bit-2.7.6.3\python-2.7.6\python.exe ..\mgi\migrate.py -u admin -p admin -path "..\mongodb\bin"

pause