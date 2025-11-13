#!/usr/bin/env python3
"""
Test script for local email functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paper_fetcher import PaperFetcher
import json
import time

def test_local_email_server():
    """Test the local email server with paper fetcher"""
    print("=== 测试本地邮件服务器 ===\n")
    
    # Create test configuration with local server
    test_config = {
        "search_terms": ["recommendation system"],
        "days_back": 60,
        "max_results": 3,  # Small number for testing
        "email": {
            "use_local_server": True,
            "local_server_host": "localhost",
            "local_server_port": 1025,
            "smtp_server": "localhost",
            "smtp_port": 1025,
            "sender_email": "paper-fetcher@localhost",
            "sender_password": "",
            "recipient_email": "test-recipient@localhost",
            "use_tls": False
        }
    }
    
    # Save test config
    with open('test_local_config.json', 'w') as f:
        json.dump(test_config, f, indent=2)
    
    print("1. 初始化论文获取器...")
    fetcher = PaperFetcher('test_local_config.json')
    
    print("2. 获取少量论文进行测试...")
    papers = fetcher.fetch_papers()
    
    if papers:
        print(f"✅ 找到 {len(papers)} 篇论文")
        print(f"第一篇论文: {papers[0]['title'][:60]}...")
        
        print("\n3. 启动本地邮件服务器并发送邮件...")
        success = fetcher.send_email()
        
        if success:
            print("✅ 邮件发送成功!")
            print("\n检查 emails/ 目录中的邮件文件:")
            
            # Wait a moment for file to be written
            time.sleep(1)
            
            # List email files
            emails_dir = "emails"
            if os.path.exists(emails_dir):
                files = os.listdir(emails_dir)
                email_files = [f for f in files if f.endswith('.eml')]
                summary_files = [f for f in files if f.endswith('_summary.txt')]
                
                print(f"📧 找到 {len(email_files)} 个邮件文件:")
                for f in email_files[-3:]:  # Show last 3
                    print(f"  - {f}")
                
                if summary_files:
                    latest_summary = sorted(summary_files)[-1]
                    print(f"\n📄 最新邮件摘要 ({latest_summary}):")
                    with open(os.path.join(emails_dir, latest_summary), 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(content[:500] + "..." if len(content) > 500 else content)
            else:
                print("❌ emails/ 目录不存在")
        else:
            print("❌ 邮件发送失败")
    else:
        print("❌ 未找到论文，创建模拟邮件进行测试...")
        
        # Create fake papers for testing
        fake_papers = [{
            'title': '测试论文: 生成式AI推荐系统研究',
            'authors': ['张三', '李四'],
            'summary': '这是一篇测试论文，用于验证本地邮件服务器功能。',
            'published': '2025-09-09',
            'url': 'http://example.com/test-paper',
            'source': 'Test'
        }]
        
        fetcher.papers = fake_papers
        success = fetcher.send_email()
        
        if success:
            print("✅ 模拟邮件发送成功!")
        else:
            print("❌ 模拟邮件发送失败")
    
    # Clean up
    try:
        os.remove('test_local_config.json')
        print("\n🧹 测试配置文件已清理")
    except:
        pass
    
    print("\n=== 使用说明 ===")
    print("本地邮件服务器的优势:")
    print("✅ 无需配置真实邮箱密码")
    print("✅ 邮件保存为本地文件，便于查看")
    print("✅ 支持HTML和纯文本格式")
    print("✅ 适合开发和测试环境")
    print("\n要使用外部邮件服务器，请在配置文件中设置:")
    print('  "use_local_server": false')

if __name__ == "__main__":
    test_local_email_server()
