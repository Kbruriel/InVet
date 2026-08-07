<#
.SYNOPSIS
  Ejecuta checks tecnicos de InVet y resume el resultado en una tabla.

.DESCRIPTION
  Este script centraliza las rutas habituales para validacion local:
  - modo completo: backend, frontend y cierre DevOps
  - modo backend o frontend aislado
  - modo UI automatizado para FE-00X
  - validacion opcional de un slice antes de correr checks

.EXAMPLE
  .\run-checks.ps1

.EXAMPLE
  .\run-checks.ps1 -SliceId FE-001

.EXAMPLE
  .\run-checks.ps1 -Mode backend

.EXAMPLE
  .\run-checks.ps1 -Mode frontend

.EXAMPLE
  .\run-checks.ps1 -Mode ui

.EXAMPLE
  .\run-checks.ps1 -Root C:\InVet
#>
[CmdletBinding()]
param(
  [string]$Root = (Get-Location).Path,
  [string]$SliceId,
  [ValidateSet('all', 'backend', 'frontend', 'ui')]
  [string]$Mode = 'all'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-CheckResult {
  param(
    [string]$Check,
    [string]$Status,
    [string]$Details
  )

  [pscustomobject]@{
    Check   = $Check
    Status  = $Status
    Details = $Details
  }
}

function Invoke-Check {
  param(
    [string]$Name,
    [string]$WorkingDirectory,
    [scriptblock]$Action,
    [System.Collections.Generic.List[object]]$Results
  )

  Write-Host ""
  Write-Host "[RUN] $Name"

  Push-Location -LiteralPath $WorkingDirectory
  try {
    $global:LASTEXITCODE = 0
    & $Action
    if ($LASTEXITCODE -ne 0) {
      throw "El comando finalizo con exit code $LASTEXITCODE."
    }
    $Results.Add((New-CheckResult -Check $Name -Status 'pass' -Details ''))
    Write-Host "[OK] $Name"
  }
  catch {
    $message = $_.Exception.Message
    $Results.Add((New-CheckResult -Check $Name -Status 'fail' -Details $message))
    Write-Host "[FAIL] $Name"
    Write-Host "       $message"
  }
  finally {
    Pop-Location
  }
}

function Add-SkippedCheck {
  param(
    [string]$Name,
    [string]$Reason,
    [System.Collections.Generic.List[object]]$Results
  )

  $Results.Add((New-CheckResult -Check $Name -Status 'skipped' -Details $Reason))
  Write-Host "[SKIP] $Name - $Reason"
}

function Test-FrontendHasEslintConfig {
  param([string]$FrontendRoot)

  $eslintFiles = @(
    '.eslintrc',
    '.eslintrc.js',
    '.eslintrc.cjs',
    '.eslintrc.json',
    '.eslintrc.yml',
    '.eslintrc.yaml',
    'eslint.config.js',
    'eslint.config.mjs',
    'eslint.config.cjs',
    'eslint.config.ts'
  )

  foreach ($file in $eslintFiles) {
    if (Test-Path -LiteralPath (Join-Path $FrontendRoot $file)) {
      return $true
    }
  }

  return $false
}

function Test-FrontendHasTests {
  param([string]$FrontendRoot)

  $ignoredPathPattern = '\\(node_modules|\.next|coverage|dist)\\'
  $testPatterns = @('*.test.*', '*.spec.*')
  foreach ($pattern in $testPatterns) {
    $match = Get-ChildItem -LiteralPath $FrontendRoot -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -notmatch $ignoredPathPattern } |
      Select-Object -First 1
    if ($null -ne $match) {
      return $true
    }
  }

  $testDirs = @('__tests__')
  foreach ($dir in $testDirs) {
    $match = Get-ChildItem -LiteralPath $FrontendRoot -Recurse -Directory -Filter $dir -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -notmatch $ignoredPathPattern } |
      Select-Object -First 1
    if ($null -ne $match) {
      return $true
    }
  }

  return $false
}

function Invoke-SliceValidation {
  param(
    [string]$RepoRoot,
    [string]$Id,
    [System.Collections.Generic.List[object]]$Results
  )

  if ([string]::IsNullOrWhiteSpace($Id)) {
    return $true
  }

  $normalized = $Id.Trim()
  if ($normalized -notmatch '^(BE|FE|QA)-\d{3}$') {
    Add-SkippedCheck -Name 'slice validation' -Reason "El slice '$Id' no tiene formato BE-001/FE-001/QA-001" -Results $Results
    return $false
  }

  $validator = Join-Path $RepoRoot 'backend\scripts\validate_slice_plan.py'
  if (-not (Test-Path -LiteralPath $validator)) {
    Add-SkippedCheck -Name 'slice validation' -Reason 'No existe backend/scripts/validate_slice_plan.py' -Results $Results
    return $true
  }

  Invoke-Check -Name "slice validation $normalized" -WorkingDirectory $RepoRoot -Results $Results -Action {
    & python backend/scripts/validate_slice_plan.py $normalized --stage checks
  }

  return -not @($Results | Where-Object { $_.Check -eq "slice validation $normalized" -and $_.Status -eq 'fail' }).Count
}

function Get-ContainerRelevantChanges {
  param(
    [string]$RepoRoot
  )

  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    return $null
  }

  $statusLines = & git -C $RepoRoot status --porcelain=v1 --untracked-files=normal
  if ($LASTEXITCODE -ne 0) {
    throw "No se pudo consultar git status para validar el cierre de Docker."
  }

  $allFiles = [System.Collections.Generic.List[string]]::new()
  foreach ($line in $statusLines) {
    if ([string]::IsNullOrWhiteSpace($line)) {
      continue
    }

    if ($line.Length -lt 4) {
      continue
    }

    $path = $line.Substring(3).Trim()
    if ($path -like '* -> *') {
      $path = ($path -split ' -> ')[-1]
    }

    $allFiles.Add($path)
  }

  $relevantPatterns = @(
    '^(backend[\\/]|frontend[\\/])',
    '^(docker-compose\.ya?ml|Dockerfile[^\\/]*$)',
    '^backend[\\/](requirements\.txt|pyproject\.toml)$',
    '^frontend[\\/](package\.json|package-lock\.json|pnpm-lock\.yaml|yarn\.lock)$',
    '^(package-lock\.json|pnpm-lock\.yaml|yarn\.lock)$'
  )

  $relevantFiles = [System.Collections.Generic.List[string]]::new()
  foreach ($file in $allFiles) {
    foreach ($pattern in $relevantPatterns) {
      if ($file -match $pattern) {
        $relevantFiles.Add($file)
        break
      }
    }
  }

  [pscustomobject]@{
    AllFiles      = $allFiles
    RelevantFiles = $relevantFiles
  }
}

function Invoke-DockerComposeHook {
  param(
    [string]$RepoRoot,
    [System.Collections.Generic.List[object]]$Results
  )

  $composeFile = Join-Path $RepoRoot 'docker-compose.yml'
  if (-not (Test-Path -LiteralPath $composeFile)) {
    Add-SkippedCheck -Name 'devops docker compose hook' -Reason 'No existe docker-compose.yml' -Results $Results
    return
  }

  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Add-SkippedCheck -Name 'devops docker compose hook' -Reason 'No esta instalado el comando docker' -Results $Results
    return
  }

  $changes = Get-ContainerRelevantChanges -RepoRoot $RepoRoot
  if ($null -eq $changes) {
    Add-SkippedCheck -Name 'devops docker compose hook' -Reason 'No se pudo validar git status para decidir si hace falta reiniciar contenedores' -Results $Results
    return
  }

  if ($changes.RelevantFiles.Count -eq 0) {
    $reason = 'No hay cambios pendientes que afecten contenedores'
    if ($changes.AllFiles.Count -gt 0) {
      $reason += " (cambios presentes fuera del runtime: $($changes.AllFiles -join ', '))"
    }

    Add-SkippedCheck -Name 'devops docker compose hook' -Reason $reason -Results $Results
    return
  }

  Write-Host "Cambios relevantes para contenedores: $($changes.RelevantFiles -join ', ')"
  Invoke-Check -Name 'devops docker compose hook' -WorkingDirectory $RepoRoot -Results $Results -Action {
    & docker compose up -d --build --force-recreate db backend frontend
  }
}

function Get-PythonCommand {
  param(
    [string]$BackendRoot,
    [string]$RepoRoot
  )

  $candidates = @(
    (Join-Path $BackendRoot '.venv\Scripts\python.exe'),
    (Join-Path $RepoRoot '.venv\Scripts\python.exe')
  )

  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      if (Test-PythonUsable -PythonCommand $candidate) {
        return $candidate
      }
    }
  }

  if (Get-Command python -ErrorAction SilentlyContinue) {
    if (Test-PythonUsable -PythonCommand 'python') {
      return 'python'
    }
  }

  throw "No se encontro un interprete Python ejecutable."
}

function Invoke-BackendChecks {
  param(
    [string]$BackendRoot,
    [string]$PythonCommand,
    [System.Collections.Generic.List[object]]$Results
  )

  Invoke-Check -Name 'backend pytest' -WorkingDirectory $BackendRoot -Results $Results -Action {
    & $PythonCommand -W ignore::PendingDeprecationWarning -m pytest app/tests -q
  }

  Invoke-Check -Name 'backend ruff' -WorkingDirectory $BackendRoot -Results $Results -Action {
    & $PythonCommand -m ruff check .
  }

  Invoke-Check -Name 'backend black' -WorkingDirectory $BackendRoot -Results $Results -Action {
    & $PythonCommand -m black --check .
  }

  Invoke-Check -Name 'backend mypy' -WorkingDirectory $BackendRoot -Results $Results -Action {
    & $PythonCommand -m mypy app
  }
}

function Invoke-FrontendChecks {
  param(
    [string]$FrontendRoot,
    [System.Collections.Generic.List[object]]$Results
  )

  $frontendPackageJson = Join-Path $FrontendRoot 'package.json'
  if (-not (Test-Path -LiteralPath $frontendPackageJson)) {
    Add-SkippedCheck -Name 'frontend' -Reason 'frontend/package.json no existe' -Results $Results
    return
  }

  $frontendConfig = Get-Content -LiteralPath $frontendPackageJson -Raw | ConvertFrom-Json
  $scripts = @()
  if ($frontendConfig.PSObject.Properties.Name -contains 'scripts') {
    $scripts = @($frontendConfig.scripts.PSObject.Properties.Name)
  }

  $manager = Get-PackageManager -FrontendRoot $FrontendRoot
  if (-not (Get-Command $manager -ErrorAction SilentlyContinue)) {
    Add-SkippedCheck -Name 'frontend package manager' -Reason "No esta instalado '$manager'" -Results $Results
    return
  }

  if ($scripts -contains 'lint') {
    if (Test-FrontendHasEslintConfig -FrontendRoot $FrontendRoot) {
      Invoke-Check -Name 'frontend lint' -WorkingDirectory $FrontendRoot -Results $Results -Action {
        switch ($manager) {
          'pnpm' { & pnpm lint }
          'npm' { & npm run lint }
          'yarn' { & yarn lint }
          default { throw "Gestor de paquetes no soportado: $manager" }
        }
      }
    }
    else {
      Add-SkippedCheck -Name 'frontend lint' -Reason 'No hay configuracion ESLint; next lint abriria un prompt interactivo' -Results $Results
    }
  }
  else {
    Add-SkippedCheck -Name 'frontend lint' -Reason "El script 'lint' no existe en package.json" -Results $Results
  }

  foreach ($scriptName in @('typecheck', 'test', 'build')) {
    if ($scripts -notcontains $scriptName) {
      Add-SkippedCheck -Name "frontend $scriptName" -Reason "El script '$scriptName' no existe en package.json" -Results $Results
      continue
    }

    if ($scriptName -eq 'test' -and -not (Test-FrontendHasTests -FrontendRoot $FrontendRoot)) {
      Add-SkippedCheck -Name 'frontend test' -Reason 'No hay archivos de prueba en frontend' -Results $Results
      continue
    }

    Invoke-Check -Name "frontend $scriptName" -WorkingDirectory $FrontendRoot -Results $Results -Action {
      switch ($manager) {
        'pnpm' { & pnpm $scriptName }
        'npm' { & npm run $scriptName }
        'yarn' { & yarn $scriptName }
        default { throw "Gestor de paquetes no soportado: $manager" }
      }
    }
  }
}

function Invoke-UiChecks {
  param(
    [string]$AutomationRoot,
    [System.Collections.Generic.List[object]]$Results
  )

  if (-not (Test-Path -LiteralPath $AutomationRoot)) {
    Add-SkippedCheck -Name 'ui automation' -Reason 'No existe InVet_UI_Automation' -Results $Results
    return
  }

  $scripts = Get-Content -LiteralPath (Join-Path $AutomationRoot 'package.json') -Raw | ConvertFrom-Json
  $scriptNames = @()
  if ($scripts.PSObject.Properties.Name -contains 'scripts') {
    $scriptNames = @($scripts.scripts.PSObject.Properties.Name)
  }

  foreach ($scriptName in @('test:e2e', 'test:regression')) {
    if ($scriptNames -notcontains $scriptName) {
      Add-SkippedCheck -Name "ui $scriptName" -Reason "El script '$scriptName' no existe en package.json" -Results $Results
      continue
    }

    Invoke-Check -Name "ui $scriptName" -WorkingDirectory $AutomationRoot -Results $Results -Action {
      & npm run $scriptName
    }
  }
}

function Test-PythonUsable {
  param([string]$PythonCommand)

  $probe = 'import sqlalchemy, pytest, ruff, black, mypy'
  try {
    & $PythonCommand -c $probe *> $null
    return $true
  }
  catch {
    return $false
  }
}

function Get-PackageManager {
  param([string]$FrontendRoot)

  if (Test-Path -LiteralPath (Join-Path $FrontendRoot 'pnpm-lock.yaml')) {
    return 'pnpm'
  }

  if (Test-Path -LiteralPath (Join-Path $FrontendRoot 'package-lock.json')) {
    return 'npm'
  }

  if (Test-Path -LiteralPath (Join-Path $FrontendRoot 'yarn.lock')) {
    return 'yarn'
  }

  return 'npm'
}

$repoRoot = (Resolve-Path -LiteralPath $Root).Path
$backendRoot = Join-Path $repoRoot 'backend'
$frontendRoot = Join-Path $repoRoot 'frontend'
$automationRoot = Join-Path $repoRoot 'InVet_UI_Automation'

if (-not (Test-Path -LiteralPath $backendRoot)) {
  throw "No se encontro la carpeta backend en: $repoRoot"
}

$results = [System.Collections.Generic.List[object]]::new()
$python = Get-PythonCommand -BackendRoot $backendRoot -RepoRoot $repoRoot

Write-Host "Repositorio: $repoRoot"
Write-Host "Python: $python"

$shouldRunBackend = $Mode -in @('all', 'backend')
$shouldRunFrontend = $Mode -in @('all', 'frontend')
$shouldRunUi = $Mode -eq 'ui'

$sliceValidated = Invoke-SliceValidation -RepoRoot $repoRoot -Id $SliceId -Results $results
if ($SliceId -and -not $sliceValidated) {
  Write-Host ""
  Write-Host 'Summary'
  $results | Format-Table -AutoSize
  exit 1
}

if ($shouldRunBackend) {
  Invoke-BackendChecks -BackendRoot $backendRoot -PythonCommand $python -Results $results
}

if ($shouldRunFrontend) {
  Invoke-FrontendChecks -FrontendRoot $frontendRoot -Results $results
}

if ($shouldRunUi) {
  Invoke-UiChecks -AutomationRoot $automationRoot -Results $results
}

$preHookFailures = @($results | Where-Object { $_.Status -eq 'fail' })
if ($preHookFailures.Count -eq 0 -and $Mode -eq 'all') {
  Invoke-DockerComposeHook -RepoRoot $repoRoot -Results $results
}
else {
  if ($Mode -ne 'all') {
    Add-SkippedCheck -Name 'devops docker compose hook' -Reason "No se ejecuta en modo '$Mode'" -Results $results
  }
  elseif ($preHookFailures.Count -gt 0) {
    Add-SkippedCheck -Name 'devops docker compose hook' -Reason 'No se ejecuta porque hubo fallos previos en checks' -Results $results
  }
}

Write-Host ""
Write-Host 'Summary'
$results | Format-Table -AutoSize

$failures = @($results | Where-Object { $_.Status -eq 'fail' })
if ($failures.Count -gt 0) {
  exit 1
}

exit 0
