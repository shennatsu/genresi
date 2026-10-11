Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:EnvPath = Join-Path $script:ProjectRoot '.env'

function Import-GenresiEnv {
    if (-not (Test-Path -LiteralPath $script:EnvPath -PathType Leaf)) {
        throw "File .env belum ada. Salin .env.example menjadi .env dan isi kredensial lokal terlebih dahulu."
    }

    foreach ($line in Get-Content -LiteralPath $script:EnvPath) {
        $trimmed = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith('#')) {
            continue
        }

        $separator = $trimmed.IndexOf('=')
        if ($separator -lt 1) {
            throw "Baris .env tidak valid: $trimmed"
        }

        $name = $trimmed.Substring(0, $separator).Trim()
        $value = $trimmed.Substring($separator + 1).Trim()
        if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        Set-Item -Path ("Env:{0}" -f $name) -Value $value
    }

    foreach ($required in @('ODOO_ADMIN_PASSWD', 'PGHOST', 'PGPORT', 'PGUSER')) {
        if ([string]::IsNullOrWhiteSpace((Get-Item -Path ("Env:{0}" -f $required)).Value)) {
            throw "Variabel $required wajib diisi di .env."
        }
    }

    $odooRootItem = Get-Item -Path 'Env:ODOO_ROOT' -ErrorAction SilentlyContinue
    $odooRootValue = if ($null -eq $odooRootItem) { $null } else { $odooRootItem.Value }
    $odooRoot = if ([string]::IsNullOrWhiteSpace($odooRootValue)) { 'D:\odoo\Odoo17' } else { $odooRootValue }
    $script:OdooPython = Join-Path $odooRoot 'python\python.exe'
    $script:OdooBin = Join-Path $odooRoot 'server\odoo-bin'
    if (-not (Test-Path -LiteralPath $script:OdooPython -PathType Leaf)) {
        throw "Python Odoo tidak ditemukan: $script:OdooPython"
    }
    if (-not (Test-Path -LiteralPath $script:OdooBin -PathType Leaf)) {
        throw "Source Odoo tidak ditemukan: $script:OdooBin"
    }

    $env:PGHOST = $env:PGHOST
    $env:PGPORT = $env:PGPORT
    $env:PGUSER = $env:PGUSER
    $pgPasswordItem = Get-Item -Path 'Env:PGPASSWORD' -ErrorAction SilentlyContinue
    $pgPasswordValue = if ($null -eq $pgPasswordItem) { $null } else { $pgPasswordItem.Value }
    $env:PGPASSWORD = if ($null -eq $pgPasswordValue) { '' } else { $pgPasswordValue }
}

function New-GenresiOdooConfig {
    $templatePath = Join-Path $script:ProjectRoot 'odoo.conf.template'
    $configPath = Join-Path $script:ProjectRoot 'odoo.conf'
    if (-not (Test-Path -LiteralPath $templatePath -PathType Leaf)) {
        throw "Template konfigurasi tidak ditemukan: $templatePath"
    }

    $config = Get-Content -Raw -LiteralPath $templatePath
    $replacements = @{
        '__ODOO_ADMIN_PASSWD__' = $env:ODOO_ADMIN_PASSWD
        '__PGHOST__'            = $env:PGHOST
        '__PGPORT__'            = $env:PGPORT
        '__PGUSER__'            = $env:PGUSER
        '__PGPASSWORD__'        = $env:PGPASSWORD
    }
    foreach ($token in $replacements.Keys) {
        $config = $config.Replace($token, [string]$replacements[$token])
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($configPath, $config, $utf8NoBom)
    return $configPath
}

function Invoke-GenresiOdoo {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [string[]]$Arguments
    )

    $configPath = New-GenresiOdooConfig
    Push-Location $script:ProjectRoot
    try {
        & $script:OdooPython $script:OdooBin '-c' $configPath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Odoo berhenti dengan exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

function Invoke-GenresiOdooShell {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Database,
        [Parameter(Mandatory = $true)]
        [string]$Code
    )

    $configPath = New-GenresiOdooConfig
    Push-Location $script:ProjectRoot
    try {
        $Code | & $script:OdooPython $script:OdooBin 'shell' '-c' $configPath '-d' $Database '--no-http'
        if ($LASTEXITCODE -ne 0) {
            throw "Odoo shell berhenti dengan exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

function Sync-GenresiAdminPassword {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Database
    )

    $code = @'
import os

env.ref("base.user_admin").sudo().write({"password": os.environ["ODOO_ADMIN_PASSWD"]})
env.cr.commit()
print("Genresi admin password synchronized.")
'@
    Invoke-GenresiOdooShell -Database $Database -Code $code
}

function Set-GenresiThemeColors {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Database
    )

    $code = @'
settings = env["res.config.settings"].create({
    "color_brand_light": "#A85A14",
    "color_primary_light": "#A85A14",
    "color_brand_dark": "#A85A14",
    "color_primary_dark": "#A85A14",
    "theme_color_appsmenu_text": "#212529",
    "theme_color_appbar_text": "#212529",
    "theme_color_appbar_active": "#FBEEDD",
    "theme_color_appbar_background": "#FFFFFF",
    "theme_background_image": False,
})
settings.set_values()
env.company.background_image = False
env.cr.commit()
print("Genresi MuK theme colors synchronized.")
'@
    Invoke-GenresiOdooShell -Database $Database -Code $code
}

function Invoke-GenresiPostgres {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [string]$Database = 'postgres'
    )

    & psql '-X' '-w' '-h' $env:PGHOST '-p' $env:PGPORT '-U' $env:PGUSER '-d' $Database '-v' 'ON_ERROR_STOP=1' '-At' '-c' $Command
    if ($LASTEXITCODE -ne 0) {
        throw "psql berhenti dengan exit code $LASTEXITCODE."
    }
}

function Test-GenresiDatabase {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Database
    )

    $result = Invoke-GenresiPostgres -Command "SELECT 1 FROM pg_database WHERE datname = '$Database';"
    return ($result -contains '1')
}

function Confirm-GenresiDatabaseDrop {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Database
    )

    if (-not $Database.StartsWith('genresi_')) {
        throw "Penolakan aman: hanya database dengan prefix genresi_ yang boleh di-drop."
    }

    $confirmation = Read-Host "Ketik $Database untuk menghapus database ini"
    if ($confirmation -cne $Database) {
        throw "Konfirmasi drop tidak cocok; tidak ada database yang dihapus."
    }

    & dropdb '-w' '-h' $env:PGHOST '-p' $env:PGPORT '-U' $env:PGUSER '--if-exists' $Database
    if ($LASTEXITCODE -ne 0) {
        throw "dropdb berhenti dengan exit code $LASTEXITCODE."
    }
}
