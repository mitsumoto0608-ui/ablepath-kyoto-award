param([string]$OutputPath = "reports/CODE_GRAPH_RAG_PILOT_STATUS.md")

$questions = @(
  @{ Name = "residual_width_callers_callees"; Query = "calculate_residual_width" },
  @{ Name = "kiyomizu_artifact_to_maplibre"; Query = "MapLibreMap|real coordinates" },
  @{ Name = "synthetic_traceback_root_cause"; Query = "throw new Error|raise .*Error" },
  @{ Name = "duplicate_helper_check"; Query = "function .*scrub|def .*scrub" }
)
$blocked = '(?i)(^|/)(data|inputs|results|cities|raw|staging|retained|generated|node_modules|dist|\.git)(/|$)|source_manifest'
$roots = @("src", "viewer/src", "docs", "README.md", "AGENTS.md")
$files = foreach ($root in $roots) {
  if (Test-Path -LiteralPath $root -PathType Container) { Get-ChildItem -LiteralPath $root -File -Recurse }
  elseif (Test-Path -LiteralPath $root -PathType Leaf) { Get-Item -LiteralPath $root }
}
$safeFiles = @($files | ForEach-Object {
  $relative = $_.FullName.Substring($PWD.Path.Length).Replace('\','/').TrimStart('/')
  if ($relative -notmatch $blocked -and $_.Extension -match '^\.(py|js|mjs|jsx|md)$') { [PSCustomObject]@{ FullName = $_.FullName; Relative = $relative } }
})

"# Code-Graph-RAG pilot status" | Set-Content -LiteralPath $OutputPath
"" | Add-Content -LiteralPath $OutputPath
"Status: PILOT_ONLY; adoption decision: REJECT. This metadata-only baseline inspected $($safeFiles.Count) safe source/documentation files. No Code-Graph-RAG package, MCP server, Docker service, or index was installed or started." | Add-Content -LiteralPath $OutputPath
foreach ($question in $questions) {
  $matches = @($safeFiles | ForEach-Object { Select-String -LiteralPath $_.FullName -Pattern $question.Query -AllMatches -ErrorAction Stop | ForEach-Object { $_.Path } })
  $groups = @($matches | Group-Object | Sort-Object Name)
  "" | Add-Content -LiteralPath $OutputPath
  "## $($question.Name)" | Add-Content -LiteralPath $OutputPath
  "outcome=ordinary_search_sufficient matched_files=$($groups.Count) matched_occurrences=$($matches.Count)" | Add-Content -LiteralPath $OutputPath
  foreach ($group in $groups) {
    $relative = $group.Name.Substring($PWD.Path.Length).Replace('\','/').TrimStart('/') -replace '[^A-Za-z0-9._/-]', '_'
    "file=$relative occurrences=$($group.Count)" | Add-Content -LiteralPath $OutputPath
  }
}
