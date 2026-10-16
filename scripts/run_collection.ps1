# Runs collection, analysis, and balanced review export.

param(
    [int]$MinWords = 10,
    [int]$ReviewsPerGame = 1000,
    [int]$MaxRawPerGame = 10000,
    [string]$Snapshot = 'raw/steam_30_games',
    [string]$GamesFile = 'data/games.json',
    [double]$RequestInterval = 3
)
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) {
    $pythonExecutable = $bundledPython
} else {
    $pythonExecutable = (Get-Command python -ErrorAction Stop).Source
}
Push-Location -LiteralPath $projectDirectory
try {
    & $pythonExecutable -u scripts/collect_steam.py --snapshot $Snapshot --games-file $GamesFile --min-words $MinWords --reviews-per-game $ReviewsPerGame --max-raw-per-game $MaxRawPerGame --request-interval $RequestInterval
    if ($LASTEXITCODE -ne 0) { throw 'Collection interrupted or partially failed. Rerun this same command to resume saved pages and cooldowns.' }
    $analysisDirectory = 'data/processed/steam_30_games'
    & $pythonExecutable scripts/analyze_steam.py --snapshot $Snapshot --min-words $MinWords --output-dir $analysisDirectory
    if ($LASTEXITCODE -ne 0) { throw 'Collection was saved, but analysis failed. Fix the reported error and rerun analysis.' }
    & $pythonExecutable scripts/export_balanced.py --snapshot $Snapshot --output-dir $analysisDirectory --cap $ReviewsPerGame --min-words $MinWords
    if ($LASTEXITCODE -ne 0) { throw 'Analysis was saved, but balanced export failed.' }
    Write-Host "Review, announcement, and balanced review files saved in $analysisDirectory"
} finally { Pop-Location }
