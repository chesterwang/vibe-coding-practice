import os
import sys
import subprocess
from pathlib import Path

def get_markdown_files(path):
    """
    递归获取目录中所有的markdown文件，并按照目录结构和文件名的字母顺序排序。
    """
    md_files = []
    for root, dirs, files in os.walk(path):
        dirs.sort()
        files.sort()
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def convert_to_epub(directory):
    """
    将指定目录中的所有 Markdown 文件转换为一个 EPUB 文件。
    """
    directory_path = Path(directory)
    if not directory_path.is_dir():
        print(f"错误: '{directory}' 不是一个有效的目录。")
        sys.exit(1)

    md_files = get_markdown_files(directory_path)
    if not md_files:
        print(f"在目录 '{directory}' 中没有找到任何 Markdown 文件。")
        sys.exit(1)

    output_epub_name = f"{directory_path.name}.epub"
    output_epub_path = directory_path.parent / output_epub_name

    try:
        # Pandoc 命令行参数
        # --toc: 根据标题自动生成目录
        # --from markdown: 指定输入格式
        # --embed-resources: 确保图片和媒体文件被嵌入到 EPUB 中
        # -o: 指定输出文件路径
        pandoc_command = [
            'pandoc',
            '--toc',
            '--from', 'markdown',
            '--embed-resources',
            '-o', str(output_epub_path)
        ]

        # 将所有 markdown 文件作为输入参数
        pandoc_command.extend(md_files)

        # 运行 pandoc 命令
        subprocess.run(pandoc_command, check=True, capture_output=True, text=True)

        print(f"成功将 '{directory}' 转换为 EPUB 文件：'{output_epub_path}'")

    except FileNotFoundError:
        print("错误: 'pandoc' 命令没有找到。请确保你已经安装了 pandoc 并将其添加到了系统路径中。")
    except subprocess.CalledProcessError as e:
        print(f"转换过程中发生错误: {e.stderr}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python create_epub.py <目录路径>")
        sys.exit(1)

    input_directory = sys.argv[1]
    convert_to_epub(input_directory)