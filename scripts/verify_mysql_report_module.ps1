param(
    [string]$DatabaseUrl = $env:MYSQL_TEST_DATABASE_URL
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw "请先设置 MYSQL_TEST_DATABASE_URL，例如 mysql+pymysql://user:password@127.0.0.1:3306/education_service_ai_test"
}

if ($DatabaseUrl -notmatch '_test(\?|$)') {
    throw "为避免误操作生产库，MYSQL_TEST_DATABASE_URL 必须指向名称以 _test 结尾的测试库。"
}

$env:MYSQL_TEST_DATABASE_URL = $DatabaseUrl
$env:DATABASE_URL = $DatabaseUrl
$env:DIFY_MOCK_ENABLED = "true"

function Invoke-NativeStep {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host "==> $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name 失败，退出码：$LASTEXITCODE"
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendRoot = Join-Path $repoRoot "backend"
$oldPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
    $backendRoot
} else {
    "$backendRoot;$oldPythonPath"
}

Push-Location $repoRoot
try {
    Invoke-NativeStep "执行 Alembic 迁移" {
        python -c "from alembic.config import main; main(argv=['-c','backend/alembic.ini','upgrade','head'])"
    }
    Invoke-NativeStep "写入 MySQL 联调种子数据" {
        python backend/scripts/seed_report_mysql.py
    }
    Invoke-NativeStep "运行报告模块 MySQL 集成测试" {
        python -m pytest backend/tests/integration/test_report_api_mysql.py -q
    }
    Invoke-NativeStep "查看 Alembic 当前版本" {
        python -c "from alembic.config import main; main(argv=['-c','backend/alembic.ini','current'])"
    }
}
finally {
    Pop-Location
    $env:PYTHONPATH = $oldPythonPath
}
