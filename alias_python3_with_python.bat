@echo off
for /f "delims=" %%i in ('where python') do @copy "%%i" "%%~dpi\python3.exe" & goto end
:end
