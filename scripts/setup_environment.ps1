$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$projectPython = Join-Path $projectRoot '.runtime\nuget-python313\tools\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    $projectPython = (& py -3.13 -B -c 'import sys; print(sys.executable)' | Select-Object -Last 1)
    if ($LASTEXITCODE -ne 0 -or -not $projectPython) { throw 'Python 3.13 is required. See docs/06_running_zh.md.' }
}
& $projectPython -B -c 'import sys; assert sys.version_info[:2] == (3, 13), sys.version'
if ($LASTEXITCODE -ne 0) { throw 'Expected Python 3.13' }
& $projectPython -m venv (Join-Path $projectRoot '.venv')
if ($LASTEXITCODE -ne 0) { throw 'venv creation failed' }
$projectVenvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$projectSourcePath = Join-Path $projectRoot 'src'
& $projectVenvPython -B -c 'import pathlib, site, sys; pathlib.Path(site.getsitepackages()[-1], "nurbs_knowledge_local.pth").write_text(sys.argv[1] + "\n", encoding="utf-8")' $projectSourcePath
if ($LASTEXITCODE -ne 0) { throw 'Local package registration failed' }
& $projectVenvPython -B -c 'import sys, nurbs_knowledge; print(sys.version); print(nurbs_knowledge.__file__)'
if ($LASTEXITCODE -ne 0) { throw 'Import check failed' }
