@ECHO OFF

REM KOS v1 - Simple Docker Image Puller (from images.env)
SET "IMAGES_FILE=%~dp0..\..\env\images.env"
SET "LOG_DIR=%~dp0..\..\logs\docker"
IF NOT EXIST "%LOG_DIR%" MKDIR "%LOG_DIR%"

REM Get ISO timestamp for log file prefix
FOR /F %%a IN ('wmic os get localdatetime ^| findstr /r "^[0-9]"') DO SET ISODT=%%a
SET "ISODT=%ISODT:~0,4%-%ISODT:~4,2%-%ISODT:~6,2%T%ISODT:~8,2%-%ISODT:~10,2%-%ISODT:~12,2%"
SET "LOG_FILE=%LOG_DIR%\%ISODT%_pull_images.log"

REM Use system logger if available, else fallback to echo
SET "LOGGER=%~dp0..\..\scripts\logger\logger.bat"
IF EXIST "%LOGGER%" (
    SET "USE_LOGGER=1"
) ELSE (
    SET "USE_LOGGER=0"
)

IF NOT EXIST "%IMAGES_FILE%" (
    ECHO [ERROR] images.env file not found at: %IMAGES_FILE%
    EXIT /B 1
)

ECHO [INFO] Pull order: > "%LOG_FILE%"
FOR /F "usebackq tokens=* delims=" %%I IN ("%IMAGES_FILE%") DO (
    IF NOT "%%I"=="" (
        ECHO   %%I >> "%LOG_FILE%"
    )
)
ECHO ------------------------------------------- >> "%LOG_FILE%"

FOR /F "usebackq tokens=* delims=" %%I IN ("%IMAGES_FILE%") DO (
    IF NOT "%%I"=="" (
        FOR /F %%T IN ('wmic os get localdatetime ^| findstr /r "^[0-9]"') DO SET ISODT=%%T
        SET "ISODT=!ISODT:~0,4!-!ISODT:~4,2!-!ISODT:~6,2!T!ISODT:~8,2!-!ISODT:~10,2!-!ISODT:~12,2!"
        IF "%USE_LOGGER%"=="1" (
            CALL "%LOGGER%" "[INFO] !ISODT! Pulling: %%I" >> "%LOG_FILE%"
        ) ELSE (
            ECHO [INFO] !ISODT! Pulling: %%I >> "%LOG_FILE%"
        )
        docker pull %%I >> "%LOG_FILE%" 2>&1
    )
)

ECHO [SUCCESS] All images processed. >> "%LOG_FILE%"
EXIT /B 0