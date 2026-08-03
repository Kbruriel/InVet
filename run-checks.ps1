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

$preHookFailures = @($results | Where-Object { $_.Status -eq 'fail' })
if ($preHookFailures.Count -eq 0) {
  Invoke-DockerComposeHook -RepoRoot $repoRoot -Results $results
}
else {
  Add-SkippedCheck -Name 'devops docker compose hook' -Reason 'No se ejecuta porque hubo fallos previos en checks' -Results $results
}

Write-Host ""
Write-Host 'Summary'
$results | Format-Table -AutoSize

$failures = @($results | Where-Object { $_.Status -eq 'fail' })
if ($failures.Count -gt 0) {
  exit 1
}

exit 0
