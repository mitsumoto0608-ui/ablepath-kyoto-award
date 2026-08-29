[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [int]$StallMinutes = 20,
    [switch]$AsJson
)

. (Join-Path $PSScriptRoot "common.ps1")
$root = Resolve-AblePathRepositoryRoot -RepositoryRoot $RepositoryRoot
$state = Read-RunState -RepositoryRoot $root
$heartbeats = @(Get-HeartbeatSnapshot -RepositoryRoot $root -StallMinutes $StallMinutes)
$now = [DateTimeOffset]::UtcNow
$deadline = ConvertTo-UtcDateTimeOffset -Value $state.hard_deadline -Name "hard_deadline"
$cutover = ConvertTo-UtcDateTimeOffset -Value $state.integration_cutover -Name "integration_cutover"
$restartRequests = @()
$requestDirectory = Join-Path $root "orchestration\logs\restart-requests"
if (Test-Path -LiteralPath $requestDirectory) {
    foreach ($requestFile in Get-ChildItem -LiteralPath $requestDirectory -Filter "*.json" -File | Sort-Object Name) {
        $restartRequests += Get-Content -LiteralPath $requestFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
    }
}
$snapshot = [ordered]@{
    run_id = [string]$state.run_id
    current_phase = [string]$state.current_phase
    now = Format-UtcDateTimeOffset -Value $now
    hard_deadline = Format-UtcDateTimeOffset -Value $deadline
    minutes_to_deadline = [math]::Round(($deadline - $now).TotalMinutes, 2)
    integration_cutover = Format-UtcDateTimeOffset -Value $cutover
    integration_reserve_active = ($now -ge $cutover)
    tasks = $state.tasks
    heartbeats = $heartbeats
    stalled_lanes = @($heartbeats | Where-Object { $_.status -eq "STALLED" } | ForEach-Object { $_.lane })
    restart_requests = $restartRequests
}
if ($AsJson) {
    $snapshot | ConvertTo-Json -Depth 32
}
else {
    Write-Output ("Run: {0}" -f $snapshot.run_id)
    Write-Output ("Phase: {0}" -f $snapshot.current_phase)
    Write-Output ("Deadline: {0} ({1} minutes remaining)" -f $snapshot.hard_deadline, $snapshot.minutes_to_deadline)
    Write-Output ("Final 45-minute reserve active: {0}" -f $snapshot.integration_reserve_active)
    foreach ($heartbeat in $heartbeats) {
        Write-Output ("{0}: {1}; phase={2}; age={3}m; restart_count={4}" -f $heartbeat.lane, $heartbeat.status, $heartbeat.phase, $heartbeat.age_minutes, $heartbeat.restart_count)
    }
    foreach ($request in $restartRequests) {
        Write-Output ("restart {0}: {1}; count={2}" -f $request.lane, $request.status, $request.restart_count)
    }
    if ($snapshot.stalled_lanes.Count -gt 0) {
        Write-Warning ("STALLED: {0}" -f ($snapshot.stalled_lanes -join ", "))
        exit 2
    }
}
