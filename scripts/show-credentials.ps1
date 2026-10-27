#Requires -Version 5.1
<#
.SYNOPSIS
    Prints where each password lives and the values that are safe to read from
    the compose / backend env files.

.DESCRIPTION
    The panel administrator password in dev.backend.env is only the initial
    seed. Once the database exists, the stored hash wins; use the panel or
    reset_admin_password.py to change it.

.PARAMETER Root
    Repository root. Defaults to the parent of this script's directory.

.PARAMETER EnvFile
    Backend env file name. Defaults to dev.backend.env.

.EXAMPLE
    .\scripts\show-credentials.ps1
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$EnvFile = "dev.backend.env"
)

$ErrorActionPreference = "Stop"

if (-not $Root) {
    $Root = Split-Path -Parent $PSScriptRoot
}

function Read-EnvFile([string]$path) {
    $map = @{}
    if (-not (Test-Path -LiteralPath $path)) {
        return $map
    }
    foreach ($line in Get-Content -LiteralPath $path) {
        if ($line -match '^\s*#') { continue }
        $index = $line.IndexOf('=')
        if ($index -lt 1) { continue }
        $key = $line.Substring(0, $index).Trim()
        $value = $line.Substring($index + 1).Trim()
        if ($key) { $map[$key] = $value }
    }
    return $map
}

$compose = Read-EnvFile (Join-Path $Root ".env")
$backend = Read-EnvFile (Join-Path $Root $EnvFile)

$adminUser = $backend["ADMIN_USERNAME"]
$adminPassword = $backend["ADMIN_PASSWORD"]
$tunnelSecret = $compose["TUNNEL_SECRET"]
$tunnelClient = 'powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\tunnel-client.ps1 -Secret ' + $tunnelSecret + ' -Insecure'

Write-Host "Password sources (authoritative)"
Write-Host "  panel admin seed : $EnvFile -> ADMIN_USERNAME / ADMIN_PASSWORD"
Write-Host "                     used only when the database is first created"
Write-Host "  tunnel secret    : .env -> TUNNEL_SECRET (restart tunnel + gateway)"
Write-Host "  portainer        : set on first visit, stored in the portainer_data volume"
Write-Host "  file browser     : first login admin/admin, stored in data/filebrowser"
Write-Host "  database         : no password (SQLite in the backend_data volume)"
Write-Host ""
Write-Host "Current values from config"
Write-Host "  admin user       : $adminUser"
Write-Host "  admin seed pass  : $adminPassword"
Write-Host "  tunnel secret    : $tunnelSecret"
Write-Host "  tunnel client    : $tunnelClient"
Write-Host ""
Write-Host "Reset the panel admin password:"
Write-Host '  docker compose exec backend python scripts/reset_admin_password.py "<new-password>"'
