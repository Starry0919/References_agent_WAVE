[CmdletBinding()]
param(
    [string]$Origin = "http://127.0.0.1:8642"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$runtimeDir = Join-Path $projectRoot ".public-tunnel"
$bundledCloudflared = Join-Path $runtimeDir "cloudflared.exe"
$stdoutLog = Join-Path $runtimeDir "cloudflared.stdout.log"
$stderrLog = Join-Path $runtimeDir "cloudflared.stderr.log"
$urlFile = Join-Path $runtimeDir "public-url.txt"

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

Write-Host "Checking the local website at $Origin ..."
try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $Origin -TimeoutSec 8
    if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 500) {
        throw "HTTP status $($response.StatusCode)"
    }
}
catch {
    Write-Host ""
    Write-Host "The local website is not available." -ForegroundColor Red
    Write-Host "Start it first with 启动网站.cmd, then run this file again."
    Write-Host "Checked address: $Origin"
    exit 1
}

if (Test-Path -LiteralPath $bundledCloudflared) {
    $cloudflared = $bundledCloudflared
}
else {
    $installedCloudflared = Get-Command cloudflared.exe -ErrorAction SilentlyContinue
    if ($null -ne $installedCloudflared) {
        $cloudflared = $installedCloudflared.Source
    }
}

if (-not (Get-Variable cloudflared -ErrorAction SilentlyContinue)) {
    $downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    $temporaryFile = "$bundledCloudflared.download"
    Write-Host "Downloading Cloudflare Tunnel for the first run ..."
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($null -ne $curl) {
        # GitHub downloads can be slow on some networks. --continue-at makes
        # an interrupted first download resume instead of starting over.
        & $curl.Source --location --fail --retry 5 --retry-all-errors `
            --continue-at - --output $temporaryFile $downloadUrl
        if ($LASTEXITCODE -ne 0) {
            throw "cloudflared download failed with curl exit code $LASTEXITCODE"
        }
    }
    else {
        Invoke-WebRequest -UseBasicParsing -Uri $downloadUrl -OutFile $temporaryFile
    }
    Move-Item -LiteralPath $temporaryFile -Destination $bundledCloudflared -Force
    $cloudflared = $bundledCloudflared
}

& $cloudflared --version
Remove-Item -LiteralPath $stdoutLog, $stderrLog, $urlFile -Force -ErrorAction SilentlyContinue

Write-Host "Creating the public HTTPS address ..."
$process = Start-Process `
    -FilePath $cloudflared `
    -ArgumentList @("tunnel", "--no-autoupdate", "--url", $Origin) `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden `
    -PassThru

try {
    $publicUrl = $null
    $deadline = (Get-Date).AddSeconds(45)

    while ((Get-Date) -lt $deadline -and -not $process.HasExited -and -not $publicUrl) {
        Start-Sleep -Milliseconds 400
        $logText = @(
            if (Test-Path -LiteralPath $stdoutLog) { Get-Content -LiteralPath $stdoutLog -Raw -ErrorAction SilentlyContinue }
            if (Test-Path -LiteralPath $stderrLog) { Get-Content -LiteralPath $stderrLog -Raw -ErrorAction SilentlyContinue }
        ) -join "`n"
        $match = [regex]::Match($logText, 'https://[a-z0-9-]+\.trycloudflare\.com')
        if ($match.Success) {
            $publicUrl = $match.Value
        }
    }

    if (-not $publicUrl) {
        if ($process.HasExited) {
            Write-Host "Cloudflare Tunnel exited unexpectedly." -ForegroundColor Red
        }
        else {
            Write-Host "Timed out while waiting for the public address." -ForegroundColor Red
        }
        Write-Host "Log: $stderrLog"
        if (Test-Path -LiteralPath $stderrLog) {
            Get-Content -LiteralPath $stderrLog -Tail 30
        }
        exit 1
    }

    Set-Content -LiteralPath $urlFile -Value $publicUrl -Encoding utf8
    Write-Host ""
    Write-Host "Public website is online:" -ForegroundColor Green
    Write-Host $publicUrl -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Share this URL only with people you trust."
    Write-Host "Keep this window and the local website window open."
    Write-Host "Press Ctrl+C here to stop public access."
    Write-Host "The URL is also saved to: $urlFile"

    while (-not $process.HasExited) {
        Start-Sleep -Seconds 1
        $process.Refresh()
    }

    throw "Cloudflare Tunnel stopped (exit code $($process.ExitCode)). See $stderrLog"
}
finally {
    if ($null -ne $process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    }
}
