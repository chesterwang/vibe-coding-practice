import argparse
import os
import markdown
import ebooklib
from ebooklib import epub
from lxml import etree


def merge_markdown_files(root_dir):
    """
    Merges all markdown files in a directory and its subdirectories into a single markdown string.

    Args:
        root_dir (str): The root directory to search for markdown files.

    Returns:
        str: The merged markdown content.
    """
    if not os.path.isdir(root_dir):
        raise FileNotFoundError(f"Error: Directory not found at '{root_dir}'")

    merged_content = ""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Sort files to ensure consistent order
        filenames.sort()
        for filename in filenames:
            if filename.endswith(".md"):
                file_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(file_path, root_dir)
                # Add a heading based on the directory structure
                level = relative_path.count(os.sep) + 2  # Start with H2
                header = "#" * level
                merged_content += f"\n\n{header} {relative_path}\n\n"
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        merged_content += f.read()
                except Exception as e:
                    print(f"Warning: Could not read file {file_path}. Skipping. Error: {e}")
    return merged_content


def convert_md_to_epub(md_content, output_file_path):
    """
    Converts markdown content to an EPUB file.

    Args:
        md_content (str): The markdown content to convert.
        output_file_path (str): The path for the output EPUB file.
    """
    try:
        # Create a new EPUB book
        book = epub.EpubBook()
        book.set_identifier("id123456")
        book.set_title(os.path.basename(output_file_path).replace(".epub", ""))
        book.set_language("zh")

        # Create EPUB chapter from markdown
        # Convert markdown to HTML
        html_content = markdown.markdown(md_content, extensions=['extra', 'toc'])

        # Create an EPUB chapter
        c = epub.EpubHtml(title="Content", file_name="content.xhtml", lang="zh")
        c.content = html_content

        # Add chapter to the book
        book.add_item(c)

        # Create spine and table of contents
        book.toc = (epub.Link("content.xhtml", "Content", "content"),)
        book.spine = ["nav", c]

        # Add default NCX and Nav files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Write the EPUB file
        epub.write_epub(output_file_path, book, {})
        print(f"Successfully created EPUB file at: {output_file_path}")

    except Exception as e:
        print(f"Error: Failed to convert Markdown to EPUB. Error: {e}")


def main():
    """
    Main function to parse command-line arguments and run the conversion process.
    """
    parser = argparse.ArgumentParser(
        description="Merges markdown files and converts them into an EPUB book."
    )
    parser.add_argument(
        "directory",
        type=str,
        help="The root directory containing markdown files to process."
    )
    args = parser.parse_args()

    # Get the directory name from the argument
    dir_path = args.directory.rstrip(os.sep)
    base_name = os.path.basename(dir_path)

    if not base_name:
        print("Error: Invalid directory path.")
        return

    # 1. Merge markdown files
    output_md_path = f"{base_name}.md"
    try:
        merged_md_content = merge_markdown_files(dir_path)
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(merged_md_content)
        print(f"Successfully created merged markdown file at: {output_md_path}")
    except FileNotFoundError as e:
        print(e)
        return

    # 2. Convert to EPUB
    output_epub_path = f"{base_name}.epub"
    convert_md_to_epub(merged_md_content, output_epub_path)


if __name__ == "__main__":
    main()
