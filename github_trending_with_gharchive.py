import requests
from bs4 import BeautifulSoup
import json
import csv
import gzip
import io
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class GitHubTrending:
    """GitHub Trending 数据抓取类"""
    
    def __init__(self):
        self.base_url = "https://github.com"
        self.trending_url = "https://github.com/trending"
    
    def fetch_trending(self, language=None, since="daily"):
        """
        获取 GitHub Trending 数据
        :param language: 编程语言，例如 "python", "javascript" 等
        :param since: 时间段，可选值："daily", "weekly", "monthly"
        :return: 仓库列表
        """
        url = self.trending_url
        params = {}
        
        if language:
            url = f"{self.trending_url}/{language}"
        if since:
            params["since"] = since
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, 
                                   timeout=10, verify=False)
            response.raise_for_status()
            return self._parse_html(response.text)
        except Exception as e:
            print(f"抓取失败: {e}")
            return []
    
    def _parse_html(self, html):
        """解析 HTML 页面，提取仓库信息"""
        soup = BeautifulSoup(html, "html.parser")
        repositories = []
        
        for repo in soup.select("article.Box-row"):
            # 仓库名称
            name_elem = repo.select_one("h2 a")
            repo_name = name_elem.text.strip().replace(" ", "").replace("\n", "") if name_elem else ""
            
            # 仓库链接
            repo_link = f"{self.base_url}{name_elem['href']}" if name_elem else ""
            
            # 仓库描述
            desc_elem = repo.select_one("p")
            repo_desc = desc_elem.text.strip() if desc_elem else ""
            
            # 编程语言
            lang_elem = repo.select_one("[itemprop='programmingLanguage']")
            language = lang_elem.text.strip() if lang_elem else ""
            
            # 星数和今日新增
            stars_elem = repo.select_one("a[href$='/stargazers']")
            stars_text = stars_elem.text.strip() if stars_elem else "0"
            stars = self._parse_number(stars_text)
            
            # 今日新增星数
            today_stars_elem = repo.select_one("span.d-inline-block.float-sm-right")
            today_stars = 0
            if today_stars_elem:
                today_text = today_stars_elem.text.strip()
                today_stars = self._parse_number(today_text.split()[0])
            
            repositories.append({
                "name": repo_name,
                "link": repo_link,
                "description": repo_desc,
                "language": language,
                "stars": stars,
                "today_stars": today_stars,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "github_trending"
            })
        
        return repositories
    
    def _parse_number(self, text):
        """解析数字（支持 k/m 后缀）"""
        text = text.replace(",", "").strip()
        if not text:
            return 0
        try:
            if "k" in text.lower():
                return int(float(text.lower().replace("k", "")) * 1000)
            elif "m" in text.lower():
                return int(float(text.lower().replace("m", "")) * 1000000)
            return int(float(text))
        except:
            return 0


class GHArchiveClient:
    """GH Archive 数据获取类"""
    
    def __init__(self):
        self.base_url = "https://data.gharchive.org"
    
    def fetch_hourly_data(self, year, month, day, hour):
        """
        获取指定小时的数据
        :param year: 年份
        :param month: 月份
        :param day: 日期
        :param hour: 小时 (0-23)
        :return: 事件列表
        """
        url = f"{self.base_url}/{year:04d}-{month:02d}-{day:02d}-{hour}.json.gz"
        
        try:
            response = requests.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # 解压 gzip 数据
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                content = f.read().decode('utf-8')
            
            # 解析 JSON Lines 格式
            events = []
            for line in content.strip().split('\n'):
                if line:
                    events.append(json.loads(line))
            
            return events
        except Exception as e:
            print(f"获取 GH Archive 数据失败: {e}")
            return []
    
    def fetch_daily_summary(self, year, month, day):
        """
        获取指定日期的数据摘要（统计信息）
        :param year: 年份
        :param month: 月份
        :param day: 日期
        :return: 统计信息
        """
        all_events = []
        for hour in range(24):
            events = self.fetch_hourly_data(year, month, day, hour)
            all_events.extend(events)
        
        return self._analyze_events(all_events)
    
    def _analyze_events(self, events):
        """分析事件数据，提取统计信息"""
        stats = {
            "total_events": len(events),
            "event_types": {},
            "top_repos": {},
            "top_users": {},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "gh_archive"
        }
        
        for event in events:
            # 统计事件类型
            event_type = event.get("type", "Unknown")
            stats["event_types"][event_type] = stats["event_types"].get(event_type, 0) + 1
            
            # 统计热门仓库
            repo_name = event.get("repo", {}).get("name", "")
            if repo_name:
                stats["top_repos"][repo_name] = stats["top_repos"].get(repo_name, 0) + 1
            
            # 统计活跃用户
            actor_login = event.get("actor", {}).get("login", "")
            if actor_login:
                stats["top_users"][actor_login] = stats["top_users"].get(actor_login, 0) + 1
        
        # 获取 Top 10 仓库和用户
        stats["top_repos"] = dict(sorted(stats["top_repos"].items(), 
                                        key=lambda x: x[1], reverse=True)[:10])
        stats["top_users"] = dict(sorted(stats["top_users"].items(), 
                                        key=lambda x: x[1], reverse=True)[:10])
        
        return stats
    
    def get_yesterday_summary(self):
        """获取昨天的数据摘要"""
        yesterday = datetime.now() - timedelta(days=1)
        return self.fetch_daily_summary(yesterday.year, yesterday.month, yesterday.day)


class GitHubTrendingWithArchive:
    """整合 GitHub Trending 和 GH Archive 的主类"""
    
    def __init__(self):
        self.trending = GitHubTrending()
        self.archive = GHArchiveClient()
    
    def get_daily_report(self):
        """
        生成每日报告，包含 Trending 和 Archive 数据
        :return: 完整的报告数据
        """
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "github_trending": {},
            "gh_archive_summary": {}
        }
        
        # 1. 获取各类 Trending 数据
        print("正在获取 GitHub Trending 数据...")
        report["github_trending"]["all_languages"] = self.trending.fetch_trending()
        report["github_trending"]["python"] = self.trending.fetch_trending(language="python")
        report["github_trending"]["javascript"] = self.trending.fetch_trending(language="javascript")
        report["github_trending"]["go"] = self.trending.fetch_trending(language="go")
        report["github_trending"]["rust"] = self.trending.fetch_trending(language="rust")
        
        # 2. 获取 GH Archive 昨日数据摘要
        print("正在获取 GH Archive 数据...")
        report["gh_archive_summary"] = self.archive.get_yesterday_summary()
        
        return report
    
    def export_report(self, report, output_dir="./"):
        """
        导出报告到文件
        :param report: 报告数据
        :param output_dir: 输出目录
        """
        # 导出完整 JSON
        json_file = f"{output_dir}github_daily_report_{report['date']}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"报告已导出: {json_file}")
        
        # 导出 Trending CSV
        for lang, repos in report["github_trending"].items():
            if repos:
                csv_file = f"{output_dir}trending_{lang}_{report['date']}.csv"
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    if repos:
                        fieldnames = repos[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(repos)
                print(f"Trending 数据已导出: {csv_file}")
    
    def print_summary(self, report):
        """打印报告摘要"""
        print("\n" + "="*80)
        print(f"GitHub 每日报告 - {report['date']}")
        print("="*80)
        
        # Trending 摘要
        print("\n【GitHub Trending】")
        for lang, repos in report["github_trending"].items():
            print(f"  {lang}: {len(repos)} 个仓库")
        
        # Archive 摘要
        archive = report.get("gh_archive_summary", {})
        print("\n【GH Archive 昨日统计】")
        print(f"  总事件数: {archive.get('total_events', 0)}")
        print(f"  事件类型: {len(archive.get('event_types', {}))} 种")
        
        # Top 5 热门仓库
        top_repos = list(archive.get("top_repos", {}).items())[:5]
        if top_repos:
            print("\n  昨日最活跃仓库 Top 5:")
            for i, (repo, count) in enumerate(top_repos, 1):
                print(f"    {i}. {repo}: {count} 个事件")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    # 创建整合客户端
    client = GitHubTrendingWithArchive()
    
    # 生成每日报告
    print("开始生成 GitHub 每日报告...")
    report = client.get_daily_report()
    
    # 打印摘要
    client.print_summary(report)
    
    # 导出报告
    client.export_report(report)
    
    print("\n✅ 报告生成完成！")
