@echo off
if "%2" == "" (
    echo If applied, my commit will: >> %1
    echo What I did was: >> %1
    echo Severidade (bugfix, feature, major): >> %1
)
