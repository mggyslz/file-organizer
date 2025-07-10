@echo off
rmdir /s /q build
rmdir /s /q dist
del /q *.spec
pyinstaller --onefile --windowed ^
--name FileOrganizerApp ^
--icon=assets/app_logo.ico ^
--add-data "assets;assets" ^
--add-data "file_organizer_config.json;." ^
core/main.py
pause



