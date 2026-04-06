# GitHub Trending 邮件通知 - 部署指南

## 项目概述

这是一个自动化的 GitHub Actions workflow，每天定时获取 GitHub Trending 热门项目并通过邮件发送给您。

## 配置信息

- **GitHub 用户名**: smy2006
- **接收邮箱**: 2789154625@qq.com
- **语言筛选**: 全部（支持按编程语言筛选）
- **发送时间**: 每天北京时间早上9点

## 部署步骤

### 步骤1：创建 GitHub 仓库
1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 仓库名称: `github-trending`（或其他名称）
4. 描述: "Daily GitHub Trending email notifications"
5. 选择 "Public" 或 "Private"
6. 点击 "Create repository"

### 步骤2：上传项目文件
1. 在本地打开命令行
2. 进入项目目录：
   ```bash
   cd c:\Users\she\.openclaw\github-trending
   ```
3. 初始化 Git 仓库（如果还没有）：
   ```bash
   git init
   git add .
   git commit -m "Initial commit: GitHub Trending email notifications"
   ```
4. 添加远程仓库并推送：
   ```bash
   git remote add origin https://github.com/smy2006/github-trending.git
   git branch -M main
   git push -u origin main
   ```

### 步骤3：配置 QQ 邮箱授权码
1. 登录 QQ 邮箱网页版：https://mail.qq.com
2. 进入"设置" → "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"IMAP/SMTP服务"
5. 按照提示获取16位授权码（**不是邮箱密码**）
6. 保存好这个授权码

### 步骤4：设置 GitHub Secrets
1. 访问您的 GitHub 仓库页面：https://github.com/smy2006/github-trending
2. 点击 "Settings"（设置）
3. 左侧菜单选择 "Secrets and variables" → "Actions"
4. 点击 "New repository secret" 按钮
5. 创建以下两个 secrets：

**第一个 secret:**
- Name: `MAIL_USERNAME`
- Value: `2789154625@qq.com`

**第二个 secret:**
- Name: `MAIL_PASSWORD`
- Value: `您的QQ邮箱授权码`

### 步骤5：测试 workflow
1. 进入仓库的 "Actions" 标签页
2. 选择 "Daily GitHub Trending Email" workflow
3. 点击 "Run workflow" 按钮
4. 可选择语言筛选（留空为"全部"）
5. 点击 "Run workflow" 开始测试

### 步骤6：验证邮件接收
1. 检查您的 QQ 邮箱收件箱
2. 查找主题为 "📊 GitHub Daily Trending" 的邮件
3. 确认邮件内容包含 GitHub 热门项目列表

## 定时设置

workflow 使用 cron 表达式定时运行：
- `0 9 * * *` - 每天北京时间早上9点
- 支持手动触发测试

## 故障排除

### 问题1：workflow 运行失败
**可能原因**: GitHub Secrets 配置错误
**解决方案**:
1. 检查 `MAIL_USERNAME` 和 `MAIL_PASSWORD` 是否正确
2. 确认使用的是 QQ 邮箱授权码，不是密码
3. 重新获取授权码并更新 secret

### 问题2：收不到邮件
**可能原因**: 邮件被标记为垃圾邮件
**解决方案**:
1. 检查垃圾邮件文件夹
2. 将发件人添加到白名单
3. 检查邮箱容量是否已满

### 问题3：解析失败
**可能原因**: GitHub 页面结构变化
**解决方案**:
1. 运行本地测试脚本验证：
   ```bash
   python test_trending.py
   ```
2. 根据错误信息调整解析逻辑

## 自定义配置

### 修改发送时间
编辑 `.github/workflows/daily-email.yml` 文件中的 cron 表达式：
```yaml
schedule:
  - cron: '0 9 * * *'  # 修改这里的数字
```

### 修改接收邮箱
1. 更新 workflow 文件中的 `to` 字段
2. 更新 `MAIL_USERNAME` secret（如果需要）

### 添加语言筛选
workflow 支持手动触发时选择语言：
- 留空：全部语言
- 输入语言名称：如 "python", "javascript", "java" 等

## 文件结构

```
github-trending/
├── .github/
│   └── workflows/
│       └── daily-email.yml      # GitHub Actions workflow
├── test_trending.py             # 本地测试脚本
├── README.md                    # 项目说明
├── DEPLOYMENT.md               # 部署指南（本文档）
└── trending_all_*.md           # 测试输出文件
```

## 技术支持

如果遇到问题：
1. 检查 GitHub Actions 运行日志
2. 运行本地测试脚本验证解析逻辑
3. 查看生成的测试报告文件

## 更新记录

- 2026-04-06: 初始版本创建
- 功能：每日 GitHub Trending 邮件通知
- 支持：语言筛选、详细项目信息、手动触发测试