[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [Parameter(Mandatory = $true)][string]$Task,
    [Parameter(Mandatory = $true)][ValidateSet("PENDING", "IN_PROGRESS", "GREEN", "DEGRADED_GREEN", "FAILED", "BLOCKED", "SKIPPED_WITH_REASON", "COMPLETE")][string]$Status,
    [string]$CurrentPhase,
    [string[]]$ActiveWorkers
)

. (Join-Path $PSScriptRoot "common.ps1")
$root = Resolve-AblePathRepositoryRoot -RepositoryRoot $RepositoryRoot
$statePath = Join-Path $root "orchestration\run_state.json"
$state = Read-RunState -RepositoryRoot $root
$taskProperty = $state.tasks.PSObject.Properties[$Task]
if ($null -eq $taskProperty) {
    throw "Unknown task in run_state.json: $Task"
}
$taskProperty.Value = $Status
if (-not [string]::IsNullOrWhiteSpace($CurrentPhase)) {
    $state.current_phase = $CurrentPhase
}
if ($PSBoundParameters.ContainsKey("ActiveWorkers")) {
    $state.active_workers = @($ActiveWorkers)
}
if ($Status -in @("GREEN", "COMPLETE")) {
    $completed = @($state.completed_tasks)
    if ($Task -notin $completed) {
        $state.completed_tasks = @($completed + $Task)
    }
}
else {
    $state.completed_tasks = @($state.completed_tasks | Where-Object { $_ -ne $Task })
}
if ($Status -in @("FAILED", "BLOCKED")) {
    $blocked = @($state.blocked_tasks)
    if ($Task -notin $blocked) {
        $state.blocked_tasks = @($blocked + $Task)
    }
}
else {
    $state.blocked_tasks = @($state.blocked_tasks | Where-Object { $_ -ne $Task })
}
$state.last_checkpoint = Get-UtcTimestamp
Write-AtomicJson -Path $statePath -Value $state
$state | ConvertTo-Json -Depth 32
