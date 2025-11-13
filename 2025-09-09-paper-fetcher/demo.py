#!/usr/bin/env python3
"""
Demo script for paper fetcher - works with arXiv only to avoid API limits
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paper_fetcher import PaperFetcher
import json

def demo_arxiv_search():
    """Demo the arXiv search functionality"""
    print("=== 生成式AI推荐系统论文获取器 Demo ===\n")
    
    # Create demo configuration with broader search terms
    demo_config = {
        "search_terms": [
            "recommendation system",
            "recommender system", 
            "generative recommendation"
        ],
        "days_back": 60,  # Increase to 60 days to find more papers
        "max_results": 10,
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": ""
        }
    }
    
    # Initialize fetcher
    fetcher = PaperFetcher()
    fetcher.config = demo_config
    
    print("正在搜索arXiv上的推荐系统相关论文...")
    print(f"搜索关键词: {', '.join(demo_config['search_terms'])}")
    print(f"时间范围: 最近 {demo_config['days_back']} 天\n")
    
    # Search only arXiv to avoid rate limits
    all_papers = []
    for search_term in demo_config['search_terms']:
        print(f"搜索: {search_term}")
        papers = fetcher.search_arxiv(search_term, demo_config['max_results'])
        all_papers.extend(papers)
        print(f"找到 {len(papers)} 篇论文")
    
    # Remove duplicates
    unique_papers = fetcher.remove_duplicates(all_papers)
    unique_papers.sort(key=lambda x: x['published'], reverse=True)
    
    fetcher.papers = unique_papers
    
    print(f"\n总共找到 {len(unique_papers)} 篇不重复的论文\n")
    
    if unique_papers:
        print("=== 论文列表预览 ===")
        for i, paper in enumerate(unique_papers[:5], 1):  # Show first 5 papers
            print(f"{i}. {paper['title']}")
            authors = ', '.join(paper['authors'][:3])
            if len(paper['authors']) > 3:
                authors += ' et al.'
            print(f"   作者: {authors}")
            print(f"   发表日期: {paper['published']}")
            print(f"   链接: {paper['url']}")
            print()
        
        if len(unique_papers) > 5:
            print(f"... 还有 {len(unique_papers) - 5} 篇论文")
        
        # Save to HTML file
        output_file = fetcher.save_to_file('demo_papers.html')
        print(f"\n完整论文列表已保存到: {output_file}")
        
        # Show sample HTML content
        print("\n=== HTML格式示例 ===")
        html_sample = fetcher.format_papers_html()
        print(f"HTML内容长度: {len(html_sample)} 字符")
        
        return True
    else:
        print("未找到符合条件的论文。可能的原因:")
        print("1. 搜索时间范围内没有相关论文")
        print("2. 网络连接问题")
        print("3. API访问限制")
        return False

def show_usage_instructions():
    """Show usage instructions"""
    print("\n=== 使用说明 ===")
    print("1. 配置邮箱设置:")
    print("   编辑 config.json 文件，填入你的邮箱信息")
    print("   Gmail用户需要使用应用专用密码")
    
    print("\n2. 运行完整脚本:")
    print("   python paper_fetcher.py --config config.json")
    
    print("\n3. 仅保存到文件:")
    print("   python paper_fetcher.py --save-only")
    
    print("\n4. 发送到指定邮箱:")
    print("   python paper_fetcher.py --email recipient@example.com")
    
    print("\n更多信息请查看 README.md 文件")

if __name__ == "__main__":
    success = demo_arxiv_search()
    show_usage_instructions()
    
    if success:
        print(f"\n✅ Demo运行成功! 请查看生成的HTML文件。")
    else:
        print(f"\n❌ Demo未找到论文，请检查网络连接或调整搜索参数。")
