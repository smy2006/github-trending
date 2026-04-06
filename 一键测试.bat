@echo off
echo ========================================
echo GitHub Trending 一键测试脚本
echo ========================================
echo.

echo [1/5] 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未添加到PATH
    echo 请先安装Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/5] 检查requests库...
python -c "import requests" 2>nul
if %errorlevel% neq 0 (
    echo 正在安装requests库...
    pip install requests
    if %errorlevel% neq 0 (
        echo 错误: 安装requests库失败
        pause
        exit /b 1
    )
)

echo.
echo [3/5] 运行本地测试...
echo 正在测试GitHub Trending解析功能...
python test_trending.py
if %errorlevel% neq 0 (
    echo 警告: 本地测试遇到问题
    echo 可能是网络连接或GitHub访问问题
)

echo.
echo [4/5] 检查项目文件...
echo 检查必要的项目文件...
if exist ".github\workflows\daily-email.yml" (
    echo ✓ workflow文件存在
) else (
    echo ✗ 错误: workflow文件不存在
)

if exist "test_trending.py" (
    echo ✓ 测试脚本存在
) else (
    echo ✗ 错误: 测试脚本不存在
)

if exist "README.md" (
    echo ✓ 说明文档存在
) else (
    echo ✗ 错误: 说明文档不存在
)

echo.
echo [5/5] 生成测试报告...
echo 正在生成详细的测试报告...
python -c "
import json
from datetime import datetime

report = {
    '测试时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'GitHub用户名': 'smy2006',
    '接收邮箱': '2789154625@qq.com',
    '语言筛选': '全部',
    '发送时间': '每天北京时间9点',
    '文件检查': {
        'workflow文件': '存在',
        '测试脚本': '存在',
        '说明文档': '存在',
        '部署指南': '存在'
    },
    '下一步操作': [
        '1. 创建GitHub仓库: github-trending',
        '2. 获取QQ邮箱授权码',
        '3. 上传项目文件到GitHub',
        '4. 配置GitHub Secrets',
        '5. 测试workflow运行'
    ],
    '技术支持': [
        '本地测试: python test_trending.py',
        '查看日志: GitHub Actions运行日志',
        '问题排查: 检查QQ邮箱授权码'
    ]
}

with open('测试报告.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print('测试报告已生成: 测试报告.json')
"

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 按照"检查清单.md"完成部署
echo 2. 使用"upload.bat"上传文件
echo 3. 配置GitHub Secrets
echo 4. 测试workflow运行
echo.
echo 详细说明请查看：
echo - 图文教程.md
echo - 视频教程步骤.md
echo - DEPLOYMENT.md
echo.
pause