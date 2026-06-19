# Scripts to publish the package to npm and PyPI

[CmdletBinding()]
param(
    [switch]$Npm,
    [switch]$Pypi,
    [switch]$All,
    [switch]$DryRun
)

if (-not ($Npm -or $Pypi -or $All)) {
    Write-Host "Usage: .\scripts\publish.ps1 [-Npm] [-Pypi] [-All] [-DryRun]"
    Write-Host ""
    Write-Host "  -Npm    Publish to npm registry (npx gitnexus-cgc-combo)"
    Write-Host "  -Pypi   Publish to PyPI (pip install gitnexus-cgc-combo)"
    Write-Host "  -All    Publish to both npm and PyPI"
    Write-Host "  -DryRun Dry run (npm: pack only, PyPI: --dry-run)"
    exit 1
}

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# --- npm ---
if ($Npm -or $All) {
    Write-Host ""
    Write-Host "=== npm publish ==="
    
    Remove-Item -Recurse -Force src\__pycache__ -ErrorAction SilentlyContinue
    
    if ($DryRun) {
        npm pack --dry-run
        Write-Host ""
        Write-Host "[DRY RUN] Would package and upload to npm."
        Write-Host "To publish for real: .\scripts\publish.ps1 -Npm"
        Write-Host "Make sure you are logged in: npm login"
    } else {
        npm publish
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Published to npm"
        } else {
            Write-Host "[ERR] npm publish failed"
        }
    }
}

# --- PyPI ---
if ($Pypi -or $All) {
    Write-Host ""
    Write-Host "=== PyPI publish ==="

    Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

    uv build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERR] Build failed"
        exit 1
    }

    if ($DryRun) {
        Write-Host ""
        Write-Host "[DRY RUN] Built packages:"
        Get-ChildItem dist | ForEach-Object { Write-Host "  $($_.Name) ($([math]::Round($_.Length/1KB, 1)) KB)" }
        Write-Host ""
        Write-Host "To publish for real: .\scripts\publish.ps1 -Pypi"
        Write-Host "Set your token: uv publish --token pypi-xxxxxxxx"
    } else {
        uv publish
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Published to PyPI"
        } else {
            Write-Host "[ERR] PyPI publish failed"
        }
    }
}

Write-Host ""
Write-Host "Done."
