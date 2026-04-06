#!/usr/bin/env python3
"""
GitHub Trending 解析逻辑测试脚本
用于验证 workflow 中的解析逻辑是否正确
"""

import requests
import re
import json
from html import unescape
from datetime import datetime

def fetch_trending(language="all"):
    """获取 GitHub Trending 页面并解析项目信息"""
    
    if language == "all":
        url = "https://github.com/trending"
    else:
        url = f"https://github.com/trending/{language}"
    
    print(f"正在获取 Trending 页面: {url}")
    
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 禁用 SSL 验证（仅用于测试）
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        
        content = response.text
        
        # 解析项目信息
        projects = []
        
        # 匹配项目信息的正则表达式
        # 匹配 <article> 标签内的项目信息
        article_pattern = r'<article[^>]*>([\s\S]*?)</article>'
        articles = re.findall(article_pattern, content)
        
        for i, article in enumerate(articles[:20], 1):
            # 提取项目名称和链接
            name_match = re.search(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', article)
            if not name_match:
                continue
                
            url_path = name_match.group(1)
            name_html = name_match.group(2)
            
            # 清理项目名称
            name = unescape(re.sub(r'<[^>]+>', '', name_html)).strip()
            
            # 提取项目描述
            desc_match = re.search(r'<p[^>]*>([\s\S]*?)</p>', article)
            description = ""
            if desc_match:
                description = unescape(re.sub(r'<[^>]+>', '', desc_match.group(1))).strip()
            
            # 提取编程语言
            lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>([^<]+)</span>', article)
            language_name = lang_match.group(1).strip() if lang_match else "Unknown"
            
            # 提取星标数
            stars_match = re.search(r'(\d+(?:,\d+)*)\s+stars', article, re.IGNORECASE)
            stars = stars_match.group(1) if stars_match else "0"
            
            # 提取今日星标数
            today_stars_match = re.search(r'(\d+(?:,\d+)*)\s+stars today', article, re.IGNORECASE)
            today_stars = today_stars_match.group(1) if today_stars_match else "0"
            
            full_url = f"https://github.com{url_path}"
            
            projects.append({
                "rank": i,
                "name": name,
                "url": full_url,
                "description": description,
                "language": language_name,
                "stars": stars,
                "stars_today": today_stars
            })
        
        return {
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": language,
            "count": len(projects),
            "projects": projects
        }
        
    except Exception as e:
        print(f"获取 Trending 页面失败: {e}")
        return {
            "error": str(e),
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": 0,
            "projects": []
        }

def format_output(data):
    """格式化输出结果"""
    
    if "error" in data:
        print(f"错误: {data['error']}")
        return
    
    print(f"\n{'='*60}")
    print(f"GitHub Trending 报告")
    print(f"{'='*60}")
    print(f"获取时间: {data['fetch_time']}")
    print(f"语言筛选: {data['language']}")
    print(f"项目数量: {data['count']}")
    print(f"{'='*60}\n")
    
    for project in data["projects"]:
        print(f"{project['rank']:2d}. {project['name']}")
        print(f"    链接: {project['url']}")
        if project['description']:
            print(f"    描述: {project['description']}")
        print(f"    语言: {project['language']}")
        print(f"    星标: {project['stars']} (今日: {project['stars_today']})")
        print()

def save_to_file(data, filename="trending_output.md"):
    """保存结果到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# GitHub Trending 测试报告\n\n")
        f.write(f"- 获取时间: {data['fetch_time']}\n")
        f.write(f"- 语言筛选: {data['language']}\n")
        f.write(f"- 项目数量: {data['count']}\n\n")
        
        f.write("## 热门项目列表\n\n")
        
        for project in data["projects"]:
            f.write(f"### {project['rank']}. {project['name']}\n")
            f.write(f"- **链接**: {project['url']}\n")
            if project['description']:
                f.write(f"- **描述**: {project['description']}\n")
            f.write(f"- **语言**: {project['language']}\n")
            f.write(f"- **星标**: {project['stars']} (今日: {project['stars_today']})\n")
            f.write("\n")
    
    print(f"结果已保存到: {filename}")

def main():
    """主函数"""
    print("GitHub Trending 解析测试")
    print("=" * 40)
    
    # 测试不同语言的 Trending
    test_languages = ["all", "python", "javascript", "java"]
    
    for lang in test_languages:
        print(f"\n测试语言: {lang}")
        print("-" * 30)
        
        data = fetch_trending(lang)
        
        if data["count"] > 0:
            print(f"成功获取 {data['count']} 个项目")
            
            # 显示前3个项目
            print("\n前3个项目:")
            for i, project in enumerate(data["projects"][:3], 1):
                print(f"  {i}. {project['name']}")
            
            # 保存完整结果
            if lang == "all":
                save_to_file(data, f"trending_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
                format_output(data)
        else:
            print("未获取到项目数据")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()