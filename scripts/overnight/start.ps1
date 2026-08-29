[CmdletBinding()]
param(
    [string]$RepositoryRoot,
    [string]$RunId,
    [double]$DurationHours = 6,
    [int]$FinalReserveMinutes = 45,
    [switch]$NoWatchdog
)

. (Join-Path $PSScriptRoot "common.ps1")
$root = Resolve-AblePathRepositoryRoot -RepositoryRoot $RepositoryRoot
$statePath = Join-Path $root "orchestration\run_state.json"
$now = [DateTimeOffset]::UtcNow
if (-not (Test-Path -LiteralPath $statePath)) {
    if ($DurationHours -le 0 -or $FinalReserveMinutes -lt 0 -or $FinalReserveMinutes -ge ($DurationHours * 60)) {
        throw "DurationHours and FinalReserveMinutes do not leave a positive execution window."
    }
    $baseSha = (& git -C $root rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($baseSha)) {
        throw "Cannot determine the repository HEAD for initial state."
    }
    $integrationBranch = (& git -C $root branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($integrationBranch)) {
        throw "Cannot determine the integration branch for initial state."
    }
    if ([string]::IsNullOrWhiteSpace($RunId)) {
        $RunId = "overnight-" + $now.UtcDateTime.ToString("yyyyMMdd-HHmmss", [Globalization.CultureInfo]::InvariantCulture)
    }
    $hardDeadline = $now.AddHours($DurationHours)
    $integrationCutover = $hardDeadline.AddMinutes(-$FinalReserveMinutes)
    $timestamp = { param([DateTimeOffset]$Value) $Value.UtcDateTime.ToString("yyyy-MM-dd'T'HH:mm:ss.fff'Z'", [Globalization.CultureInfo]::InvariantCulture) }
    $state = [ordered]@{
        orchestration_state_version = "1.0.0"
        run_id = $RunId
        started_at = (& $timestamp $now)
        hard_deadline = (& $timestamp $hardDeadline)
        integration_cutover = (& $timestamp $integrationCutover)
        base_sha = $baseSha
        integration_branch = $integrationBranch
        current_phase = "BOOTSTRAP_STATE"
        tasks = [ordered]@{
            preflight = "PENDING"
            orchestration_bootstrap = "IN_PROGRESS"
            core = "PENDING"
            kyoto_kiyomizu = "PENDING"
            kyoto_arashiyama = "PENDING"
            fujisawa_enoshima = "PENDING"
            ui_2d = "PENDING"
            ui_3d = "PENDING"
            ci = "PENDING"
            self_improvement = "PENDING"
            integration = "PENDING"
            final_verification = "PENDING"
        }
        active_workers = @("orchestrator")
        completed_tasks = @()
        blocked_tasks = @()
        budgets = [ordered]@{
            preflight_end = (& $timestamp ($now.AddMinutes(30)))
            contracts_and_citypacks_end = (& $timestamp ($now.AddHours(2)))
            runner_and_2d_ui_end = (& $timestamp ($now.AddHours(3.5)))
            hazard_and_evidence_ui_end = (& $timestamp ($now.AddHours(4.5)))
            optional_3d_end = (& $timestamp ($now.AddHours(5)))
            self_improvement_end = (& $timestamp $integrationCutover)
            hard_deadline = (& $timestamp $hardDeadline)
            self_improvement_max_minutes = 30
            repair_attempts_per_lane = 6
        }
        last_checkpoint = (& $timestamp $now)
        resume_command = "pwsh -NoProfile -File scripts/overnight/resume.ps1"
        bootstrap_source = "scripts/overnight/start.ps1"
    }
    Write-AtomicJson -Path $statePath -Value $state
}
$state = Read-RunState -RepositoryRoot $root
$deadline = ConvertTo-UtcDateTimeOffset -Value $state.hard_deadline -Name "hard_deadline"
if ($now -ge $deadline) {
    throw "Hard deadline has already passed: $deadline"
}
$pidPath = Join-Path $root "orchestration\watchdog.pid"
if (-not $NoWatchdog -and (Test-Path -LiteralPath $pidPath)) {
    $existingPidText = (Get-Content -LiteralPath $pidPath -Raw -Encoding UTF8).Trim()
    $existingPid = 0
    if ([int]::TryParse($existingPidText, [ref]$existingPid)) {
        $existingProcess = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
        if ($null -ne $existingProcess) {
            throw "A watchdog PID is already active ($existingPid). Stop that exact process before starting another watchdog."
        }
    }
    Remove-Item -LiteralPath $pidPath -Force
}
foreach ($relative in @("orchestration\heartbeats", "orchestration\logs")) {
    New-Item -ItemType Directory -Path (Join-Path $root $relative) -Force | Out-Null
}
$stopPath = Join-Path $root "orchestration\STOP_WATCHDOG"
if (Test-Path -LiteralPath $stopPath) {
    Remove-Item -LiteralPath $stopPath -Force
}
$state.current_phase = "ACTIVE"
$state.last_checkpoint = Get-UtcTimestamp
if (-not ($state.PSObject.Properties.Name -contains "watchdog")) {
    $state | Add-Member -NotePropertyName watchdog -NotePropertyValue ([ordered]@{})
}
$state.watchdog = [ordered]@{ status = if ($NoWatchdog) { "DISABLED_BY_CALLER" } else { "STARTING" } }
Write-AtomicJson -Path $statePath -Value $state
& (Join-Path $PSScriptRoot "heartbeat.ps1") -Lane "orchestrator" -Status "ACTIVE" -Phase "ACTIVE" -LastAction "overnight harness started" -RepositoryRoot $root | Out-Null
if (-not $NoWatchdog) {
    $powerShell = Get-PowerShellExecutable
    $stdout = Join-Path $root "orchestration\logs\watchdog.stdout.log"
    $stderr = Join-Path $root "orchestration\logs\watchdog.stderr.log"
    $arguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $PSScriptRoot "watchdog.ps1"), "-RepositoryRoot", $root)
    $startArguments = @{
        FilePath = $powerShell
        ArgumentList = $arguments
        RedirectStandardOutput = $stdout
        RedirectStandardError = $stderr
        PassThru = $true
    }
    if ($PSVersionTable.Platform -eq "Win32NT" -or $env:OS -eq "Windows_NT") {
        $startArguments.WindowStyle = "Hidden"
    }
    $process = Start-Process @startArguments
    Write-AtomicUtf8Text -Path $pidPath -Text (([string]$process.Id) + "`n")
    $state = Read-RunState -RepositoryRoot $root
    $state.watchdog = [ordered]@{ status = "ACTIVE"; process_id = $process.Id; started_at = Get-UtcTimestamp }
    $state.last_checkpoint = Get-UtcTimestamp
    Write-AtomicJson -Path $statePath -Value $state
}
& (Join-Path $PSScriptRoot "status.ps1") -RepositoryRoot $root
