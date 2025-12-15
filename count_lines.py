import os
import re

def count_lines(directory):
    total_files = 0
    total_lines = 0
    total_comment_lines = 0
    total_blank_lines = 0
    
    # 定义支持的文件类型及其注释格式
    comment_patterns = {
        '.py': r'^\s*#',  # Python 单行注释
        '.js': r'^\s*//',  # JavaScript 单行注释
        '.html': r'^\s*<!--',  # HTML 注释开始
        '.css': r'^\s*/\*|^\s*//',  # CSS 注释
        '.ts': r'^\s*//',  # TypeScript 单行注释
        '.tsx': r'^\s*//',  # TypeScript JSX 单行注释
        '.jsx': r'^\s*//',  # JavaScript JSX 单行注释
    }
    
    # 忽略的目录和文件
    ignore_dirs = ['.git', '__pycache__', 'venv', '.env', 'node_modules', '.vscode']
    ignore_files = ['count_lines.py']  # 忽略统计脚本本身
    
    for root, dirs, files in os.walk(directory):
        # 过滤掉要忽略的目录
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file in ignore_files:
                continue
                
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            # 只统计支持的文件类型
            if ext not in comment_patterns:
                continue
                
            total_files += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    stripped_line = line.strip()
                    
                    if not stripped_line:
                        total_blank_lines += 1
                    elif re.match(comment_patterns[ext], line):
                        total_comment_lines += 1
                    else:
                        total_lines += 1
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return {
        'total_files': total_files,
        'total_lines': total_lines,
        'total_comment_lines': total_comment_lines,
        'total_blank_lines': total_blank_lines
    }

if __name__ == "__main__":
    directory = '.'
    stats = count_lines(directory)
    
    print("项目代码统计结果：")
    print(f"总文件数：{stats['total_files']}")
    print(f"总代码行数：{stats['total_lines']}")
    print(f"注释行数：{stats['total_comment_lines']}")
    print(f"空白行数：{stats['total_blank_lines']}")
    print(f"物理总行数：{stats['total_lines'] + stats['total_comment_lines'] + stats['total_blank_lines']}")
