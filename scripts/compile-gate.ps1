[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $repoRoot "frontend"
$backendRoot = Join-Path $repoRoot "backend"

function Invoke-NativeStep {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    Write-Host "`n==> $Name" -ForegroundColor Cyan
    Push-Location $WorkingDirectory
    try {
        & $Command @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$Name failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

function Find-BackendPython {
    $candidates = @()

    if ($env:INVET_PYTHON) {
        $candidates += $env:INVET_PYTHON
    }

    $candidates += @(
        (Join-Path $backendRoot ".venv\Scripts\python.exe"),
        (Join-Path $backendRoot "venv\Scripts\python.exe")
    )

    $requiredImports = "import mypy, pytest, pytest_asyncio, ruff, sqlalchemy"

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            continue
        }

        Push-Location $backendRoot
        try {
            $previousErrorActionPreference = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            & $candidate -c $requiredImports *> $null
            $candidateExitCode = $LASTEXITCODE
            $ErrorActionPreference = $previousErrorActionPreference

            if ($candidateExitCode -eq 0) {
                return $candidate
            }
        }
        finally {
            Pop-Location
        }
    }

    throw @"
No compatible backend Python environment was found.
Create backend/.venv with Python 3.12 and install backend/requirements.txt,
or set INVET_PYTHON to the full path of a prepared Python executable.
"@
}

$npm = (Get-Command npm -ErrorAction Stop).Source
$python = Find-BackendPython
$previousBytecodeSetting = $env:PYTHONDONTWRITEBYTECODE
$env:PYTHONDONTWRITEBYTECODE = "1"

try {
    Invoke-NativeStep -Name "Frontend gate" `
        -WorkingDirectory $frontendRoot `
        -Command $npm `
        -Arguments @("run", "gate")

    Invoke-NativeStep -Name "Backend lint" `
        -WorkingDirectory $backendRoot `
        -Command $python `
        -Arguments @("-m", "ruff", "check", "app")

    Invoke-NativeStep -Name "Backend typecheck" `
        -WorkingDirectory $backendRoot `
        -Command $python `
        -Arguments @("-m", "mypy", "app")

    Invoke-NativeStep -Name "Backend tests" `
        -WorkingDirectory $backendRoot `
        -Command $python `
        -Arguments @("-m", "pytest", "app/tests", "-q")
}
finally {
    $env:PYTHONDONTWRITEBYTECODE = $previousBytecodeSetting
}

Write-Host "`nInVet compilation gate passed." -ForegroundColor Green
