:<<"::CMDLITERAL"
@echo off
goto :CMDSCRIPT
::CMDLITERAL
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

script_dir=$(cd $(dirname $0); pwd -P)

$script_dir/bootstrap $script_dir/project.py $*

exit $?

:CMDSCRIPT
@echo off
call "%~dp0bootstrap.cmd" "%~dp0project.py" %*
if errorlevel 1 (
    echo script failed
    exit /b 1
)
