import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# 禁用 SSL 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class GitHubTrending:
    """GitHub Trending 数据抓取类"""
    
    def __init__(self):
        self.base_url = "https://github.com"
        self.trending_url = "https://github.com/trending"
    
    def fetch_trending(self, language=None, since="daily"):
        """获取 GitHub Trending 数据"""
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
        """解析 HTML 页面"""
        soup = BeautifulSoup(html, "html.parser")
        repositories = []
        
        for repo in soup.select("article.Box-row"):
            name_elem = repo.select_one("h2 a")
            repo_name = name_elem.text.strip().replace(" ", "").replace("\n", "") if name_elem else ""
            repo_link = f"{self.base_url}{name_elem['href']}" if name_elem else ""
            
            desc_elem = repo.select_one("p")
            repo_desc = desc_elem.text.strip() if desc_elem else ""
            
            lang_elem = repo.select_one("[itemprop='programmingLanguage']")
            language = lang_elem.text.strip() if lang_elem else ""
            
            stars_elem = repo.select_one("a[href$='/stargazers']")
            stars_text = stars_elem.text.strip() if stars_elem else "0"
            stars = self._parse_number(stars_text)
            
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
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return repositories
    
    def _parse_number(self, text):
        """解析数字"""
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


def print_trending_table(repos, title, limit=10):
    """打印格式化的 Trending 表格"""
    print(f"\n{'='*80}")
    print(f"[DATA] {title} (Top {min(limit, len(repos))})")
    print('='*80)
    
    if not repos:
        print("暂无数据")
        return
    
    # 表头
    print(f"{'排名':<4} {'仓库名':<30} {'语言':<12} {'星数':<10} {'今日新增':<10}")
    print('-'*80)
    
    for i, repo in enumerate(repos[:limit], 1):
        name = repo['name'][:28] if len(repo['name']) > 28 else repo['name']
        lang = repo['language'][:10] if repo['language'] else '-'
        stars = f"{repo['stars']:,}"
        today = f"+{repo['today_stars']:,}" if repo['today_stars'] > 0 else '-'
        
        print(f"{i:<4} {name:<30} {lang:<12} {stars:<10} {today:<10}")
    
    print('='*80)


def print_gharchive_info():
    """打印 GH Archive 信息"""
    print(f"\n{'='*80}")
    print("[INFO] GH Archive (GitHub 时间线存档)")
    print('='*80)
    print("""
GH Archive 是一个记录 GitHub 公共时间线活动的项目：

项目地址: https://www.gharchive.org/
数据范围: 2011年2月12日至今
更新频率: 每小时
数据格式: JSON (gzip压缩)

[数据用途]
- 分析开源项目活跃度
- 追踪技术趋势变化
- 研究开发者行为模式
- 生成趋势报告

[数据访问方式]
1. HTTP 下载: https://data.gharchive.org/YYYY-MM-DD-H.json.gz
2. BigQuery: 公开的 githubarchive 数据集
3. API: 通过 GitHub Events API

[示例数据URL]
- 单小时: https://data.gharchive.org/2024-01-01-0.json.gz
- 全天:   https://data.gharchive.org/2024-01-01-{0..23}.json.gz

[事件类型]
- PushEvent (代码推送)
- WatchEvent (Star/取消Star)
- IssuesEvent (Issue操作)
- PullRequestEvent (PR操作)
- ForkEvent (Fork仓库)
- CreateEvent/DeleteEvent (创建/删除)
- ReleaseEvent (发布Release)
- 等等...
""")
    print('='*80)


if __name__ == "__main__":
    trending = GitHubTrending()
    
    print("[START] GitHub Trending + GH Archive 数据获取工具")
    print(f"[TIME] 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取各类 Trending 数据
    print("\n[LOADING] 正在获取 GitHub Trending 数据...")
    
    all_repos = trending.fetch_trending()
    print_trending_table(all_repos, "全语言热门仓库", limit=10)
    
    python_repos = trending.fetch_trending(language="python")
    print_trending_table(python_repos, "Python 热门仓库", limit=10)
    
    js_repos = trending.fetch_trending(language="javascript")
    print_trending_table(js_repos, "JavaScript 热门仓库", limit=10)
    
    go_repos = trending.fetch_trending(language="go")
    print_trending_table(go_repos, "Go 热门仓库", limit=10)
    
    rust_repos = trending.fetch_trending(language="rust")
    print_trending_table(rust_repos, "Rust 热门仓库", limit=10)
    
    # 显示 GH Archive 信息
    print_gharchive_info()
    
    # 导出数据
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 保存 JSON
    all_data = {
        "date": date_str,
        "all_languages": all_repos,
        "python": python_repos,
        "javascript": js_repos,
        "go": go_repos,
        "rust": rust_repos
    }
    
    json_file = f"github_trending_{date_str}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n[SAVED] 数据已保存到: {json_file}")
    
    # 保存 CSV
    for lang, repos in [("all", all_repos), ("python", python_repos), 
                        ("javascript", js_repos), ("go", go_repos), ("rust", rust_repos)]:
        if repos:
            csv_file = f"github_trending_{lang}_{date_str}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=repos[0].keys())
                writer.writeheader()
                writer.writerows(repos)
            print(f"[SAVED] {lang} 数据已保存到: {csv_file}")
    
    print("\n[DONE] 全部完成！")
