# 快速发布到GitHub指南

## 方法一：使用自动化脚本（推荐）

1. **在GitHub上创建仓库**：
   - 访问 https://github.com/new
   - 填写仓库名称（例如：`stl-revolution-generator`）
   - 选择 Public 或 Private
   - **不要勾选** "Initialize this repository with a README"
   - 点击 "Create repository"

2. **运行发布脚本**：
   ```powershell
   .\publish_to_github.ps1
   ```
   
3. **按提示操作**：
   - 输入你的GitHub仓库URL
   - 脚本会自动完成剩余步骤

## 方法二：手动命令

如果你已经创建了GitHub仓库，可以直接运行：

```bash
# 添加远程仓库（替换为你的实际URL）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 重命名分支为main（可选）
git branch -M main

# 推送到GitHub
git push -u origin main
```

## 启用GitHub Pages（在线访问）

1. 访问你的仓库 Settings → Pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 "main"，文件夹选择 "/ (root)"
4. 点击 "Save"
5. 几分钟后，网站将在 `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/stl_generator_with_preview.html` 可访问

## 提示

- 如果遇到认证问题，可以使用 GitHub Desktop 或配置 Git Credential Manager
- 建议将 `stl_generator_with_preview.html` 重命名为 `index.html`，这样访问根目录就能直接打开
