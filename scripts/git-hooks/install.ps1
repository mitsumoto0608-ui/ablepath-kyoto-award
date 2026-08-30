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
        throw "Hook source must be valid UTF-8 without an invalid byte sequence: $Path"
    }
    if ($text.Length -gt 0 -and $text[0] -eq [char]0xFEFF) {
        throw "Hook source must not contain a UTF-8 BOM: $Path"
    }
    $normalized = $text.Replace("`r`n", "`n").Replace("`r", "`n")
    if (-not $normalized.StartsWith("#!/bin/sh`n")) {
        throw "Hook source must begin with an LF-terminated #!/bin/sh shebang."
    }
    return ,$utf8.GetBytes($normalized)
}

function Get-BytesSha256 {
    param([Parameter(Mandatory = $true)][byte[]]$Bytes)

    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return (($sha.ComputeHash($Bytes) | ForEach-Object { $_.ToString("x2") }) -join "")
    } finally {
        $sha.Dispose()
    }
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
$hooksDir = Join-Path $commonGitDir "hooks"
$installedHook = Join-Path $hooksDir "pre-push"

if (-not (Test-Path -LiteralPath $sourceHook -PathType Leaf)) {
    throw "Versioned pre-push source is missing: $sourceHook"
}

& git -C $repositoryRoot ls-files --error-unmatch -- scripts/git-hooks/pre-push 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Refusing to install an untracked hook source. Commit and review it first."
}
& git -C $repositoryRoot diff --quiet -- scripts/git-hooks/pre-push
if ($LASTEXITCODE -ne 0) {
    throw "Refusing to install a hook source with unstaged changes."
}
& git -C $repositoryRoot diff --cached --quiet -- scripts/git-hooks/pre-push
if ($LASTEXITCODE -ne 0) {
    throw "Refusing to install a hook source with staged changes."
}

$configuredHooksPath = & git -C $repositoryRoot config --get core.hooksPath
$configuredHooksPathExit = $LASTEXITCODE
if ($configuredHooksPathExit -eq 0 -and -not [string]::IsNullOrWhiteSpace($configuredHooksPath)) {
    throw "An effective core.hooksPath is configured. Refusing to change or bypass it: $configuredHooksPath"
}
if ($configuredHooksPathExit -ne 0 -and $configuredHooksPathExit -ne 1) {
    throw "Unable to inspect core.hooksPath (exit $configuredHooksPathExit)."
}

New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
[byte[]]$normalizedSourceBytes = Get-NormalizedHookBytes -Path $sourceHook
$temporaryHook = Join-Path $hooksDir ("pre-push.codex-" + [guid]::NewGuid().ToString("N") + ".tmp")
[System.IO.File]::WriteAllBytes($temporaryHook, $normalizedSourceBytes)

if (Test-Path -LiteralPath $installedHook -PathType Leaf) {
    $installedBytes = [System.IO.File]::ReadAllBytes($installedHook)
    if (-not (Test-ByteArraysEqual -Left $normalizedSourceBytes -Right $installedBytes)) {
        Remove-Item -LiteralPath $temporaryHook
        throw "A different pre-push hook already exists. Refusing to overwrite: $installedHook"
    }
    Remove-Item -LiteralPath $temporaryHook
} else {
    Move-Item -LiteralPath $temporaryHook -Destination $installedHook
}

$onWindows = $env:OS -eq "Windows_NT"
if (-not $onWindows) {
    & chmod 755 -- $installedHook
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to mark the installed hook executable: $installedHook"
    }
}

$verifiedInstalledBytes = [System.IO.File]::ReadAllBytes($installedHook)
if (-not (Test-ByteArraysEqual -Left $normalizedSourceBytes -Right $verifiedInstalledBytes)) {
    throw "Installed pre-push hook does not match the versioned source."
}
$verifiedInstalledHash = Get-BytesSha256 -Bytes $verifiedInstalledBytes

Write-Output "SERVER_SIDE_BRANCH_PROTECTION=false"
Write-Output "LOCAL_MAIN_GUARD=true"
Write-Output "PR_ONLY_AGENT_POLICY=true"
Write-Output "HUMAN_MAIN_MERGE_REQUIRED=true"
Write-Output "installed_hook=$installedHook"
Write-Output "sha256=$verifiedInstalledHash"
