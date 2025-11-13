#!/usr/bin/env python3
# file: markdown_to_epub.py

import os
import sys
import argparse
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup
import markdown
import re

def collect_markdown_files(directory):
    """收集目录中的所有Markdown文件"""
    md_files = []
    for root, dirs, files in sorted(list(os.walk(directory)),key=lambda x:x[0]):
        for file in files:
            if file.lower().endswith(('.md', '.markdown')):
                md_files.append(os.path.join(root, file))
                print(md_files[-1])
    # return sorted(md_files)
    return md_files

def convert_md_to_html(md_content, base_path):
    """将Markdown内容转换为HTML，并处理图片路径"""
    # 使用markdown库转换
    md = markdown.Markdown(extensions=['extra', 'toc'])
    html_content = md.convert(md_content)
    
    # 处理图片路径
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            # 处理相对路径
            if not src.startswith('http'):
                img_path = os.path.join(base_path, src)
                if os.path.exists(img_path):
                    # 在EPUB中使用相对路径
                    img['src'] = src
    
    return str(soup)

def extract_toc_from_html(html_content, filename):
    """从HTML内容中提取目录结构"""
    soup = BeautifulSoup(html_content, 'html.parser')
    toc_items = []
    
    # 查找所有标题标签
    for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
        level = int(heading.name[1])  # 从h1,h2等获取级别
        title = heading.get_text()
        anchor_id = heading.get('id') or f"{filename}_heading_{i}"
        heading['id'] = anchor_id
        toc_items.append({
            'level': level,
            'title': title,
            'id': anchor_id
        })
    tag = soup.find_all('h1')[0]
    html_title = tag.get_text()
    
    return html_title, toc_items, str(soup)

def create_epub_from_markdown(directory, output_file):
    """将目录中的Markdown文件转换为EPUB"""
    # 创建EPUB书籍
    book = epub.EpubBook()
    
    # 设置书籍元数据
    book.set_identifier(f'md_collection_{os.path.basename(directory)}')
    book.set_title(f'Markdown Collection - {os.path.basename(directory)}')
    book.set_language('zh')
    book.add_author('Markdown to EPUB Converter')
    
    # 收集所有Markdown文件
    md_files = collect_markdown_files(directory)
    
    if not md_files:
        print(f"在目录 {directory} 中未找到Markdown文件")
        return False
    
    # 存储章节和目录信息
    chapters = []
    full_toc = []
    
    # 处理每个Markdown文件
    for md_file_index,md_file_path in enumerate(md_files):
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 获取文件相对于根目录的路径
        relative_path = os.path.relpath(md_file_path, directory)
        file_dir = os.path.dirname(md_file_path)
        
        # 转换为HTML
        html_content = convert_md_to_html(md_content, file_dir)
        
        # 提取目录结构
        html_title, toc_items, updated_html = extract_toc_from_html(html_content, os.path.basename(md_file_path))
        print(html_title)

        # 创建章节
        chapter = epub.EpubHtml(
            title=html_title,
            file_name=f'{md_file_index}-{os.path.basename(md_file_path)}.xhtml',
            lang='zh'
        )
        chapter.content = updated_html
        
        # 添加章节到书籍
        book.add_item(chapter)
        chapters.append(chapter)
        
        # 更新全局目录
        for item in toc_items:
            full_toc.append((item['level'], item['title'], chapter, item['id']))
        
        # 处理图片资源
        soup = BeautifulSoup(html_content, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.startswith('http'):
                img_path = os.path.join(file_dir, src)
                if os.path.exists(img_path):
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = img_file.read()
                        
                        # 创建图片项
                        img_ext = os.path.splitext(src)[1][1:] or 'jpeg'
                        img_item = epub.EpubItem(
                            file_name=f'images/{os.path.basename(img_path)}',
                            media_type=f'image/{img_ext}',
                            content=img_data
                        )
                        book.add_item(img_item)
                    except Exception as e:
                        print(f"警告: 无法处理图片 {img_path}: {e}")
    
    # 添加默认样式
    style = '''
        body { font-family: Arial, sans-serif; }
        h1 { color: #333; }
        h2 { color: #666; }
        h3 { color: #999; }
        code { background-color: #f4f4f4; padding: 2px 4px; }
        pre { background-color: #f4f4f4; padding: 10px; overflow-x: auto; }
    '''
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    
    # 创建导航页面
    book.toc = [epub.Link(chapter.file_name, chapter.title, chapter.file_name) for chapter in chapters]
    
    # 添加基本导航
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 设置书籍结构
    book.spine = ['nav'] + chapters
    
    # 写入EPUB文件
    epub.write_epub(output_file, book)
    print(f"成功创建EPUB文件: {output_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description='将目录中的Markdown文件转换为EPUB电子书')
    parser.add_argument('directory', help='包含Markdown文件的目录路径')
    parser.add_argument('-o', '--output', help='输出EPUB文件路径')
    
    args = parser.parse_args()
    
    directory = args.directory
    
    # 检查目录是否存在
    if not os.path.isdir(directory):
        print(f"错误: 目录 {directory} 不存在")
        sys.exit(1)
    
    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        output_file = os.path.basename(os.path.abspath(directory)) + '.epub'
    
    # 创建EPUB
    try:
        create_epub_from_markdown(directory, output_file)
    except Exception as e:
        print(f"创建EPUB时出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
