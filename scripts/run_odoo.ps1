param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$OdooArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

Import-GenresiEnv
$arguments = @()
if ($null -ne $OdooArgs) {
    $arguments += $OdooArgs
}
Invoke-GenresiOdoo -Arguments $arguments
