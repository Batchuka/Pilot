@echo off
set commit_msg_file=%1
set commit_msg=%cat %commit_msg_file%

findstr /c:"If applied, my commit will:" %commit_msg_file% > nul
if errorlevel 1 (
    echo Error: A mensagem de commit deve incluir a seção 'If applied, my commit will:'
    exit /b 1
)

findstr /c:"What I did was:" %commit_msg_file% > nul
if errorlevel 1 (
    echo Error: A mensagem de commit deve incluir a seção 'What I did was:'
    exit /b 1
)

findstr /c:"Severidade:" %commit_msg_file% > nul
if errorlevel 1 (
    echo Error: A mensagem de commit deve incluir a seção 'Severidade:'
    exit /b 1
)
