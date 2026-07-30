[CmdletBinding()]
param(
  [string]$Root = (Get-Location).Path
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

if (-not (Test-Path -LiteralPath $backendRoot)) {
  throw "No se encontro la carpeta backend en: $repoRoot"
}

$results = [System.Collections.Generic.List[object]]::new()
$python = Get-PythonCommand -BackendRoot $backendRoot -RepoRoot $repoRoot

Write-Host "Repositorio: $repoRoot"
Write-Host "Python: $python"

Invoke-Check -Name 'backend pytest' -WorkingDirectory $backendRoot -Results $results -Action {
  & $python -W ignore::PendingDeprecationWarning -m pytest app/tests -q
}

Invoke-Check -Name 'backend ruff' -WorkingDirectory $backendRoot -Results $results -Action {
  & $python -m ruff check .
}

Invoke-Check -Name 'backend black' -WorkingDirectory $backendRoot -Results $results -Action {
  & $python -m black --check .
}

Invoke-Check -Name 'backend mypy' -WorkingDirectory $backendRoot -Results $results -Action {
  & $python -m mypy app
}

$frontendPackageJson = Join-Path $frontendRoot 'package.json'
if (-not (Test-Path -LiteralPath $frontendPackageJson)) {
  Add-SkippedCheck -Name 'frontend' -Reason 'frontend/package.json no existe' -Results $results
}
else {
  $frontendConfig = Get-Content -LiteralPath $frontendPackageJson -Raw | ConvertFrom-Json
  $scripts = @()
  if ($frontendConfig.PSObject.Properties.Name -contains 'scripts') {
    $scripts = @($frontendConfig.scripts.PSObject.Properties.Name)
  }

  $manager = Get-PackageManager -FrontendRoot $frontendRoot
  $managerCommand = $manager
  if (-not (Get-Command $managerCommand -ErrorAction SilentlyContinue)) {
    Add-SkippedCheck -Name 'frontend package manager' -Reason "No esta instalado '$managerCommand'" -Results $results
  }
  else {
    foreach ($scriptName in @('lint', 'typecheck', 'test', 'build')) {
      if ($scripts -notcontains $scriptName) {
        Add-SkippedCheck -Name "frontend $scriptName" -Reason "El script '$scriptName' no existe en package.json" -Results $results
        continue
      }

      $label = "frontend $scriptName"
      Invoke-Check -Name $label -WorkingDirectory $frontendRoot -Results $results -Action {
        switch ($managerCommand) {
          'pnpm' { & pnpm $scriptName }
          'npm' { & npm run $scriptName }
          'yarn' { & yarn $scriptName }
          default { throw "Gestor de paquetes no soportado: $managerCommand" }
        }
      }
    }
  }
}

Add-SkippedCheck -Name 'devops compose' -Reason 'Docker Compose es opcional y no se ejecuta en este wrapper' -Results $results

Write-Host ""
Write-Host 'Summary'
$results | Format-Table -AutoSize

$failures = @($results | Where-Object { $_.Status -eq 'fail' })
if ($failures.Count -gt 0) {
  exit 1
}

exit 0
