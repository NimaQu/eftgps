@echo off
setlocal

set "filename=%~n0"
eftgps.exe %filename%
endlocal
