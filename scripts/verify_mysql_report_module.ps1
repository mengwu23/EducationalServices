param(
    [string]$DatabaseUrl = $env:MYSQL_TEST_DATABASE_URL
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw "请先设置 MYSQL_TEST_DATABASE_URL，例如 mysql+pymysql://user:password@127.0.0.1:3306/education_service_ai_test"
}

if ($DatabaseUrl -notmatch "_test(\?|$)") {
    throw "为避免误操作生产库，MYSQL_TEST_DATABASE_URL 必须指向名称以 _test 结尾的测试库。"
}

$env:MYSQL_TEST_DATABASE_URL = $DatabaseUrl
$env:DATABASE_URL = $DatabaseUrl
$env:DIFY_MOCK_ENABLED = "true"

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
    python -c "from alembic.config import main; main(argv=['-c','backend/alembic.ini','upgrade','head'])"
    python backend/scripts/seed_report_mysql.py
    python -m pytest backend/tests/integration/test_report_api_mysql.py -q
    python -c "from alembic.config import main; main(argv=['-c','backend/alembic.ini','current'])"
}
finally {
    Pop-Location
    $env:PYTHONPATH = $oldPythonPath
}
