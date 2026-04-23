$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$python = "python"
$appName = "AutoKeyboard"
$entryScript = "autokeyboard.py"
$stringsFile = "strings.json"
$assetsDir = "assets"
$iconFile = Join-Path $assetsDir "icon.ico"

Write-Host "Building $appName executable..." -ForegroundColor Cyan

& $python -m pip show pyinstaller *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    & $python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install PyInstaller."
    }
}

$arguments = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onefile",
    "--name", $appName,
    "--add-data", "$stringsFile;.",
    "--add-data", "$assetsDir;$assetsDir"
)

if (Test-Path $iconFile) {
    $arguments += @("--icon", $iconFile)
}
else {
    Write-Host "Optional icon file not found at $iconFile. The EXE will be built without a Windows .ico file." -ForegroundColor Yellow
}

$arguments += $entryScript

& $python @arguments

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed."
}

Write-Host ""
Write-Host "Build completed successfully." -ForegroundColor Green
Write-Host "Executable: dist\\$appName.exe" -ForegroundColor Green
