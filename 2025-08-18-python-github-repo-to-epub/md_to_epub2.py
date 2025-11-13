import os
import re
import subprocess
import sys
from pathlib import Path

def get_markdown_files(path):
    """
    递归获取目录中所有的markdown文件，并按照目录结构和文件名的字母顺序排序
    """
    md_files = []
    # 按照目录结构遍历
    for root, dirs, files in os.walk(path):
        # 按照文件夹名排序
        dirs.sort()
        # 按照文件名排序
        files.sort()
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def convert_html_img_to_md(content):
    """
    将内容中的<img>标签转换为标准的markdown图片引用格式。
    """
    # 匹配 <img src="..." alt="..." /> 或 <img src="..." />
    img_pattern = re.compile(r'<img\s+src="([^"]+)"(?:\s+alt="([^"]*)")?\s*.*/*>')
    # 替换函数
    def replacer(match):
        src = match.group(1)
        alt = match.group(2) if match.group(2) else ""
        return f"![{alt}]({src})"
    return img_pattern.sub(replacer, content)

def merge_markdown_files(directory):
    """
    合并目录下的所有markdown文件为一个大文件，并处理图片引用。
    """
    merged_content = []
    md_files = get_markdown_files(directory)
    if not md_files:
        print(f"在目录 '{directory}' 中没有找到任何markdown文件。")
        return None

    # 获取目录的基名，作为最终文件的名称
    dir_name = Path(directory).name
    output_md_path = Path(directory).parent / f"{dir_name}.md"

    # 根据目录深度为每个文件添加标题，以创建层级结构
    base_level = 1
    for md_file in md_files:
        # 获得相对路径
        relative_path = Path(md_file).relative_to(directory)
        parts = relative_path.parts
        # 根据目录深度确定标题级别
        level = base_level + len(parts) - 1
        title = Path(parts[-1]).stem.replace('-', ' ').title() # 使用文件名作为标题

        # 读取文件内容并处理
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 转换图片引用
            processed_content = convert_html_img_to_md(content)
            # 添加文件标题和内容
            merged_content.append(f"{'#' * level} {title}\n\n{processed_content}\n\n")

    # 写入合并后的markdown文件
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.writelines(merged_content)

    return output_md_path

def convert_md_to_epub(md_file_path):
    """
    将大markdown文件转换为epub文件，使用pandoc。
    """
    # 构造输出epub文件的路径
    output_epub_path = md_file_path.with_suffix('.epub')

    try:
        # 使用subprocess调用pandoc命令
        # --toc: 自动生成目录
        # -o: 指定输出文件
        # -f markdown: 指定输入格式为markdown
        # --metadata title="..." --metadata author="...": 可以自定义元数据
        subprocess.run(
            ['pandoc', str(md_file_path), '-o', str(output_epub_path), '--toc', '--from', 'markdown'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"成功将 '{md_file_path}' 转换为 EPUB 文件: '{output_epub_path}'")
    except FileNotFoundError:
        print("错误: 'pandoc' 命令没有找到。请确保你已经安装了 pandoc 并将其添加到了系统路径中。")
        print("你可以从 https://pandoc.org/installing.html 下载安装。")
    except subprocess.CalledProcessError as e:
        print(f"在转换过程中发生错误: {e.stderr}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python convert_to_epub.py <目录路径>")
        sys.exit(1)

    input_directory = sys.argv[1]
    # 检查路径是否存在
    if not os.path.isdir(input_directory):
        print(f"错误: 提供的路径 '{input_directory}' 不是一个有效的目录。")
        sys.exit(1)

    print(f"正在合并目录 '{input_directory}' 中的Markdown文件...")
    merged_md_file = merge_markdown_files(input_directory)

    if merged_md_file:
        print(f"成功合并所有Markdown文件到 '{merged_md_file}'。")
        print("正在将合并后的Markdown文件转换为EPUB...")
        convert_md_to_epub(merged_md_file)
    else:
        sys.exit(1)