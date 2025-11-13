#!/usr/bin/env python3
"""
Academic Paper Fetcher for Generative AI Recommendation Systems
Fetches recent papers from arXiv and sends them via email
"""

import requests
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import argparse
import logging
from typing import List, Dict
import re
import time
from local_smtp_server import SMTPServerManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaperFetcher:
    def __init__(self, config_file: str = None):
        """Initialize the paper fetcher with configuration"""
        self.config = self.load_config(config_file)
        self.papers = []
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "search_terms": [
                "generative AI recommendation",
                "generative recommendation system", 
                "LLM recommendation",
                "large language model recommendation",
                "generative retrieval recommendation"
            ],
            "days_back": 30,
            "max_results": 50,
            "email": {
                "use_local_server": True,
                "local_server_host": "localhost",
                "local_server_port": 1025,
                "smtp_server": "localhost",
                "smtp_port": 1025,
                "sender_email": "paper-fetcher@localhost",
                "sender_password": "",
                "recipient_email": "recipient@localhost",
                "use_tls": False
            }
        }
        
        if config_file:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except FileNotFoundError:
                logger.warning(f"Config file {config_file} not found, using defaults")
        
        return default_config
    
    def search_arxiv(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search arXiv for papers matching the query"""
        logger.info(f"Searching arXiv for: {query}")
        
        # Calculate date threshold
        date_threshold = datetime.now() - timedelta(days=self.config['days_back'])
        
        # Construct arXiv API query
        base_url = "http://export.arxiv.org/api/query"
        search_query = f'all:"{query}"'
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', namespace):
                # Extract paper information
                paper_id = entry.find('atom:id', namespace).text
                title = entry.find('atom:title', namespace).text.strip()
                summary = entry.find('atom:summary', namespace).text.strip()
                
                # Get authors
                authors = []
                for author in entry.findall('atom:author', namespace):
                    name = author.find('atom:name', namespace).text
                    authors.append(name)
                
                # Get publication date
                published = entry.find('atom:published', namespace).text
                pub_date = datetime.strptime(published[:10], '%Y-%m-%d')
                
                # Only include papers from the last month
                if pub_date >= date_threshold:
                    papers.append({
                        'id': paper_id,
                        'title': title,
                        'authors': authors,
                        'summary': summary,
                        'published': pub_date.strftime('%Y-%m-%d'),
                        'url': paper_id,
                        'source': 'arXiv'
                    })
            
            logger.info(f"Found {len(papers)} recent papers for query: {query}")
            return papers
            
        except requests.RequestException as e:
            logger.error(f"Error searching arXiv: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"Error parsing arXiv response: {e}")
            return []
    
    def search_semantic_scholar(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search Semantic Scholar for papers (requires API key for full access)"""
        logger.info(f"Searching Semantic Scholar for: {query}")
        
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        
        # Calculate date threshold
        date_threshold = datetime.now() - timedelta(days=self.config['days_back'])
        year_threshold = date_threshold.year
        
        params = {
            'query': query,
            'limit': max_results,
            'fields': 'paperId,title,authors,abstract,year,publicationDate,url',
            'year': f'{year_threshold}-'
        }
        
        headers = {
            'User-Agent': 'Academic Paper Fetcher (your-email@example.com)'
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for paper in data.get('data', []):
                # Check if paper is recent enough
                pub_date_str = paper.get('publicationDate')
                if pub_date_str:
                    try:
                        pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d')
                        if pub_date < date_threshold:
                            continue
                    except ValueError:
                        continue
                
                authors = [author.get('name', '') for author in paper.get('authors', [])]
                
                papers.append({
                    'id': paper.get('paperId', ''),
                    'title': paper.get('title', ''),
                    'authors': authors,
                    'summary': paper.get('abstract', ''),
                    'published': pub_date_str or '',
                    'url': paper.get('url', ''),
                    'source': 'Semantic Scholar'
                })
            
            logger.info(f"Found {len(papers)} recent papers from Semantic Scholar")
            return papers
            
        except requests.RequestException as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Semantic Scholar response: {e}")
            return []
    
    def fetch_papers(self) -> List[Dict]:
        """Fetch papers from all configured sources"""
        logger.info("Starting paper fetch process...")
        all_papers = []
        
        for search_term in self.config['search_terms']:
            # Search arXiv
            arxiv_papers = self.search_arxiv(search_term, self.config['max_results'])
            all_papers.extend(arxiv_papers)
            
            # Add delay to be respectful to APIs
            time.sleep(1)
            
            # Search Semantic Scholar
            ss_papers = self.search_semantic_scholar(search_term, self.config['max_results'])
            all_papers.extend(ss_papers)
            
            time.sleep(1)
        
        # Remove duplicates based on title similarity
        unique_papers = self.remove_duplicates(all_papers)
        
        # Sort by publication date (newest first)
        unique_papers.sort(key=lambda x: x['published'], reverse=True)
        
        self.papers = unique_papers
        logger.info(f"Total unique papers found: {len(unique_papers)}")
        
        return unique_papers
    
    def remove_duplicates(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicate papers based on title similarity"""
        unique_papers = []
        seen_titles = set()
        
        for paper in papers:
            # Normalize title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', paper['title'].lower())
            normalized_title = ' '.join(normalized_title.split())
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_papers.append(paper)
        
        return unique_papers
    
    def format_papers_html(self) -> str:
        """Format papers as HTML for email"""
        if not self.papers:
            return "<p>No recent papers found.</p>"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 30px; }}
                .paper {{ margin-bottom: 25px; padding: 15px; border-left: 3px solid #007acc; background-color: #f9f9f9; }}
                .title {{ font-weight: bold; font-size: 16px; color: #007acc; margin-bottom: 5px; }}
                .authors {{ color: #666; margin-bottom: 5px; }}
                .meta {{ color: #888; font-size: 12px; margin-bottom: 10px; }}
                .summary {{ line-height: 1.4; }}
                .url {{ margin-top: 10px; }}
                .url a {{ color: #007acc; text-decoration: none; }}
                .url a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Recent Papers: Generative AI Recommendation Systems</h1>
            <p>Found {len(self.papers)} papers from the last {self.config['days_back']} days</p>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        for i, paper in enumerate(self.papers, 1):
            authors_str = ', '.join(paper['authors'][:5])  # Limit to first 5 authors
            if len(paper['authors']) > 5:
                authors_str += ' et al.'
            
            summary = paper['summary'][:500] + '...' if len(paper['summary']) > 500 else paper['summary']
            
            html += f"""
            <div class="paper">
                <div class="title">{i}. {paper['title']}</div>
                <div class="authors">Authors: {authors_str}</div>
                <div class="meta">Published: {paper['published']} | Source: {paper['source']}</div>
                <div class="summary">{summary}</div>
                <div class="url"><a href="{paper['url']}" target="_blank">Read Paper</a></div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def format_papers_text(self) -> str:
        """Format papers as plain text for email"""
        if not self.papers:
            return "No recent papers found."
        
        text = f"""Recent Papers: Generative AI Recommendation Systems
Found {len(self.papers)} papers from the last {self.config['days_back']} days
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        for i, paper in enumerate(self.papers, 1):
            authors_str = ', '.join(paper['authors'][:5])
            if len(paper['authors']) > 5:
                authors_str += ' et al.'
            
            summary = paper['summary'][:500] + '...' if len(paper['summary']) > 500 else paper['summary']
            
            text += f"""{i}. {paper['title']}
Authors: {authors_str}
Published: {paper['published']} | Source: {paper['source']}
Summary: {summary}
URL: {paper['url']}

{'='*80}

"""
        
        return text
    
    def start_local_smtp_server(self):
        """Start local SMTP server if configured"""
        email_config = self.config['email']
        if email_config.get('use_local_server', False):
            if not hasattr(self, 'smtp_server_manager'):
                host = email_config.get('local_server_host', 'localhost')
                port = email_config.get('local_server_port', 1025)
                self.smtp_server_manager = SMTPServerManager(host, port)
                
            if not self.smtp_server_manager.is_running():
                logger.info("Starting local SMTP server...")
                print("Starting local SMTP server...")
                success = self.smtp_server_manager.start()
                print("Starting local SMTP server...----------")
                if success:
                    logger.info(f"Local SMTP server started on {host}:{port}")
                    print(f"📧 Local email server started on {host}:{port}")
                    print(f"Emails will be saved to: emails/ directory")
                    return True
                else:
                    logger.error("Failed to start local SMTP server")
                    return False
            return True
        return True
    
    def send_email(self, recipient_email: str = None) -> bool:
        """Send the paper list via email"""
        email_config = self.config['email']
        recipient = recipient_email or email_config['recipient_email']
        
        # Start local server if needed
        if email_config.get('use_local_server', False):
            if not self.start_local_smtp_server():
                return False
        
        if not email_config['sender_email'] or not recipient:
            logger.error("Email configuration incomplete")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Recent Papers: Generative AI Recommendation Systems ({datetime.now().strftime('%Y-%m-%d')})"
            msg['From'] = email_config['sender_email']
            msg['To'] = recipient
            
            # Create both plain text and HTML versions
            text_content = self.format_papers_text()
            html_content = self.format_papers_html()
            
            # Attach parts
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                # Only use TLS for external servers
                if email_config.get('use_tls', True) and not email_config.get('use_local_server', False):
                    server.starttls()
                
                # Only login if password is provided
                if email_config['sender_password']:
                    server.login(email_config['sender_email'], email_config['sender_password'])
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient}")
            if email_config.get('use_local_server', False):
                print(f"📧 Email sent to local server! Check the emails/ directory for the saved email.")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def save_to_file(self, filename: str = None) -> str:
        """Save papers to a file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"generative_ai_papers_{timestamp}.html"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.format_papers_html())
            
            logger.info(f"Papers saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
            return ""

def main():
    parser = argparse.ArgumentParser(description='Fetch recent papers on Generative AI Recommendation Systems')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--email', '-e', help='Recipient email address')
    parser.add_argument('--save-only', '-s', action='store_true', help='Save to file only, do not send email')
    parser.add_argument('--output', '-o', help='Output filename')
    
    args = parser.parse_args()
    
    # Initialize fetcher
    fetcher = PaperFetcher(args.config)
    
    # Fetch papers
    papers = fetcher.fetch_papers()
    
    if not papers:
        logger.warning("No papers found")
        return
    
    # Save to file
    if args.save_only or args.output:
        filename = fetcher.save_to_file(args.output)
        print(f"Papers saved to: {filename}")
    else:
        # Send email
        success = fetcher.send_email(args.email)
        if success:
            print("Email sent successfully!")
        else:
            print("Failed to send email. Check configuration and try again.")
            # Save to file as backup
            filename = fetcher.save_to_file()
            print(f"Papers saved to backup file: {filename}")

if __name__ == "__main__":
    main()
