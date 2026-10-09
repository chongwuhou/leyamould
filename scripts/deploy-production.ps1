param([switch]$DryRun)

# XUYI-specific adaptation of Demalong V1.4 production script.
# Do not execute against the Demalong site or upload the repository root.
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function RunChecked([string]$Executable, [string[]]$Arguments) {
  & $Executable @Arguments
  if ($LASTEXITCODE -ne 0) { throw "$Executable failed with $LASTEXITCODE" }
}

$cfg = Get-Content (Join-Path $root "deployment/site.config.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($cfg.cloudflare.pagesProjectName -ne "xuyi-drinkware-site") { throw "Wrong Pages project" }
if ($cfg.cloudflare.d1Database -ne "xuyi-drinkware-d1") { throw "Wrong D1 database" }
if ($cfg.cloudflare.r2Bucket -ne "xuyi-drinkware-r2") { throw "Wrong R2 bucket" }

RunChecked "python" @("scripts/preflight.py")
RunChecked "python" @("scripts/build_release.py")
RunChecked "python" @("scripts/test_release.py")

if ($DryRun) {
  Write-Host "XUYI DRY RUN PASSED. No Cloudflare deployment was performed."
  exit 0
}

$node = Join-Path $root "_local_ops/.tooling/node/node.exe"
$wrangler = Join-Path $root "_local_ops/.tooling/wrangler/node_modules/wrangler/bin/wrangler.js"
if (-not (Test-Path $node)) {
  $nodeCmd=Get-Command "node.exe" -ErrorAction SilentlyContinue
  if (-not $nodeCmd) { throw "Node.js not found" }
  $node=$nodeCmd.Source
}
if (-not (Test-Path $wrangler)) {
  throw "Wrangler not found at local XUYI runtime; install the tool under this project or use its existing runtime path"
}

RunChecked $node @($wrangler,"pages","deploy","dist","--project-name","xuyi-drinkware-site","--branch","main")
RunChecked "python" @("scripts/verify_live.py")
Write-Host "XUYI PRODUCTION DEPLOYMENT VERIFIED. Demalong remains unchanged."