import os

def generate_tree(dir_path, prefix="", ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.next', 'dist', 'build'}
    
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return ""

    entries = [e for e in entries if e not in ignore_dirs]
    
    tree_str = ""
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        
        tree_str += f"{prefix}{connector}{entry}\n"
        
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree_str += generate_tree(path, new_prefix, ignore_dirs)
            
    return tree_str

def main():
    project_root = "."
    project_name = os.path.basename(os.path.abspath(project_root))
    
    tree_content = f"# Project Tree: {project_name}\n\n```text\n{project_name}/\n"
    tree_content += generate_tree(project_root)
    tree_content += "```\n"
    
    output_file = "project_tree.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tree_content)
        
    print(f"Project tree has been generated and saved to '{output_file}'")

if __name__ == "__main__":
    main()
