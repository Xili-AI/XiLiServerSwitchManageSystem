#Requires -Version 5.1
<#
.SYNOPSIS
    Starts the wstunnel client for the XiLi service gateway.

.DESCRIPTION
    Opens a loopback SOCKS5 proxy plus one loopback origin per registered
    service, all carried by the single existing HTTPS entry. No extra public
    port and no extra DNS record is used.

    The script is plain ASCII on purpose: Windows PowerShell 5.1 reads files
    without a BOM using the system code page, so non-ASCII text breaks parsing.

.PARAMETER Server
    Public tunnel URL (wss://...). Keep the default unless the entry changes.

.PARAMETER Secret
    TUNNEL_SECRET (32 lowercase hex chars). Defaults to $env:WSTUNNEL_SECRET.

.PARAMETER SocksPort
    Loopback port for the SOCKS5 proxy.

.PARAMETER Forward
    "localPort:host:port" pairs. Use "host" for the Docker host itself.
    Example: -Forward 2222:192.168.1.10:22 -Forward 13389:host:3389

.PARAMETER Panel
    Console base URL used to read the loopback endpoint map. Defaults to the
    -Server URL with ws/wss turned into http/https.

.PARAMETER NoAutoForwards
    Do not create a loopback origin for every registered service.

.PARAMETER Insecure
    Skip TLS certificate verification. Required when the entry uses a
    self-signed certificate or an incomplete chain (curl exit code 60).

.EXAMPLE
    .\scripts\tunnel-client.ps1 -Secret 0123456789abcdef0123456789abcdef

.EXAMPLE
    .\scripts\tunnel-client.ps1 -Secret 0123456789abcdef0123456789abcdef -Insecure

.EXAMPLE
    .\scripts\tunnel-client.ps1 -Forward 2222:192.168.1.10:22 -Forward 13389:host:3389
#>
[CmdletBinding()]
param(
    [string]$Server = "wss://frp-fog.com:27294",
    [string]$Secret = $env:WSTUNNEL_SECRET,
    [int]$SocksPort = 1080,
    [string[]]$Forward = @(),
    [string]$Panel = "",
    [switch]$NoAutoForwards,
    [switch]$Insecure,
    [string]$Version = "11.1.0",
    [string]$CacheDir
)

$ErrorActionPreference = "Stop"

if (-not $Secret) {
    throw "Missing secret. Pass -Secret or set WSTUNNEL_SECRET (see TUNNEL_SECRET in .env)."
}
if ($Secret -notmatch '^[0-9a-f]{32}$') {
    throw "Secret must be exactly 32 lowercase hex characters (TUNNEL_SECRET in .env)."
}
if ($Insecure) {
    Write-Warning "[tunnel] -Insecure: TLS certificate verification is disabled."
}

if (-not $CacheDir) {
    $baseDir = if ($env:LOCALAPPDATA) {
        Join-Path $env:LOCALAPPDATA "XiLiServerSwitchManageSystem"
    }
    else {
        Split-Path -Parent $PSScriptRoot
    }
    $CacheDir = Join-Path $baseDir "tunnel-client"
}

$arch = "amd64"
switch ($env:PROCESSOR_ARCHITECTURE) {
    "ARM64" { $arch = "arm64" }
    "x86" { $arch = "386" }
}

$exeDir = Join-Path $CacheDir "v$Version"
$exe = Join-Path $exeDir "wstunnel.exe"
$hasCurl = $null -ne (Get-Command curl.exe -ErrorAction SilentlyContinue)

if (-not (Test-Path -LiteralPath $exe)) {
    New-Item -ItemType Directory -Force -Path $exeDir | Out-Null
    $archive = Join-Path $exeDir "wstunnel.tar.gz"
    $url = "https://github.com/erebe/wstunnel/releases/download/v$Version/wstunnel_${Version}_windows_${arch}.tar.gz"
    Write-Host "[tunnel] downloading $url"

    if ($hasCurl) {
        & curl.exe -sSL --max-time 300 -o $archive $url
        if ($LASTEXITCODE -ne 0) {
            throw "Download failed (exit $LASTEXITCODE). Set HTTPS_PROXY if GitHub is blocked."
        }
    }
    else {
        $request = @{ Uri = $url; OutFile = $archive; UseBasicParsing = $true }
        $proxy = $env:HTTPS_PROXY
        if (-not $proxy) { $proxy = $env:HTTP_PROXY }
        if ($proxy) { $request.Proxy = $proxy }
        Invoke-WebRequest @request
    }

    & tar -xzf $archive -C $exeDir
    if ($LASTEXITCODE -ne 0) { throw "Could not extract $archive." }
    Remove-Item -LiteralPath $archive -Force
}

if (-not (Test-Path -LiteralPath $exe)) {
    throw "wstunnel.exe not found at $exe after download."
}

$clientArgs = @("client", "-P", $Secret, "-L", "socks5://127.0.0.1:$SocksPort")

$manualForwards = @()
foreach ($item in $Forward) {
    if ($item -notmatch '^(\d{1,5}):([^\s:]+):(\d{1,5})$') {
        throw "Invalid -Forward '$item'. Expected localPort:host:port, e.g. 2222:192.168.1.10:22"
    }
    $localPort = $Matches[1]
    $targetHost = $Matches[2]
    $targetPort = $Matches[3]

    # "host" reaches the machine running Docker, including 127.0.0.1-only services.
    if ($targetHost -eq "host") { $targetHost = "host.docker.internal" }

    $clientArgs += @("-L", "tcp://127.0.0.1:${localPort}:${targetHost}:${targetPort}")
    $manualForwards += [pscustomobject]@{
        LocalPort  = $localPort
        TargetHost = $targetHost
        TargetPort = $targetPort
    }
}

# One loopback origin per registered service: the app serves at "/" instead of
# "/p/<slug>/", so SPAs with hardcoded root paths work unchanged.
$localOrigins = @()
if (-not $NoAutoForwards) {
    if (-not $Panel) {
        $Panel = $Server -replace '^wss://', 'https://'
        $Panel = $Panel -replace '^ws://', 'http://'
    }
    $Panel = $Panel.TrimEnd('/')

    if (-not $hasCurl) {
        Write-Warning "[tunnel] curl.exe not found; skipping automatic loopback origins."
    }
    else {
        $curlArgs = @("-sS", "--max-time", "20")
        if ($Insecure) { $curlArgs += "-k" }
        $curlArgs += @("-H", "X-Tunnel-Secret: $Secret", "$Panel/api/tunnel/endpoints")

        $raw = & curl.exe @curlArgs
        $curlExit = $LASTEXITCODE

        if ($curlExit -in @(58, 60, 77)) {
            throw "The entry certificate is not trusted (curl exit $curlExit). Add -Insecure, or fix the entry certificate."
        }
        if ($curlExit -ne 0) {
            Write-Warning "[tunnel] endpoint map unavailable (curl exit $curlExit); SOCKS only."
        }
        else {
            try {
                $payload = $raw | ConvertFrom-Json
                $usedPorts = @{}
                foreach ($item in $manualForwards) { $usedPorts["$($item.LocalPort)"] = $true }

                foreach ($endpoint in $payload.data.endpoints) {
                    $originPort = [int]$endpoint.local_port
                    if ($usedPorts.ContainsKey("$originPort")) { continue }

                    $target = [uri]$endpoint.target_url
                    $targetPort = 80
                    if ($target.Scheme -eq "https") { $targetPort = 443 }
                    if ($target.Port -gt 0) { $targetPort = $target.Port }

                    $clientArgs += @("-L", "tcp://127.0.0.1:${originPort}:$($target.Host):${targetPort}")
                    $localOrigins += [pscustomobject]@{
                        LocalPort = $originPort
                        Slug      = $endpoint.slug
                        Target    = "$($target.Host):${targetPort}"
                    }
                }
            }
            catch {
                Write-Warning "[tunnel] endpoint map parse failed: $($_.Exception.Message)"
            }
        }
    }
}

if (-not $Insecure) {
    $clientArgs += "--tls-verify-certificate"
}
$clientArgs += $Server

Write-Host "[tunnel] server    $Server"
Write-Host "[tunnel] SOCKS5    127.0.0.1:$SocksPort"
foreach ($item in $manualForwards) {
    Write-Host "[tunnel] forward   127.0.0.1:$($item.LocalPort) -> $($item.TargetHost):$($item.TargetPort)"
}
foreach ($item in $localOrigins) {
    Write-Host "[tunnel] local     http://127.0.0.1:$($item.LocalPort)/  -> $($item.Slug) ($($item.Target))"
}
Write-Host "[tunnel] stop with Ctrl+C"

& $exe @clientArgs
