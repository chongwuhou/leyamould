param([switch]$DryRun)

# LEYA production deployment script.
# Do not upload the repository root.
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function RunChecked([string]$Executable, [string[]]$Arguments) {
  & $Executable @Arguments
  if ($LASTEXITCODE -ne 0) { throw "$Executable failed with $LASTEXITCODE" }
}

$cfg = Get-Content (Join-Path $root "deployment/site.config.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($cfg.cloudflare.pagesProjectName -ne "leyamould") { throw "Wrong Pages project" }
if ($cfg.cloudflare.d1Database -ne "leyamould-d1") { throw "Wrong D1 database" }
if ($cfg.cloudflare.r2Bucket -ne "leyamould-r2") { throw "Wrong R2 bucket" }

RunChecked "python" @("scripts/preflight.py")

if ($DryRun) {
  RunChecked "python" @("scripts/build_release.py")
  RunChecked "python" @("scripts/test_release.py")
  Write-Host "LEYA DRY RUN PASSED. No Cloudflare deployment was performed."
  exit 0
}

# Production content comes from D1, not a stale local
# snapshot or local JSON fixtures. Fail closed without independent LEYA CI credentials.
RunChecked "python" @("scripts/fetch_build_snapshot.py")
RunChecked "python" @("scripts/build_release.py")
RunChecked "python" @("scripts/test_release.py")

$node = Join-Path $root "_local_ops/.tooling/node/node.exe"
$wrangler = Join-Path $root "_local_ops/.tooling/wrangler/node_modules/wrangler/bin/wrangler.js"
if (-not (Test-Path $node)) {
  $nodeCmd=Get-Command "node.exe" -ErrorAction SilentlyContinue
  if (-not $nodeCmd) { throw "Node.js not found" }
  $node=$nodeCmd.Source
}
if (-not (Test-Path $wrangler)) {
  throw "Wrangler not found at local LEYA runtime; install the tool under this project or use its existing runtime path"
}

RunChecked $node @($wrangler,"pages","deploy","dist","--project-name","leyamould","--branch","main")
RunChecked "python" @("scripts/verify_live.py")
Write-Host "LEYA PRODUCTION DEPLOYMENT VERIFIED."
