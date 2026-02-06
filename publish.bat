@echo off
chcp 65001 >nul
echo ========================================
echo STL模型生成器 - GitHub发布工具
echo ========================================
echo.

echo 请先在GitHub上创建仓库：
echo 1. 访问 https://github.com/new
echo 2. 填写仓库名称
echo 3. 选择 Public 或 Private
echo 4. 不要勾选 "Initialize this repository with a README"
echo 5. 点击 "Create repository"
echo.

set /p REPO_URL="请输入你的GitHub仓库URL（例如：https://github.com/username/repo-name.git）: "

if "%REPO_URL%"=="" (
    echo 错误：未提供仓库URL
    pause
    exit /b 1
)

echo.
echo 正在添加远程仓库...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo 当前分支: 
git branch --show-current

echo.
echo 正在推送到GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo 成功推送到GitHub！
    echo ========================================
    echo.
    echo 仓库地址: %REPO_URL%
    echo.
    echo 启用GitHub Pages（可选）：
    echo 1. 访问仓库的 Settings ^> Pages
    echo 2. Source 选择 "Deploy from a branch"
    echo 3. Branch 选择 "main"，文件夹选择 "/ (root)"
    echo 4. 点击 "Save"
    echo.
) else (
    echo.
    echo 推送失败，可能的原因：
    echo 1. 需要先登录GitHub
    echo 2. 仓库URL不正确
    echo 3. 没有推送权限
    echo.
    echo 请检查错误信息并重试
    echo.
)

pause
