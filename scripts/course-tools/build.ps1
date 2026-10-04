[CmdletBinding()]
param([switch]$Preview)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$siteRoot = Join-Path $projectRoot 'site'
$validator = Join-Path $PSScriptRoot 'validate-site.py'
Push-Location -LiteralPath $projectRoot
try {
    & quarto render $siteRoot
    if ($LASTEXITCODE -ne 0) { throw 'Quarto render failed' }
    & python $validator (Join-Path $siteRoot '_site') --source $siteRoot
    if ($LASTEXITCODE -ne 0) { throw 'Public-output validation failed' }
    if ($Preview) {
        & quarto preview $siteRoot --no-browser
        if ($LASTEXITCODE -ne 0) { throw 'Quarto preview failed' }
    }
} finally {
    Pop-Location
}
