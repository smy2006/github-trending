#!/usr/bin/env python3
import json
import base64
import smtplib
import requests
import gzip
import io
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465
SMTP_USER = '2789154625@qq.com'
SMTP_PASSWORD = 'nhmbgkbipglfdebb'
TO_EMAIL = '2789154625@qq.com'


class GHArchiveClient:
    """GH Archive 数据获取类"""
    
    def __init__(self):
        self.base_url = "https://data.gharchive.org"
    
    def fetch_hourly_data(self, year, month, day, hour):
        """获取指定小时的数据"""
        url = f"{self.base_url}/{year:04d}-{month:02d}-{day:02d}-{hour}.json.gz"
        
        try:
            response = requests.get(url, timeout=30, verify=False)
            if response.status_code != 200:
                return []
            
            # 解压 gzip 数据
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                content = f.read().decode('utf-8')
            
            # 解析 JSON Lines 格式
            events = []
            for line in content.strip().split('\n')[:1000]:  # 限制处理数量
                if line:
                    try:
                        events.append(json.loads(line))
                    except:
                        continue
            
            return events
        except Exception as e:
            print(f"获取 GH Archive 数据失败: {e}")
            return []
    
    def fetch_recent_summary(self, hours=6):
        """获取最近几小时的数据摘要"""
        all_events = []
        now = datetime.now() - timedelta(hours=1)  # 上一小时的数据通常最完整
        
        for i in range(hours):
            target_time = now - timedelta(hours=i)
            events = self.fetch_hourly_data(
                target_time.year, 
                target_time.month, 
                target_time.day, 
                target_time.hour
            )
            all_events.extend(events)
            if len(all_events) > 5000:  # 限制总数
                break
        
        return self._analyze_events(all_events)
    
    def _analyze_events(self, events):
        """分析事件数据"""
        stats = {
            "total_events": len(events),
            "event_types": {},
            "top_repos": {},
            "top_users": {},
            "recent_pushes": [],
            "recent_stars": []
        }
        
        for event in events:
            event_type = event.get("type", "Unknown")
            stats["event_types"][event_type] = stats["event_types"].get(event_type, 0) + 1
            
            repo_name = event.get("repo", {}).get("name", "")
            if repo_name:
                stats["top_repos"][repo_name] = stats["top_repos"].get(repo_name, 0) + 1
            
            actor_login = event.get("actor", {}).get("login", "")
            if actor_login:
                stats["top_users"][actor_login] = stats["top_users"].get(actor_login, 0) + 1
            
            # 收集最近的 Push 事件
            if event_type == "PushEvent" and len(stats["recent_pushes"]) < 5:
                stats["recent_pushes"].append({
                    "repo": repo_name,
                    "user": actor_login,
                    "time": event.get("created_at", "")
                })
            
            # 收集最近的 Star 事件
            if event_type == "WatchEvent" and len(stats["recent_stars"]) < 5:
                payload = event.get("payload", {})
                if payload.get("action") == "started":
                    stats["recent_stars"].append({
                        "repo": repo_name,
                        "user": actor_login,
                        "time": event.get("created_at", "")
                    })
        
        # 获取 Top 10
        stats["top_repos"] = dict(sorted(stats["top_repos"].items(), 
                                        key=lambda x: x[1], reverse=True)[:10])
        stats["top_users"] = dict(sorted(stats["top_users"].items(), 
                                        key=lambda x: x[1], reverse=True)[:5])
        
        return stats


def format_github_trending(data):
    """格式化 GitHub Trending 部分"""
    body = "=" * 70 + "\n"
    body += "【GitHub Trending - 今日热门项目】\n"
    body += "=" * 70 + "\n\n"
    
    if 'githubTrending' in data:
        for lang, repos in data['githubTrending'].items():
            if lang:
                body += f"\n📁 {lang.upper()}:\n"
                body += "-" * 50 + "\n"
            else:
                body += "\n📁 All Languages:\n"
                body += "-" * 50 + "\n"
            
            for i, repo in enumerate(repos[:10], 1):
                body += f"\n{i}. {repo['title']}\n"
                body += f"   🔗 https://github.com{repo['link']}\n"
                if repo.get('description'):
                    body += f"   📝 {repo['description']}\n"
                body += f"   ⭐ {repo['stars']} | +{repo['todayStars']} today\n"
            
            body += "\n"
    
    return body


def format_gh_archive(stats):
    """格式化 GH Archive 部分"""
    body = "\n" + "=" * 70 + "\n"
    body += "【GH Archive - GitHub 时间线数据分析】\n"
    body += "=" * 70 + "\n\n"
    
    body += f"📊 数据概览\n"
    body += "-" * 50 + "\n"
    body += f"   总事件数: {stats.get('total_events', 0):,}\n"
    body += f"   事件类型: {len(stats.get('event_types', {}))} 种\n\n"
    
    # 事件类型统计
    body += "📈 事件类型分布\n"
    body += "-" * 50 + "\n"
    sorted_types = sorted(stats.get('event_types', {}).items(), 
                         key=lambda x: x[1], reverse=True)[:8]
    for event_type, count in sorted_types:
        body += f"   {event_type}: {count:,}\n"
    body += "\n"
    
    # 热门仓库
    top_repos = list(stats.get('top_repos', {}).items())[:10]
    if top_repos:
        body += "🔥 最活跃仓库 Top 10\n"
        body += "-" * 50 + "\n"
        for i, (repo, count) in enumerate(top_repos, 1):
            body += f"   {i}. {repo}: {count} 个事件\n"
        body += "\n"
    
    # 活跃用户
    top_users = list(stats.get('top_users', {}).items())[:5]
    if top_users:
        body += "👥 最活跃用户 Top 5\n"
        body += "-" * 50 + "\n"
        for i, (user, count) in enumerate(top_users, 1):
            body += f"   {i}. @{user}: {count} 个事件\n"
        body += "\n"
    
    # 最近的 Star 事件
    recent_stars = stats.get('recent_stars', [])
    if recent_stars:
        body += "⭐ 最近的 Star 活动\n"
        body += "-" * 50 + "\n"
        for star in recent_stars[:5]:
            body += f"   @{star['user']} starred {star['repo']}\n"
        body += "\n"
    
    return body


def main():
    if len(sys.argv) < 2:
        print("Usage: python send_email_with_archive.py <trending_data_base64>")
        return

    trending_data_b64 = sys.argv[1]
    
    try:
        # 解码 Trending 数据
        trending_data_json = base64.b64decode(trending_data_b64).decode('utf-8')
        data = json.loads(trending_data_json)
        
        print("Trending data loaded successfully!")
        
        # 获取 GH Archive 数据
        print("Fetching GH Archive data...")
        archive_client = GHArchiveClient()
        archive_stats = archive_client.fetch_recent_summary(hours=6)
        print(f"GH Archive data fetched: {archive_stats.get('total_events', 0)} events")
        
        # 构建邮件内容
        email_body = ""
        
        # 第一部分：GitHub Trending
        email_body += format_github_trending(data)
        
        # 第二部分：GH Archive
        email_body += format_gh_archive(archive_stats)
        
        # 页脚
        email_body += "\n" + "=" * 70 + "\n"
        email_body += "📧 Sent by GitHub Actions | GitHub Trending + GH Archive\n"
        email_body += "🔗 GH Archive: https://www.gharchive.org/\n"
        email_body += "=" * 70 + "\n"
        
        print("Sending email...")
        
        # 发送邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'GitHub Daily Report - {datetime.now().strftime("%Y-%m-%d")}'
        msg['From'] = SMTP_USER
        msg['To'] = TO_EMAIL
        
        # 添加纯文本内容
        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())
        
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
