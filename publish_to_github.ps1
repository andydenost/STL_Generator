# GitHub发布脚本
# 使用方法：在GitHub上创建仓库后，运行此脚本并提供仓库URL

Write-Host "=== STL模型生成器 - GitHub发布脚本 ===" -ForegroundColor Green
Write-Host ""

# 检查是否已配置远程仓库
$remoteExists = git remote -v 2>&1
if ($remoteExists -and $remoteExists -notmatch "fatal") {
    Write-Host "检测到已配置的远程仓库：" -ForegroundColor Yellow
    git remote -v
    $useExisting = Read-Host "是否使用现有远程仓库？(y/n)"
    if ($useExisting -eq "y" -or $useExisting -eq "Y") {
        Write-Host "使用现有远程仓库..." -ForegroundColor Green
    } else {
        git remote remove origin
    }
}

# 如果没有远程仓库，询问用户输入
$remoteCheck = git remote -v 2>&1
if ($remoteCheck -match "fatal" -or !$remoteCheck) {
    Write-Host ""
    Write-Host "请在GitHub上创建新仓库：" -ForegroundColor Cyan
    Write-Host "1. 访问 https://github.com/new" -ForegroundColor White
    Write-Host "2. 填写仓库名称（例如：stl-revolution-generator）" -ForegroundColor White
    Write-Host "3. 选择 Public 或 Private" -ForegroundColor White
    Write-Host "4. 不要勾选 'Initialize this repository with a README'" -ForegroundColor White
    Write-Host "5. 点击 'Create repository'" -ForegroundColor White
    Write-Host ""
    
    $repoUrl = Read-Host "请输入你的GitHub仓库URL（例如：https://github.com/username/repo-name.git）"
    
    if ($repoUrl) {
        Write-Host "添加远程仓库..." -ForegroundColor Green
        git remote add origin $repoUrl
    } else {
        Write-Host "错误：未提供仓库URL，退出脚本" -ForegroundColor Red
        exit 1
    }
}

# 检查当前分支
$currentBranch = git branch --show-current
Write-Host "当前分支: $currentBranch" -ForegroundColor Yellow

# 如果分支是master，询问是否重命名为main
if ($currentBranch -eq "master") {
    $renameBranch = Read-Host "是否将分支重命名为 'main'？(y/n，推荐y)"
    if ($renameBranch -eq "y" -or $renameBranch -eq "Y") {
        Write-Host "重命名分支为 main..." -ForegroundColor Green
        git branch -M main
        $currentBranch = "main"
    }
}

# 检查是否有未提交的更改
$status = git status --porcelain
if ($status) {
    Write-Host "检测到未提交的更改，正在添加..." -ForegroundColor Yellow
    git add .
    $commitMsg = Read-Host "请输入提交信息（直接回车使用默认信息）"
    if (!$commitMsg) {
        $commitMsg = "Update files"
    }
    git commit -m $commitMsg
}

# 推送到GitHub
Write-Host ""
Write-Host "正在推送到GitHub..." -ForegroundColor Green
try {
    git push -u origin $currentBranch
    Write-Host ""
    Write-Host "✓ 成功推送到GitHub！" -ForegroundColor Green
    Write-Host ""
    
    # 获取仓库信息
    $remoteUrl = (git remote get-url origin)
    if ($remoteUrl -match "github.com/([^/]+)/([^/]+)") {
        $username = $matches[1]
        $repoName = $matches[2] -replace '\.git$', ''
        
        Write-Host "=== 发布完成 ===" -ForegroundColor Green
        Write-Host "仓库地址: https://github.com/$username/$repoName" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "启用GitHub Pages（可选）：" -ForegroundColor Yellow
        Write-Host "1. 访问: https://github.com/$username/$repoName/settings/pages" -ForegroundColor White
        Write-Host "2. Source 选择 'Deploy from a branch'" -ForegroundColor White
        Write-Host "3. Branch 选择 '$currentBranch'，文件夹选择 '/ (root)'" -ForegroundColor White
        Write-Host "4. 点击 'Save'" -ForegroundColor White
        Write-Host ""
        Write-Host "网站将在以下地址可访问：" -ForegroundColor Yellow
        Write-Host "https://$username.github.io/$repoName/stl_generator_with_preview.html" -ForegroundColor Cyan
    }
} catch {
    Write-Host ""
    Write-Host "推送失败，可能的原因：" -ForegroundColor Red
    Write-Host "1. 需要先登录GitHub（使用 git credential-manager 或 GitHub Desktop）" -ForegroundColor Yellow
    Write-Host "2. 仓库URL不正确" -ForegroundColor Yellow
    Write-Host "3. 没有推送权限" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请检查错误信息并重试" -ForegroundColor Red
}

Write-Host ""
Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
