param(
    [switch]$Recreate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

Import-GenresiEnv
$database = 'genresi_dev'
if ($Recreate -and (Test-GenresiDatabase -Database $database)) {
    Confirm-GenresiDatabaseDrop -Database $database
}

if (-not (Test-GenresiDatabase -Database $database)) {
    & createdb '-w' '-h' $env:PGHOST '-p' $env:PGPORT '-U' $env:PGUSER $database
    if ($LASTEXITCODE -ne 0) {
        throw "createdb berhenti dengan exit code $LASTEXITCODE."
    }
}

$modules = 'muk_web_appsbar,muk_web_chatter,muk_web_colors,muk_web_dialog,muk_web_theme,genresi_base,genresi_stock,genresi_cash,genresi_report,genresi_demo'
Invoke-GenresiOdoo -Arguments @('-d', $database, '-i', $modules, '-u', $modules, '--without-demo=all', '--skip-auto-install', '--no-http', '--stop-after-init')
Set-GenresiThemeColors -Database $database
Invoke-GenresiOdoo -Arguments @('-d', $database, '-u', $modules, '--without-demo=all', '--skip-auto-install', '--no-http', '--stop-after-init')
Sync-GenresiAdminPassword -Database $database
