[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [int]$PollSeconds = 60,
    [int]$StallMinutes = 20
)

. (Join-Path $PSScriptRoot "common.ps1")
$root = Resolve-AblePathRepositoryRoot -RepositoryRoot $RepositoryRoot
$state = Read-RunState -RepositoryRoot $root
$deadline = ConvertTo-UtcDateTimeOffset -Value $state.hard_deadline -Name "hard_deadline"
$logDirectory = Join-Path $root "orchestration\logs"
$snapshotPath = Join-Path $logDirectory "watchdog.latest.json"
$historyPath = Join-Path $logDirectory "watchdog.jsonl"
$stopPath = Join-Path $root "orchestration\STOP_WATCHDOG"
$requestDirectory = Join-Path $logDirectory "restart-requests"
New-Item -ItemType Directory -Path $logDirectory,$requestDirectory -Force | Out-Null
while ([DateTimeOffset]::UtcNow -lt $deadline -and -not (Test-Path -LiteralPath $stopPath)) {
    $heartbeats = @(Get-HeartbeatSnapshot -RepositoryRoot $root -StallMinutes $StallMinutes)
    $stalled = @($heartbeats | Where-Object { $_.status -eq "STALLED" })
    $laneActions = @()
    foreach ($heartbeat in $heartbeats) {
        $lane = [string]$heartbeat.lane
        if ($lane -notmatch "^[A-Za-z0-9_-]+$") {
            $laneActions += [ordered]@{ lane = $lane; status = "INVALID_LANE_ID" }
            continue
        }
        $requestPath = Join-Path $requestDirectory ("{0}.json" -f $lane.ToLowerInvariant())
        $request = $null
        if (Test-Path -LiteralPath $requestPath) {
            $request = Get-Content -LiteralPath $requestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        if ([string]$heartbeat.status -eq "STALLED" -and $null -eq $request) {
            $request = [ordered]@{
                restart_request_schema_version = "1.0.0"
                lane = $lane
                status = "RESTART_REQUIRED"
                restart_count = 1
                detected_at = Get-UtcTimestamp
                stale_heartbeat_updated_at = [string]$heartbeat.updated_at
                checkpoint = $heartbeat
                instruction = "External orchestrator must checkpoint and restart this lane once; no automatic command execution is permitted."
            }
            Write-AtomicJson -Path $requestPath -Value $request
        }
        elseif ($null -ne $request) {
            $requestStatus = [string]$request.status
            $heartbeatTime = ConvertTo-UtcDateTimeOffset -Value $heartbeat.updated_at -Name "heartbeat.updated_at"
            $detectedTime = ConvertTo-UtcDateTimeOffset -Value $request.detected_at -Name "restart.detected_at"
            $referenceTime = $detectedTime
            if ($request.PSObject.Properties.Name -contains "resume_requested_at") {
                $referenceTime = ConvertTo-UtcDateTimeOffset -Value $request.resume_requested_at -Name "restart.resume_requested_at"
            }
            if ([string]$heartbeat.status -ne "STALLED" -and $heartbeatTime -gt $detectedTime -and $requestStatus -in @("RESTART_REQUIRED", "RESUME_REQUESTED")) {
                $request.status = "RECOVERED"
                if (-not ($request.PSObject.Properties.Name -contains "recovered_at")) {
                    $request | Add-Member -NotePropertyName recovered_at -NotePropertyValue (Get-UtcTimestamp)
                }
                else {
                    $request.recovered_at = Get-UtcTimestamp
                }
                Write-AtomicJson -Path $requestPath -Value $request
            }
            elseif ([string]$heartbeat.status -eq "STALLED" -and $requestStatus -eq "RECOVERED") {
                $request.status = "FAILED"
                $request | Add-Member -Force -NotePropertyName failed_at -NotePropertyValue (Get-UtcTimestamp)
                $request | Add-Member -Force -NotePropertyName failure_reason -NotePropertyValue "second stall after the single permitted restart"
                Write-AtomicJson -Path $requestPath -Value $request
            }
            elseif ([string]$heartbeat.status -eq "STALLED" -and $requestStatus -in @("RESTART_REQUIRED", "RESUME_REQUESTED") -and ([DateTimeOffset]::UtcNow - $referenceTime).TotalMinutes -ge $StallMinutes) {
                $request.status = "FAILED"
                $request | Add-Member -Force -NotePropertyName failed_at -NotePropertyValue (Get-UtcTimestamp)
                $request | Add-Member -Force -NotePropertyName failure_reason -NotePropertyValue "lane did not recover within one stall window after its single restart token"
                Write-AtomicJson -Path $requestPath -Value $request
            }
        }
        if ($null -ne $request) {
            $laneActions += [ordered]@{ lane = $lane; status = [string]$request.status; restart_count = [int]$request.restart_count; request_path = ("orchestration/logs/restart-requests/{0}" -f (Split-Path -Leaf $requestPath)) }
        }
    }
    $attention = @($laneActions | Where-Object { $_.status -in @("RESTART_REQUIRED", "RESUME_REQUESTED", "FAILED", "INVALID_LANE_ID") })
    $snapshot = [ordered]@{
        watchdog_schema_version = "1.0.0"
        checked_at = Get-UtcTimestamp
        stall_threshold_minutes = $StallMinutes
        status = if ($attention.Count -eq 0) { "GREEN" } else { "ATTENTION_REQUIRED" }
        heartbeats = $heartbeats
        stalled_lanes = @($stalled | ForEach-Object { $_.lane })
        lane_actions = $laneActions
        required_action = if ($attention.Count -eq 0) { $null } else { "External orchestrator must consume each RESTART_REQUIRED token once; FAILED requires DEGRADED_GREEN or terminal lane classification." }
    }
    Write-AtomicJson -Path $snapshotPath -Value $snapshot
    $line = ($snapshot | ConvertTo-Json -Depth 32 -Compress) + "`n"
    [System.IO.File]::AppendAllText($historyPath, $line, (New-Object System.Text.UTF8Encoding($false)))
    Start-Sleep -Seconds $PollSeconds
}
$terminal = [ordered]@{
    checked_at = Get-UtcTimestamp
    status = if (Test-Path -LiteralPath $stopPath) { "STOP_REQUESTED" } else { "HARD_DEADLINE_REACHED" }
}
Write-AtomicJson -Path $snapshotPath -Value $terminal
