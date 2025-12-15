import os

def count_characters(directory):
    total_files = 0
    total_characters = 0
    
    # 定义支持的文件类型
    supported_extensions = {'.py', '.js', '.html', '.css', '.ts', '.tsx', '.jsx'}
    
    # 忽略的目录和文件
    ignore_dirs = ['.git', '__pycache__', 'venv', '.env', 'node_modules', '.vscode']
    ignore_files = ['count_chars.py']  # 忽略统计脚本本身
    
    for root, dirs, files in os.walk(directory):
        # 过滤掉要忽略的目录
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file in ignore_files:
                continue
                
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            # 只统计支持的文件类型
            if ext not in supported_extensions:
                continue
                
            total_files += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_characters += len(content)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return {
        'total_files': total_files,
        'total_characters': total_characters
    }

if __name__ == "__main__":
    directory = '.'
    stats = count_characters(directory)
    
    print("项目字符统计结果：")
    print(f"总文件数：{stats['total_files']}")
    print(f"总字符数：{stats['total_characters']}")
