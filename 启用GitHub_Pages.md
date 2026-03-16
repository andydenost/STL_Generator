# 如何启用GitHub Pages

如果访问 `https://andydenost.github.io/STL_Generator/` 无法打开，说明GitHub Pages可能还没有启用。

## 启用步骤

### 方法一：通过GitHub网页界面

1. **访问仓库设置页面**
   - 打开：https://github.com/andydenost/STL_Generator
   - 点击仓库页面右上角的 **Settings**（设置）按钮

2. **进入Pages设置**
   - 在左侧菜单中找到 **Pages**（页面）选项
   - 点击进入Pages设置页面

3. **配置Pages**
   - 在 **Source**（源）部分，选择 **Deploy from a branch**（从分支部署）
   - 在 **Branch**（分支）下拉菜单中，选择 **main**
   - 在 **Folder**（文件夹）下拉菜单中，选择 **/ (root)**（根目录）
   - 点击 **Save**（保存）按钮

4. **等待部署**
   - GitHub会自动开始构建和部署你的网站
   - 通常需要1-2分钟
   - 部署完成后，你会看到绿色的成功提示
   - 网站地址会显示在页面顶部：`https://andydenost.github.io/STL_Generator/`

### 方法二：检查当前状态

如果已经配置过，可以检查：

1. **访问仓库的Actions标签**
   - 打开：https://github.com/andydenost/STL_Generator/actions
   - 查看是否有GitHub Pages的部署记录

2. **检查仓库设置**
   - 打开：https://github.com/andydenost/STL_Generator/settings/pages
   - 查看Pages配置是否正确

## 常见问题

### 问题1：404错误
- **原因**：GitHub Pages未启用或正在部署中
- **解决**：按照上述步骤启用，等待1-2分钟后再访问

### 问题2：页面空白
- **原因**：可能是文件路径问题
- **解决**：确保 `index.html` 文件在仓库根目录

### 问题3：显示仓库文件列表而不是网页
- **原因**：GitHub Pages未正确配置
- **解决**：检查Source是否选择了正确的分支和文件夹

## 验证网站是否可用

启用后，访问以下地址应该能看到网页：
- https://andydenost.github.io/STL_Generator/
- https://andydenost.github.io/STL_Generator/index.html

## 注意事项

- GitHub Pages只支持静态网站（HTML、CSS、JavaScript）
- 我们的项目是纯前端，完全兼容GitHub Pages
- 如果修改了代码，需要推送到GitHub，Pages会自动更新（通常需要几分钟）
