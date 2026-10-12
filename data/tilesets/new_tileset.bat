@echo off
setlocal

rem Create a new porytiles-managed tileset.
rem
rem Usage: data\tilesets\new_tileset.bat [Name] [primary/secondary] [partner-primary]
rem   Name               PascalCase, e.g. Omaiville or HaieFroide (symbol gTileset_Name)
rem   primary/secondary  default: secondary
rem   partner-primary    primary a secondary is paired with, default: gTileset_General
rem Any missing argument is asked for interactively.

cd /d "%~dp0..\.."

if not exist porytiles\tilesets\ (
    echo Could not find the repository root. Run this from the repository.
    exit /b 1
)

where porytiles >nul 2>&1
if errorlevel 1 (
    echo porytiles not found on PATH. Install porytiles 2.x first.
    exit /b 1
)

set "NAME=%~1"
set "TYPE=%~2"
set "PARTNER=%~3"

if "%NAME%"=="" set /p "NAME=Tileset name (PascalCase, e.g. Omaiville): "
echo %NAME%| findstr /r "^[A-Z][A-Za-z0-9]*$" >nul
if errorlevel 1 (
    echo Invalid name. Use PascalCase letters and digits, starting with a capital.
    exit /b 1
)

if "%TYPE%"=="" set /p "TYPE=Type [secondary/primary] (default: secondary): "
if "%TYPE%"=="" set "TYPE=secondary"
if /i "%TYPE%"=="primary" set "TYPE=primary"
if /i "%TYPE%"=="secondary" set "TYPE=secondary"
if not "%TYPE%"=="primary" if not "%TYPE%"=="secondary" (
    echo Type must be primary or secondary.
    exit /b 1
)

if /i "%TYPE%"=="secondary" if "%PARTNER%"=="" set /p "PARTNER=Partner primary tileset (default: gTileset_General): "
if /i "%TYPE%"=="secondary" if "%PARTNER%"=="" set "PARTNER=gTileset_General"

set "SYMBOL=gTileset_%NAME%"
for /f "delims=" %%F in ('powershell -NoProfile -Command "('%NAME%' -creplace '([a-z0-9])([A-Z])', '$1_$2').ToLower()"') do set "FOLDER=%%F"
set "DIR=data\tilesets\%TYPE%\%FOLDER%"

if /i "%TYPE%"=="primary" if not exist "data\tilesets\primary\general\porytiles_src\top.png" (
    echo Missing data\tilesets\primary\general\porytiles_src\, needed as the base for new primaries.
    exit /b 1
)

findstr /c:"const struct Tileset %SYMBOL% =" src\data\tilesets\headers.h >nul 2>&1
if not errorlevel 1 (
    echo %SYMBOL% already exists in src\data\tilesets\headers.h.
    exit /b 1
)
if exist "%DIR%" (
    echo %DIR% already exists.
    exit /b 1
)
if exist "porytiles\tilesets\%SYMBOL%" (
    echo porytiles\tilesets\%SYMBOL% already exists.
    exit /b 1
)

set "PAIRING="
set "SECONDARY_FLAG="
if /i "%TYPE%"=="secondary" (
    set "SECONDARY_FLAG=--secondary"
    set "PAIRING=--primary-pairing-mode manual --primary-pairing-partners %PARTNER%"
)

porytiles create-tileset --metatile-attribute-size 2 %SECONDARY_FLAG% %PAIRING% -- %SYMBOL%
if errorlevel 1 (
    echo porytiles failed to create %SYMBOL%.
    exit /b 1
)

if /i "%TYPE%"=="primary" (
    for %%L in (bottom.png middle.png top.png attributes.csv) do copy /y "data\tilesets\primary\general\porytiles_src\%%L" "%DIR%\porytiles_src\" >nul
)

mkdir "%DIR%\porytiles" 2>nul

set "COMPILE_ARGS=%SYMBOL%"
if /i "%TYPE%"=="secondary" if not "%PARTNER%"=="gTileset_General" set "COMPILE_ARGS=%PAIRING% -- %SYMBOL%"

> "%DIR%\porytiles\compile.bat" (
    echo @echo off
    echo if not "%%CD:porytiles=%%"=="%%CD%%" ^(
    echo     echo Please run this script from the root of the repository.
    echo     echo .\%DIR%\porytiles\compile.bat
    echo     exit /b 1
    echo ^)
    echo.
    echo porytiles compile-tileset --metatile-attribute-size 2 %COMPILE_ARGS%
)
> "%DIR%\porytiles\decompile.bat" (
    echo @echo off
    echo if not "%%CD:porytiles=%%"=="%%CD%%" ^(
    echo     echo Please run this script from the root of the repository.
    echo     echo .\%DIR%\porytiles\decompile.bat
    echo     exit /b 1
    echo ^)
    echo.
    echo porytiles decompile-tileset --metatile-attribute-size 2 %SYMBOL%
    echo echo Done! Source PNGs updated in %DIR%\porytiles_src\
)

set "ASEPRITE_MADE=0"
where python >nul 2>&1 && python -c "import PIL" >nul 2>&1 && python data\tilesets\make_aseprite.py "%DIR%\porytiles_src" "%DIR%\porytiles\tileset.aseprite" && set "ASEPRITE_MADE=1"

echo.
echo Created %SYMBOL% in %DIR%
echo.
if "%ASEPRITE_MADE%"=="1" (
    echo Created %DIR%\porytiles\tileset.aseprite with layers bottom, middle, top.
) else (
    echo Could not create tileset.aseprite ^(needs python with Pillow: pip install pillow^).
    echo Paint the PNGs in %DIR%\porytiles_src\ directly instead.
)

echo.
echo Next steps:
echo   1. Paint the tileset. Either open %DIR%\porytiles\tileset.aseprite in
echo      Aseprite and export each layer to %DIR%\porytiles_src\^<layer^>.png
echo      bottom.png, middle.png, top.png, keeping the canvas size, or edit those PNGs directly.
echo   2. Set metatile behaviors in %DIR%\porytiles_src\attributes.csv id,behavior
echo   3. Compile: %DIR%\porytiles\compile.bat
echo   4. Use %SYMBOL% as the secondary tileset of a layout in Porymap.
echo   5. Build with make.

endlocal
