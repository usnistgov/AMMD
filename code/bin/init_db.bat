@setlocal enableextensions
@cd /d "%~dp0"
@echo off

if exist "..\data\db" if exist "..\db.sqlite3" (
	echo ERROR: Databases already present
	pause
	exit
)

echo Initialize databases
if exist "..\data\db" (
	echo MongoDB database is already present
	start cmd /k ..\mongodb\bin\mongod.exe --config ..\conf\mongodb.conf
	echo Waiting for MongoDB to start...
	timeout /t 10
) else (
	echo Creating MongoDB database...
	mkdir ..\data\db
	start cmd /k ..\mongodb\bin\mongod.exe --config ..\conf\mongodb.conf
	echo Waiting for MongoDB to start...
	timeout /t 10
	echo Creating MongoDB models...
	..\mongodb\bin\mongo.exe < create_admin.js
	..\mongodb\bin\mongo.exe --port 27017 -u "admin" -p "admin" --authenticationDatabase admin < create_user.js
)

if exist "..\db.sqlite3" (
	echo SQLite3 database is already present
) else (
	echo Creating SQLite3 models...
	set PYTHONHOME=
	..\WinPython-32bit-2.7.6.3\python-2.7.6\python.exe ..\manage.py migrate
	echo CREATE AN ADMIN USER TO ACCESS THE MDCS:
	..\WinPython-32bit-2.7.6.3\python-2.7.6\python.exe ..\manage.py createsuperuser
)

echo SUCCESS: Databases are initialized.
pause