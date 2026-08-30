[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Invoke-GitValue {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $value = & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
    return ($value | Select-Object -First 1).Trim()
}

function Get-NormalizedHookBytes {
    param([Parameter(Mandatory = $true)][string]$Path)

    $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    try {
        $text = $utf8.GetString([System.IO.File]::ReadAllBytes($Path))
    } catch {
        return $null
    }
    if ($text.Length -gt 0 -and $text[0] -eq [char]0xFEFF) {
        return $null
    }
    $normalized = $text.Replace("`r`n", "`n").Replace("`r", "`n")
    if (-not $normalized.StartsWith("#!/bin/sh`n")) {
        return $null
    }
    return ,$utf8.GetBytes($normalized)
}

function Test-ByteArraysEqual {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Left,
        [Parameter(Mandatory = $true)][byte[]]$Right
    )

    if ($Left.Length -ne $Right.Length) {
        return $false
    }
    for ($index = 0; $index -lt $Left.Length; $index++) {
        if ($Left[$index] -ne $Right[$index]) {
            return $false
        }
    }
    return $true
}

$repositoryRoot = Invoke-GitValue -Arguments @("rev-parse", "--show-toplevel")
$commonGitDirValue = Invoke-GitValue -Arguments @("rev-parse", "--git-common-dir")
$commonGitDir = if ([System.IO.Path]::IsPathRooted($commonGitDirValue)) {
    [System.IO.Path]::GetFullPath($commonGitDirValue)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot $commonGitDirValue))
}

$sourceHook = Join-Path $PSScriptRoot "pre-push"
$installedHook = Join-Path (Join-Path $commonGitDir "hooks") "pre-push"
$sourceExists = Test-Path -LiteralPath $sourceHook -PathType Leaf
$installedExists = Test-Path -LiteralPath $installedHook -PathType Leaf
$hashMatches = $false
$hooksPathConflict = $false
$sourceTrackedClean = $false
$installedExecutable = $true
$onWindows = $env:OS -eq "Windows_NT"

$configuredHooksPath = & git -C $repositoryRoot config --get core.hooksPath
$configuredHooksPathExit = $LASTEXITCODE
if ($configuredHooksPathExit -eq 0 -and -not [string]::IsNullOrWhiteSpace($configuredHooksPath)) {
    $hooksPathConflict = $true
} elseif ($configuredHooksPathExit -ne 0 -and $configuredHooksPathExit -ne 1) {
    $hooksPathConflict = $true
}

if ($sourceExists) {
    & git -C $repositoryRoot ls-files --error-unmatch -- scripts/git-hooks/pre-push 2>$null | Out-Null
    $tracked = $LASTEXITCODE -eq 0
    & git -C $repositoryRoot diff --quiet -- scripts/git-hooks/pre-push
    $unstagedClean = $LASTEXITCODE -eq 0
    & git -C $repositoryRoot diff --cached --quiet -- scripts/git-hooks/pre-push
    $stagedClean = $LASTEXITCODE -eq 0
    $sourceTrackedClean = $tracked -and $unstagedClean -and $stagedClean
}

if ($sourceExists -and $installedExists) {
    [byte[]]$normalizedSourceBytes = Get-NormalizedHookBytes -Path $sourceHook
    if ($null -ne $normalizedSourceBytes) {
        $installedBytes = [System.IO.File]::ReadAllBytes($installedHook)
        $hashMatches = Test-ByteArraysEqual -Left $normalizedSourceBytes -Right $installedBytes
    }
}

if ($installedExists -and -not $onWindows) {
    try {
        $mode = [System.IO.File]::GetUnixFileMode($installedHook)
        $installedExecutable = (
            $mode -band [System.IO.UnixFileMode]::UserExecute
        ) -ne 0
    } catch {
        $installedExecutable = $false
    }
}

$localGuard = (
    $sourceExists -and
    $installedExists -and
    $hashMatches -and
    $sourceTrackedClean -and
    $installedExecutable -and
    -not $hooksPathConflict
)

Write-Output "SERVER_SIDE_BRANCH_PROTECTION=false"
Write-Output "LOCAL_MAIN_GUARD=$($localGuard.ToString().ToLowerInvariant())"
Write-Output "PR_ONLY_AGENT_POLICY=true"
Write-Output "HUMAN_MAIN_MERGE_REQUIRED=true"
Write-Output "source_hook=$sourceHook"
Write-Output "installed_hook=$installedHook"
Write-Output "source_exists=$($sourceExists.ToString().ToLowerInvariant())"
Write-Output "installed_exists=$($installedExists.ToString().ToLowerInvariant())"
Write-Output "hash_matches=$($hashMatches.ToString().ToLowerInvariant())"
Write-Output "source_tracked_clean=$($sourceTrackedClean.ToString().ToLowerInvariant())"
Write-Output "installed_executable=$($installedExecutable.ToString().ToLowerInvariant())"
Write-Output "hooks_path_conflict=$($hooksPathConflict.ToString().ToLowerInvariant())"

if (-not $localGuard) {
    exit 1
}
