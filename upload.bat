@echo off
echo ========================================
echo GitHub Trending 项目上传脚本
echo ========================================
echo.

echo 步骤1: 初始化Git仓库
git init
if %errorlevel% neq 0 (
    echo 错误: Git未安装或初始化失败
    pause
    exit /b 1
)

echo.
echo 步骤2: 添加所有文件
git add .
if %errorlevel% neq 0 (
    echo 错误: 添加文件失败
    pause
    exit /b 1
)

echo.
echo 步骤3: 提交更改
git commit -m "Initial commit: GitHub Trending email notifications"
if %errorlevel% neq 0 (
    echo 错误: 提交失败
    pause
    exit /b 1
)

echo.
echo 步骤4: 添加远程仓库
echo 请确保您已经创建了GitHub仓库: https://github.com/smy2006/github-trending
set /p REPO_URL=请输入您的GitHub仓库URL (直接回车使用默认): 
if "%REPO_URL%"=="" (
    set REPO_URL=https://github.com/smy2006/github-trending.git
)

git remote add origin %REPO_URL%
if %errorlevel% neq 0 (
    echo 错误: 添加远程仓库失败
    pause
    exit /b 1
)

echo.
echo 步骤5: 推送代码到GitHub
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo 错误: 推送失败，请检查网络和GitHub权限
    pause
    exit /b 1
)

echo.
echo ========================================
echo 恭喜！项目已成功上传到GitHub！
echo ========================================
echo.
echo 下一步操作：
echo 1. 访问您的GitHub仓库: %REPO_URL%
echo 2. 点击 "Settings" -> "Secrets and variables" -> "Actions"
echo 3. 创建两个secrets（见下面的说明）
echo.
echo Secrets配置说明：
echo 第一个secret: MAIL_USERNAME = 2789154625@qq.com
echo 第二个secret: MAIL_PASSWORD = 您的QQ邮箱授权码
echo.
pause