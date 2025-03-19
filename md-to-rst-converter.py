import os
import glob

def convert_md_to_rst(md_content):
    lines = md_content.split('\n')
    rst_content = []
    for line in lines:
        if line.startswith('Title:'):
            rst_content.append(line.replace('Title:', ":title:"))
        elif line.startswith('Category:'):
            rst_content.append(line.replace('Category:', ":category:"))
        elif line.startswith('Author:'):
            rst_content.append(line.replace('Author:', ":author:"))
        elif line.startswith('Summary:'):
            rst_content.append(line.replace('Summary:', ":summary:"))
        elif line.startswith('Date:'):
            rst_content.append(line.replace('Date:', ":date:"))
        elif line.startswith('Tags:'):
            rst_content.append(line.replace('Tags:', ":tags:"))
        elif line.startswith('Category:'):      
            rst_content.append(line.replace('Category:', ":category:"))
        elif line.startswith('image:'):
            rst_content.append(line.replace('{filename}..\\', '{filename}../'))
        elif line.startswith('!['):
            alt_text = line.split('[')[1].split(']')[0]
            image_path = line.split('(')[1].split(')')[0]
            rst_content.append(f'.. image:: {image_path}')
            rst_content.append(f'   :alt: {alt_text}')
            rst_content.append('   :class: img-responsive')
        elif line.startswith('# '):
            rst_content.append(line[2:])
            rst_content.append('=' * len(line[2:]))
        elif line.startswith('## '):
            rst_content.append(line[3:])
            rst_content.append('-' * len(line[3:]))
        elif line.startswith('### '):
            rst_content.append(line[4:])
            rst_content.append('~' * len(line[4:]))
        elif line.startswith('#### '):
            rst_content.append(line[5:])
            rst_content.append('^' * len(line[5:]))
        elif line.startswith('##### '):
            rst_content.append(line[6:])
            rst_content.append('"' * len(line[6:]))
        else:
            rst_content.append(line)
    return '\n'.join(rst_content)

def convert_all_md_to_rst(blog_folder):
    md_files = glob.glob(os.path.join(blog_folder, '*.md'))
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        rst_content = convert_md_to_rst(md_content)
        rst_file = md_file.replace('.md', '.rst')
        with open(rst_file, 'w', encoding='utf-8') as f:
            f.write(rst_content)
        print(f'Converted {md_file} to {rst_file}')

blog_folder = 'e:\\GitHub\\pelican-blog-2025\\content\\blog'
convert_all_md_to_rst(blog_folder)