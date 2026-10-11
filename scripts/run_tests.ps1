param(
    [switch]$KeepDatabase
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

Import-GenresiEnv
$database = 'genresi_test'
if (-not $KeepDatabase -and (Test-GenresiDatabase -Database $database)) {
    Confirm-GenresiDatabaseDrop -Database $database
}

if (-not (Test-GenresiDatabase -Database $database)) {
    & createdb '-w' '-h' $env:PGHOST '-p' $env:PGPORT '-U' $env:PGUSER $database
    if ($LASTEXITCODE -ne 0) {
        throw "createdb berhenti dengan exit code $LASTEXITCODE."
    }
}

$modules = 'genresi_base,genresi_stock,genresi_cash,genresi_report'
Invoke-GenresiOdoo -Arguments @('-d', $database, '-i', $modules, '-u', $modules, '--without-demo=all', '--skip-auto-install', '--no-http', '--test-enable', '--test-tags', '/genresi_base', '--stop-after-init')
