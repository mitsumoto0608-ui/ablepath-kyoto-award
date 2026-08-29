Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AblePathRepositoryRoot {
    param([string]$RepositoryRoot)
    if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
        return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
    }
    return (Resolve-Path -LiteralPath $RepositoryRoot).Path
}

function Write-AtomicUtf8Text {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $temporaryPath = Join-Path $parent (".{0}.{1}.tmp" -f (Split-Path -Leaf $Path), [guid]::NewGuid().ToString("N"))
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($temporaryPath, $Text, $utf8NoBom)
    $backupPath = Join-Path $parent (".{0}.{1}.bak" -f (Split-Path -Leaf $Path), [guid]::NewGuid().ToString("N"))
    try {
        if (Test-Path -LiteralPath $Path) {
            [System.IO.File]::Replace($temporaryPath, $Path, $backupPath)
        }
        else {
            [System.IO.File]::Move($temporaryPath, $Path)
        }
    }
    finally {
        if (Test-Path -LiteralPath $temporaryPath) {
            Remove-Item -LiteralPath $temporaryPath -Force
        }
        if (Test-Path -LiteralPath $backupPath) {
            Remove-Item -LiteralPath $backupPath -Force
        }
    }
}

function Write-AtomicJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value,
        [int]$Depth = 32
    )
    $json = $Value | ConvertTo-Json -Depth $Depth
    Write-AtomicUtf8Text -Path $Path -Text ($json + "`n")
}

function Read-RunState {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)
    $statePath = Join-Path $RepositoryRoot "orchestration\run_state.json"
    if (-not (Test-Path -LiteralPath $statePath)) {
        throw "Missing orchestration state: $statePath"
    }
    return Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function ConvertTo-UtcDateTimeOffset {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [string]$Name = "timestamp"
    )
    if ($Value -is [DateTimeOffset]) {
        return $Value.ToUniversalTime()
    }
    if ($Value -is [DateTime]) {
        $dateTime = [DateTime]$Value
        if ($dateTime.Kind -eq [DateTimeKind]::Unspecified) {
            $dateTime = [DateTime]::SpecifyKind($dateTime, [DateTimeKind]::Utc)
        }
        return ([DateTimeOffset]$dateTime).ToUniversalTime()
    }
    if (-not ($Value -is [string]) -or [string]::IsNullOrWhiteSpace([string]$Value)) {
        throw "$Name must be an ISO-8601 timestamp."
    }
    $parsed = [DateTimeOffset]::MinValue
    $styles = [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal
    if (-not [DateTimeOffset]::TryParse([string]$Value, [Globalization.CultureInfo]::InvariantCulture, $styles, [ref]$parsed)) {
        throw "$Name must be an ISO-8601 timestamp: $Value"
    }
    return $parsed.ToUniversalTime()
}

function Format-UtcDateTimeOffset {
    param([Parameter(Mandatory = $true)]$Value)
    $utc = ConvertTo-UtcDateTimeOffset -Value $Value
    return $utc.UtcDateTime.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", [Globalization.CultureInfo]::InvariantCulture)
}

function Get-HeartbeatSnapshot {
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [int]$StallMinutes = 20
    )
    $now = [DateTimeOffset]::UtcNow
    $heartbeatDirectory = Join-Path $RepositoryRoot "orchestration\heartbeats"
    $snapshots = @()
    if (-not (Test-Path -LiteralPath $heartbeatDirectory)) {
        return $snapshots
    }
    foreach ($file in Get-ChildItem -LiteralPath $heartbeatDirectory -Filter "*.json" -File | Sort-Object Name) {
        try {
            $heartbeat = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            $timestampValue = if ($heartbeat.PSObject.Properties.Name -contains "updated_at") {
                $heartbeat.updated_at
            }
            elseif ($heartbeat.PSObject.Properties.Name -contains "timestamp") {
                $heartbeat.timestamp
            }
            else {
                throw "Heartbeat is missing updated_at/timestamp."
            }
            $updatedAt = ConvertTo-UtcDateTimeOffset -Value $timestampValue -Name "heartbeat timestamp"
            $ageMinutes = ($now - $updatedAt).TotalMinutes
            $effectiveStatus = if ($ageMinutes -ge $StallMinutes -and [string]$heartbeat.status -in @("ACTIVE", "RUNNING")) { "STALLED" } else { [string]$heartbeat.status }
            $restartCount = 0
            if ($heartbeat.PSObject.Properties.Name -contains "restart_count") {
                $restartCount = [int]$heartbeat.restart_count
            }
            $snapshots += [ordered]@{
                lane = [string]$heartbeat.lane
                status = $effectiveStatus
                reported_status = [string]$heartbeat.status
                phase = [string]$heartbeat.phase
                updated_at = Format-UtcDateTimeOffset -Value $updatedAt
                age_minutes = [math]::Round($ageMinutes, 2)
                last_action = [string]$heartbeat.last_action
                restart_count = $restartCount
                source = ("orchestration/heartbeats/{0}" -f $file.Name)
            }
        }
        catch {
            $snapshots += [ordered]@{
                lane = $file.BaseName
                status = "INVALID_HEARTBEAT"
                error = $_.Exception.Message
                source = ("orchestration/heartbeats/{0}" -f $file.Name)
            }
        }
    }
    return $snapshots
}

function Get-PowerShellExecutable {
    return (Get-Process -Id $PID).Path
}

function Get-UtcTimestamp {
    return [DateTime]::UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", [Globalization.CultureInfo]::InvariantCulture)
}
