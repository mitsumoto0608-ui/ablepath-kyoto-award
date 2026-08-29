[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][ValidatePattern("^[a-z0-9_\-]+$")][string]$Lane,
    [Parameter(Mandatory = $true)][ValidateSet("ACTIVE", "RUNNING", "GREEN", "DEGRADED_GREEN", "FAILED", "BLOCKED")][string]$Status,
    [Parameter(Mandatory = $true)][string]$Phase,
    [Parameter(Mandatory = $true)][string]$LastAction,
    [int]$RestartCount = 0,
    [string]$RepositoryRoot
)

. (Join-Path $PSScriptRoot "common.ps1")
$root = Resolve-AblePathRepositoryRoot -RepositoryRoot $RepositoryRoot
$path = Join-Path $root ("orchestration\heartbeats\{0}.json" -f $Lane)
$heartbeat = [ordered]@{
    heartbeat_schema_version = "1.0.0"
    lane = $Lane
    status = $Status
    phase = $Phase
    last_action = $LastAction
    restart_count = $RestartCount
    process_id = $PID
    updated_at = Get-UtcTimestamp
}
Write-AtomicJson -Path $path -Value $heartbeat
$heartbeat | ConvertTo-Json -Depth 8
