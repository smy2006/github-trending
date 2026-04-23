# GitHub Trending 邮件通知

每天自动发送 GitHub 热门项目到您的邮箱，并整合 GH Archive (GitHub 时间线存档) 数据分析。

## 功能特性

- 每天自动发送 GitHub Trending 项目到指定邮箱
- 支持按编程语言筛选（Python、JavaScript、Go、Rust 等）
- 显示项目排名、名称、链接、描述、星数和今日新增
- 整合 GH Archive 数据分析
- 支持手动触发测试
- 使用 GitHub Secrets 安全存储邮箱凭证
- 数据导出为 JSON 和 CSV 格式

## 新增功能：GH Archive 整合

### GH Archive 是什么？

GH Archive 是一个记录 GitHub 公共时间线活动的开源项目：

- **项目地址**: https://www.gharchive.org/
- **数据范围**: 2011年2月12日至今
- **更新频率**: 每小时
- **数据格式**: JSON (gzip压缩)

### GH Archive 数据用途

- 分析开源项目活跃度
- 追踪技术趋势变化
- 研究开发者行为模式
- 生成趋势报告

### 新增脚本

| 脚本文件 | 功能说明 |
|---------|---------|
| `github_trending_demo.py` | 演示版本，获取 Trending 数据并展示 GH Archive 信息 |
| `github_trending_with_gharchive.py` | 完整版本，包含 GH Archive 数据下载和分析功能 |

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

## 本地运行

### 安装依赖

```bash
pip install beautifulsoup4 requests
```

### 运行演示脚本

```bash
python github_trending_demo.py
```

### 运行完整版本（包含 GH Archive 数据）

```bash
python github_trending_with_gharchive.py
```

## 邮件内容示例

```
GitHub Daily Trending

日期: 2024-01-01
语言: 全部
项目数量: 20

## 今日热门项目推荐：

1. **项目名称**
   https://github.com/username/repo
   项目描述...
   星数: 10,000 | 今日新增: +500

2. **另一个项目**
   https://github.com/another/repo
   描述...
   星数: 5,000 | 今日新增: +200
```

## 输出文件

运行脚本后会生成以下文件：

- `github_trending_YYYY-MM-DD.json` - 完整 JSON 数据
- `github_trending_all_YYYY-MM-DD.csv` - 全语言 CSV
- `github_trending_python_YYYY-MM-DD.csv` - Python 数据
- `github_trending_javascript_YYYY-MM-DD.csv` - JavaScript 数据
- `github_trending_go_YYYY-MM-DD.csv` - Go 数据
- `github_trending_rust_YYYY-MM-DD.csv` - Rust 数据

## GH Archive 数据访问

### HTTP 下载

```bash
# 单小时数据
wget https://data.gharchive.org/2024-01-01-0.json.gz

# 全天数据
wget https://data.gharchive.org/2024-01-01-{0..23}.json.gz
```

### BigQuery 查询

```sql
-- 查询某天的 Issues 事件
SELECT event as issue_status, COUNT(*) as cnt FROM (
  SELECT type, repo.name, actor.login,
    JSON_EXTRACT(payload, '$.action') as event
  FROM `githubarchive.day.20190101`
  WHERE type = 'IssuesEvent'
)
GROUP by issue_status;
```

## 定时设置

默认每天北京时间早上9点发送（cron: '0 9 * * *'）

## 项目文件说明

| 文件 | 说明 |
|-----|------|
| `send_email.py` | 邮件发送主程序 |
| `test_trending.py` | 测试脚本 |
| `github_trending_demo.py` | Trending + GH Archive 演示 |
| `github_trending_with_gharchive.py` | 完整版（含 GH Archive 数据下载） |
| `.github/workflows/daily-email.yml` | GitHub Actions 工作流 |
| `upload.bat` | 一键上传脚本 |
| `一键测试.bat` | 本地测试脚本 |

## 技术支持

- GitHub 用户名: smy2006
- 接收邮箱: 2789154625@qq.com
- 语言筛选: 全部

## 参考链接

- [GH Archive 官网](https://www.gharchive.org/)
- [GitHub Trending](https://github.com/trending)
- [GitHub Events API](https://docs.github.com/en/rest/activity/events)
