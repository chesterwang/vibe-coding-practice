#!/usr/bin/env python3
"""
Test script for paper_fetcher.py
Tests the basic functionality without sending emails
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from paper_fetcher import PaperFetcher
import json

def test_paper_fetcher():
    """Test the paper fetcher functionality"""
    print("Testing Paper Fetcher...")
    
    # Create test configuration
    test_config = {
        "search_terms": ["generative AI recommendation"],
        "days_back": 30,
        "max_results": 5,  # Small number for testing
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": ""
        }
    }
    
    # Save test config
    with open('test_config.json', 'w') as f:
        json.dump(test_config, f, indent=2)
    
    # Initialize fetcher
    fetcher = PaperFetcher('test_config.json')
    
    print("Fetching papers...")
    papers = fetcher.fetch_papers()
    
    print(f"Found {len(papers)} papers")
    
    if papers:
        print("\nFirst paper:")
        paper = papers[0]
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'][:3])}")
        print(f"Published: {paper['published']}")
        print(f"Source: {paper['source']}")
        print(f"Summary: {paper['summary'][:200]}...")
        
        # Test HTML formatting
        print("\nTesting HTML formatting...")
        html_content = fetcher.format_papers_html()
        print(f"HTML content length: {len(html_content)} characters")
        
        # Save to test file
        test_filename = fetcher.save_to_file('test_output.html')
        print(f"Test output saved to: {test_filename}")
        
    else:
        print("No papers found. This might be due to API limits or network issues.")
    
    # Clean up test files
    try:
        os.remove('test_config.json')
        print("Test config cleaned up")
    except:
        pass
    
    print("Test completed!")

if __name__ == "__main__":
    test_paper_fetcher()
