param(
    [string]$DatabaseUrl = $env:MYSQL_TEST_DATABASE_URL,
    [int]$Port = 18000,
    [string]$Document = "docs/delivery/report-module-full-acceptance-results.md",
    [string]$AiToolsSecret = $env:AI_TOOLS_SECRET,
    [string]$DifyApiBaseUrl = $env:DIFY_API_BASE_URL,
    [string]$DifyApiKey = $env:DIFY_API_KEY
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ([string]::IsNullOrWhiteSpace($DatabaseUrl)) {
    throw "请先设置 MYSQL_TEST_DATABASE_URL，例如 mysql+pymysql://user:password@127.0.0.1:3306/education_service_ai_test"
}

if ($DatabaseUrl -notmatch '_test(\?|$)') {
    throw "为避免误操作生产库，MYSQL_TEST_DATABASE_URL 必须指向名称以 _test 结尾的测试库。"
}

if ([string]::IsNullOrWhiteSpace($AiToolsSecret)) {
    throw "请先设置 AI_TOOLS_SECRET，并确保 Dify 工作流 HTTP Tool 使用同一个值。"
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendRoot = Join-Path $repoRoot "backend"
$baseUrl = "http://127.0.0.1:$Port"
$logDir = Join-Path $repoRoot "storage/acceptance-logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$oldPythonPath = $env:PYTHONPATH
$oldDatabaseUrl = $env:DATABASE_URL
$oldMysqlTestDatabaseUrl = $env:MYSQL_TEST_DATABASE_URL
$oldDifyMockEnabled = $env:DIFY_MOCK_ENABLED
$oldAiToolsSecret = $env:AI_TOOLS_SECRET
$oldDifyApiBaseUrl = $env:DIFY_API_BASE_URL
$oldDifyApiKey = $env:DIFY_API_KEY

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

function Wait-BackendHealth {
    param([string]$HealthUrl)

    for ($i = 0; $i -lt 40; $i++) {
        try {
            $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) {
                return
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    throw "FastAPI 后端启动超时：$HealthUrl"
}

function Start-Backend {
    param(
        [string]$Phase,
        [string]$MockEnabled
    )

    $env:DATABASE_URL = $DatabaseUrl
    $env:MYSQL_TEST_DATABASE_URL = $DatabaseUrl
    $env:AI_TOOLS_SECRET = $AiToolsSecret
    $env:DIFY_MOCK_ENABLED = $MockEnabled
    if (-not [string]::IsNullOrWhiteSpace($DifyApiBaseUrl)) {
        $env:DIFY_API_BASE_URL = $DifyApiBaseUrl
    }
    if (-not [string]::IsNullOrWhiteSpace($DifyApiKey)) {
        $env:DIFY_API_KEY = $DifyApiKey
    }

    $stdout = Join-Path $logDir "$Phase-uvicorn.out.log"
    $stderr = Join-Path $logDir "$Phase-uvicorn.err.log"
    $process = Start-Process `
        -FilePath "python" `
        -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$Port") `
        -WorkingDirectory $backendRoot `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr
    Wait-BackendHealth "$baseUrl/health"
    return $process
}

function Stop-Backend {
    param($Process)

    if ($null -ne $Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force
        $Process.WaitForExit()
    }
}

try {
    $env:PYTHONPATH = if ([string]::IsNullOrWhiteSpace($oldPythonPath)) {
        $backendRoot
    } else {
        "$backendRoot;$oldPythonPath"
    }
    $env:DATABASE_URL = $DatabaseUrl
    $env:MYSQL_TEST_DATABASE_URL = $DatabaseUrl
    $env:AI_TOOLS_SECRET = $AiToolsSecret

    Push-Location $repoRoot
    try {
        Invoke-NativeStep "执行 Alembic 迁移" {
            python -c "from alembic.config import main; main(argv=['-c','backend/alembic.ini','upgrade','head'])"
        }
        Invoke-NativeStep "写入报告模块全量验收测试数据" {
            python backend/scripts/seed_report_full_test_data.py
        }

        $mockProcess = $null
        try {
            $mockProcess = Start-Backend -Phase "mock" -MockEnabled "true"
            Invoke-NativeStep "执行 Mock 阶段全链路验收" {
                python backend/scripts/run_report_full_acceptance.py `
                    --base-url $baseUrl `
                    --phase mock `
                    --document $Document `
                    --database-url $DatabaseUrl `
                    --ai-tools-secret $AiToolsSecret `
                    --reset-document
            }
        }
        finally {
            Stop-Backend $mockProcess
        }

        if ([string]::IsNullOrWhiteSpace($DifyApiBaseUrl) -or [string]::IsNullOrWhiteSpace($DifyApiKey)) {
            throw "真实 Dify 阶段需要设置 DIFY_API_BASE_URL 和 DIFY_API_KEY。"
        }

        $realProcess = $null
        try {
            $realProcess = Start-Backend -Phase "real-dify" -MockEnabled "false"
            Invoke-NativeStep "执行真实 Dify 阶段全链路验收" {
                python backend/scripts/run_report_full_acceptance.py `
                    --base-url $baseUrl `
                    --phase real-dify `
                    --document $Document `
                    --database-url $DatabaseUrl `
                    --ai-tools-secret $AiToolsSecret `
                    --allow-failures
            }
        }
        finally {
            Stop-Backend $realProcess
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    $env:PYTHONPATH = $oldPythonPath
    $env:DATABASE_URL = $oldDatabaseUrl
    $env:MYSQL_TEST_DATABASE_URL = $oldMysqlTestDatabaseUrl
    $env:DIFY_MOCK_ENABLED = $oldDifyMockEnabled
    $env:AI_TOOLS_SECRET = $oldAiToolsSecret
    $env:DIFY_API_BASE_URL = $oldDifyApiBaseUrl
    $env:DIFY_API_KEY = $oldDifyApiKey
}
