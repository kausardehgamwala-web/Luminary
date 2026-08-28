$ErrorActionPreference = "Continue"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspace = Split-Path -Parent (Split-Path -Parent $root)
$configPath = Join-Path $root "skill_repos.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$cloneRoot = Join-Path $workspace $config.clone_root

New-Item -ItemType Directory -Force $cloneRoot | Out-Null

foreach ($repo in $config.repositories) {
    $target = Join-Path $cloneRoot $repo.name
    if (Test-Path $target) {
        Write-Host "Skipping existing repo: $($repo.name)"
        continue
    }

    Write-Host "Cloning $($repo.url) -> $target"
    git clone --depth 1 $repo.url $target
}

Write-Host ""
Write-Host "Clone pass complete. Run build_skill_index.py next."
