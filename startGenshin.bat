@echo off
cd "C:\Users\Pierre\Documents\Genshin Mods\3dmigoto\"
powershell -Command "Start-Process 'C:\Users\Pierre\Documents\Genshin Mods\3dmigoto\3DMigoto Loader.exe' -Verb RunAs"
timeout /t 2 /nobreak >nul
cd "C:\Users\Pierre\Documents\Genshin Mods\"
powershell -Command "Start-Process 'C:\Users\Pierre\Documents\Genshin Mods\unlockfps_nc_signed.exe' -Verb RunAs"