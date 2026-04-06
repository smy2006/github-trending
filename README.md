# GitHub Trending 邮件通知

每天自动发送 GitHub 热门项目到您的邮箱。

## 功能特性

- 📧 每天自动发送 GitHub Trending 项目到指定邮箱
- 🌐 支持按编程语言筛选（默认显示全部）
- 📊 显示项目排名、名称、链接和描述
- ⚡ 支持手动触发测试
- 🔒 使用 GitHub Secrets 安全存储邮箱凭证

## 配置步骤

### 1. 获取 QQ 邮箱授权码
1. 登录 QQ 邮箱网页版
2. 进入"设置" → "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"IMAP/SMTP服务"
5. 获取16位授权码（不是密码）

### 2. 配置 GitHub Secrets
在 GitHub 仓库的 Settings → Secrets and variables → Actions 中创建：

- `MAIL_USERNAME`: `2789154625@qq.com`
- `MAIL_PASSWORD`: 您的QQ邮箱授权码

### 3. 手动触发测试
1. 进入仓库的 "Actions" 标签页
2. 选择 "Daily GitHub Trending Email" workflow
3. 点击 "Run workflow"
4. 可选择语言筛选（留空为"全部"）

## 邮件内容示例

```
📊 GitHub Daily Trending

日期: 2024-01-01
语言: 全部
项目数量: 20

## 今日热门项目推荐：

1. **项目名称**
   https://github.com/username/repo
   项目描述...

2. **另一个项目**
   https://github.com/another/repo
   描述...
```

## 定时设置

默认每天北京时间早上9点发送（cron: '0 9 * * *'）

## 技术支持

- GitHub 用户名: smy2006
- 接收邮箱: 2789154625@qq.com
- 语言筛选: 全部