[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [switch]$AllowDegradedGreen
)

. (Join-Path $PSScriptRoot "common.ps1")
$root = Resolve-AblePathRepositoryRoot -RepositoryRoot $RepositoryRoot
$statePath = Join-Path $root "orchestration\run_state.json"
$state = Read-RunState -RepositoryRoot $root
$heartbeats = @(Get-HeartbeatSnapshot -RepositoryRoot $root -StallMinutes 20)
$stalled = @($heartbeats | Where-Object { $_.status -eq "STALLED" })
$failed = @($heartbeats | Where-Object { $_.status -in @("FAILED", "INVALID_HEARTBEAT") })
$degraded = @($heartbeats | Where-Object { $_.status -eq "DEGRADED_GREEN" })
$active = @($heartbeats | Where-Object { $_.lane -ne "orchestrator" -and $_.status -in @("ACTIVE", "RUNNING") })
$nonTerminalTasks = @($state.tasks.PSObject.Properties | Where-Object { [string]$_.Value -notin @("GREEN", "COMPLETE", "SKIPPED_WITH_REASON", "DEGRADED_GREEN") })
$degradedTasks = @($state.tasks.PSObject.Properties | Where-Object { [string]$_.Value -eq "DEGRADED_GREEN" })
$restartRequests = @()
$requestDirectory = Join-Path $root "orchestration\logs\restart-requests"
if (Test-Path -LiteralPath $requestDirectory) {
    foreach ($requestFile in Get-ChildItem -LiteralPath $requestDirectory -Filter "*.json" -File | Sort-Object Name) {
        $restartRequests += Get-Content -LiteralPath $requestFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
    }
}
$pendingRestartRequests = @($restartRequests | Where-Object { [string]$_.status -in @("RESTART_REQUIRED", "RESUME_REQUESTED") })
$failedRestartRequests = @($restartRequests | Where-Object { [string]$_.status -in @("FAILED", "ABANDONED") })
if ($stalled.Count -gt 0 -or $failed.Count -gt 0 -or $active.Count -gt 0) {
    throw "Cannot finalize with stalled, failed, invalid, or active lanes."
}
if ($nonTerminalTasks.Count -gt 0) {
    throw ("Cannot finalize with non-terminal tasks: {0}" -f (($nonTerminalTasks | ForEach-Object { "{0}={1}" -f $_.Name, $_.Value }) -join ", "))
}
if ($pendingRestartRequests.Count -gt 0) {
    throw "Cannot finalize while restart requests are pending external recovery."
}
if (($degraded.Count -gt 0 -or $degradedTasks.Count -gt 0 -or $failedRestartRequests.Count -gt 0) -and -not $AllowDegradedGreen) {
    throw "DEGRADED_GREEN tasks/lanes or failed/abandoned restart history require explicit -AllowDegradedGreen."
}
$stopPath = Join-Path $root "orchestration\STOP_WATCHDOG"
Write-AtomicUtf8Text -Path $stopPath -Text ((Get-UtcTimestamp) + "`n")
$state.current_phase = "FINALIZED"
$state.last_checkpoint = Get-UtcTimestamp
if (-not ($state.PSObject.Properties.Name -contains "finalization")) {
    $state | Add-Member -NotePropertyName finalization -NotePropertyValue ([ordered]@{})
}
$state.finalization = [ordered]@{
    finalized_at = Get-UtcTimestamp
    heartbeats = $heartbeats
    restart_requests = $restartRequests
    restarted_lanes = @($restartRequests | Where-Object { [int]$_.restart_count -gt 0 } | ForEach-Object { $_.lane } | Sort-Object -Unique)
    stalled_lanes = @($restartRequests | Where-Object { $_.status -in @("RESTART_REQUIRED", "RESUME_REQUESTED") } | ForEach-Object { $_.lane } | Sort-Object -Unique)
    abandoned_lanes = @($restartRequests | Where-Object { $_.status -in @("FAILED", "ABANDONED") } | ForEach-Object { $_.lane } | Sort-Object -Unique)
    degraded_green_lanes = @(@($degraded | ForEach-Object { $_.lane }) + @($degradedTasks | ForEach-Object { $_.Name }) | Sort-Object -Unique)
}
Write-AtomicJson -Path $statePath -Value $state
Write-AtomicJson -Path (Join-Path $root "orchestration\logs\final_state.json") -Value $state
& (Join-Path $PSScriptRoot "heartbeat.ps1") -Lane "orchestrator" -Status "GREEN" -Phase "FINALIZED" -LastAction "final state written" -RepositoryRoot $root | Out-Null
Write-Output "Finalized orchestration state. Main and baseline refs are not modified by this script."
