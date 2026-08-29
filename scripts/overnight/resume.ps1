[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [switch]$NoWatchdog
)

. (Join-Path $PSScriptRoot "common.ps1")
$root = Resolve-AblePathRepositoryRoot -RepositoryRoot $RepositoryRoot
$statePath = Join-Path $root "orchestration\run_state.json"
$state = Read-RunState -RepositoryRoot $root
$deadline = ConvertTo-UtcDateTimeOffset -Value $state.hard_deadline -Name "hard_deadline"
if ([DateTimeOffset]::Now -ge $deadline) {
    throw "Cannot resume after hard deadline: $deadline"
}
$completed = @($state.completed_tasks)
$remaining = @()
foreach ($property in $state.tasks.PSObject.Properties) {
    if ([string]$property.Value -notin @("GREEN", "COMPLETE", "SKIPPED_WITH_REASON", "DEGRADED_GREEN")) {
        $remaining += $property.Name
    }
}
$state.current_phase = "RESUMING"
$state.last_checkpoint = Get-UtcTimestamp
if (-not ($state.PSObject.Properties.Name -contains "resume")) {
    $state | Add-Member -NotePropertyName resume -NotePropertyValue ([ordered]@{})
}
$state.resume = [ordered]@{
    resumed_at = Get-UtcTimestamp
    completed_tasks_not_repeated = $completed
    remaining_tasks = $remaining
    restart_requests = @()
}
$restartRequestDirectory = Join-Path $root "orchestration\logs\restart-requests"
$restartRequests = @()
if (Test-Path -LiteralPath $restartRequestDirectory) {
    foreach ($requestFile in Get-ChildItem -LiteralPath $restartRequestDirectory -Filter "*.json" -File | Sort-Object Name) {
        $request = Get-Content -LiteralPath $requestFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        if ([string]$request.status -eq "RESTART_REQUIRED" -and [int]$request.restart_count -eq 1) {
            $request.status = "RESUME_REQUESTED"
            $request | Add-Member -Force -NotePropertyName resume_requested_at -NotePropertyValue (Get-UtcTimestamp)
            Write-AtomicJson -Path $requestFile.FullName -Value $request
            $restartRequests += [string]$request.lane
        }
    }
}
$state.resume.restart_requests = $restartRequests
Write-AtomicJson -Path $statePath -Value $state
& (Join-Path $PSScriptRoot "start.ps1") -RepositoryRoot $root -NoWatchdog:$NoWatchdog
Write-Output ("Resume set: {0}" -f ($remaining -join ", "))
if ($restartRequests.Count -gt 0) {
    Write-Warning ("External lane supervisor must restart exactly once: {0}" -f ($restartRequests -join ", "))
}
