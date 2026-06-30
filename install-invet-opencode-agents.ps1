<#
.SYNOPSIS
  Instala agentes, comandos y documentación OpenCode para InVet.

.DESCRIPTION
  Copia el contenido de payload/.opencode y payload/docs/opencode al repositorio destino.
  No modifica código fuente de backend ni frontend. Solo instala archivos de configuración/documentación.

.PARAMETER Root
  Ruta raíz del repositorio destino. Por defecto usa el directorio actual.

.PARAMETER Force
  Sobrescribe archivos existentes. Si no se especifica, conserva archivos existentes y los reporta como omitidos.

.PARAMETER NoBackup
  Evita respaldar archivos existentes antes de sobrescribir.

.PARAMETER DryRun
  Muestra qué se copiaría sin escribir archivos.

.EXAMPLE
  .\install-invet-opencode-agents.ps1 -Root "C:\Projects\invet" -Force

.EXAMPLE
  .\install-invet-opencode-agents.ps1 -Force -DryRun
#>
[CmdletBinding()]
param(
  [string]$Root = (Get-Location).Path,
  [switch]$Force,
  [switch]$NoBackup,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info([string]$Message) { Write-Host "[InVet/OpenCode] $Message" -ForegroundColor Cyan }
function Write-Ok([string]$Message) { Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-WarnMsg([string]$Message) { Write-Host "[WARN] $Message" -ForegroundColor Yellow }

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PayloadRoot = Join-Path $ScriptRoot 'payload'

if (-not (Test-Path $PayloadRoot)) {
  throw "No se encontró la carpeta payload junto al instalador: $PayloadRoot"
}

$TargetRoot = Resolve-Path -LiteralPath $Root -ErrorAction Stop
$TargetRoot = $TargetRoot.Path
$BackupRoot = Join-Path $TargetRoot (".invet-update-backups/opencode-agents/" + (Get-Date -Format 'yyyyMMdd-HHmmss'))

Write-Info "Repositorio destino: $TargetRoot"
Write-Info "Payload origen: $PayloadRoot"

$items = @(
  @{ Source = 'payload/.opencode/agents';   Target = '.opencode/agents';   Label = 'Agentes OpenCode' },
  @{ Source = 'payload/.opencode/commands'; Target = '.opencode/commands'; Label = 'Comandos slash OpenCode' },
  @{ Source = 'payload/docs/opencode';      Target = 'docs/opencode';      Label = 'Documentación y tareas Markdown' }
)

$copied = 0
$skipped = 0
$backedUp = 0

foreach ($item in $items) {
  $src = Join-Path $ScriptRoot $item.Source
  $dst = Join-Path $TargetRoot $item.Target
  if (-not (Test-Path $src)) {
    Write-WarnMsg "No existe origen para $($item.Label): $src"
    continue
  }

  Write-Info "Instalando $($item.Label) → $($item.Target)"
  $files = Get-ChildItem -LiteralPath $src -Recurse -File
  foreach ($file in $files) {
    $relative = $file.FullName.Substring($src.Length).TrimStart('\', '/')
    $targetFile = Join-Path $dst $relative
    $targetDir = Split-Path -Parent $targetFile

    if ((Test-Path $targetFile) -and (-not $Force)) {
      Write-WarnMsg "Omitido existente: $targetFile"
      $skipped++
      continue
    }

    if ($DryRun) {
      Write-Host "DRY-RUN copy: $($file.FullName) -> $targetFile"
      continue
    }

    if (-not (Test-Path $targetDir)) {
      New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    if ((Test-Path $targetFile) -and $Force -and (-not $NoBackup)) {
      $backupFile = Join-Path $BackupRoot ($item.Target + '/' + $relative)
      $backupDir = Split-Path -Parent $backupFile
      if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
      }
      Copy-Item -LiteralPath $targetFile -Destination $backupFile -Force
      $backedUp++
    }

    Copy-Item -LiteralPath $file.FullName -Destination $targetFile -Force
    $copied++
  }
}

if (-not $DryRun) {
  Write-Ok "Instalación completada. Archivos copiados: $copied. Omitidos: $skipped. Respaldados: $backedUp."
  Write-Info "Comandos disponibles esperados: /plan-task, /implement-backend-task, /implement-frontend-task, /qa-task, /clean-architecture-review, /security-review, /run-checks, /update-docs"
  Write-Info "Siguiente ejecución sugerida: /plan-task BE-001"
  if ($Force -and (-not $NoBackup) -and $backedUp -gt 0) {
    Write-Info "Backup creado en: $BackupRoot"
  }
} else {
  Write-Ok "Dry-run completado. No se escribieron archivos."
}
