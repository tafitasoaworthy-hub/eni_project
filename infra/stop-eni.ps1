# PowerShell wrapper for the ENI stop script.
$bash = 'C:\Program Files\Git\bin\bash.exe'
if (-not (Test-Path $bash)) { throw "Git Bash not found at $bash" }
& $bash "$PSScriptRoot/stop-eni.sh" @args
exit $LASTEXITCODE
