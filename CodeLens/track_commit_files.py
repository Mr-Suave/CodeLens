import os
import sys
import subprocess
import shutil

def get_modified_files(commit_hash,repo_path):
    """Get the modified files in that specific file"""
    os.chdir(repo_path)
    result = subprocess.run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
                            capture_output=True, text=True)
    return result.stdout.strip().splitlines()

def get_untracked_files(repo_path):
    """Get untracked files"""
    os.chdir(repo_path)
    result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                            capture_output=True, text=True)
    return result.stdout.strip().splitlines()

def write_file_content(file_path,output_dir):
    base = os.path.basename(file_path)
    name,_ = os.path.splitext(base)

    try:
        with open(file_path,'r',encoding="utf-8",errors="ignore") as f:
            content = f.read()

        with open(os.path.join(output_dir, name + ".txt"), "w", encoding="utf-8") as f_out:
            f_out.write(content)
    except Exception as e:
        print(f"Error writing {file_path}: {e}")

def clear_output_folder(folder_path):
    """Delete contents of the folder if it exists"""
    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    else:
        os.makedirs(folder_path)


def main():
    if len(sys.argv) < 4:
        print("Usage: track_commit_files.py <commit_hash> <repo_path> <user_type>")
        sys.exit(1)

    commit_hash=sys.argv[1]
    repo_path = os.path.abspath(sys.argv[2])
    user_type = sys.argv[3]
    codelens_path= sys.argv[4]

    output_dir = os.path.join(repo_path,"Data_Extraction_Files")
    clear_output_folder(output_dir)

    modified_files = get_modified_files(commit_hash, repo_path)
    untracked_files = get_untracked_files(repo_path)

    for file in modified_files + untracked_files:
        full_path = os.path.join(repo_path, file)
        if os.path.isfile(full_path):
            write_file_content(full_path, output_dir)

    doc_script_path = os.path.join(codelens_path, "code_documentation_generation_api.py")
    subprocess.run(["py", doc_script_path, repo_path, user_type, codelens_path])


if __name__ == "__main__":
    main()