import subprocess
import os
import requests
import sys
import shutil

def valid_github_url(repo_url):
    """Checking if the given GitHub repository URL is valid."""
    try:
        api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/")
        response = requests.get(api_url)
        if response.status_code == 200:
            print(f"GitHub URL: {repo_url} is valid")
            return True
        else:
            print(f"Invalid URL: {repo_url}")
            return False
    except requests.RequestException as e:
        print(f"The error occurred in checking the URL: {e}")
        return False

def extract_files(status_prefix):
    """Extract the list of files based on the Git Status prefix"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"],
                                capture_output=True, text=True, check=True)
        files = [line[3:] for line in result.stdout.splitlines()
                 if line.startswith(status_prefix)]
        return files
    except subprocess.CalledProcessError as e:
        print(f"The error obtained executing the git command: {e}")
        return []

def write_to_file(file_list, label, output_dir):
    """Writes contents of each file into a .txt file with same name (no folder structure)."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    index_file_path = os.path.join(output_dir, f"{label.replace(' ', '_').lower()}_index.txt")

    # Write index and file contents
    with open(index_file_path, "w", encoding="utf-8") as index_file:
        index_file.write(f"{label} Files:\n")
        index_file.write("-" * 50 + "\n")

        for file_path in file_list:
            try:
                file_name = os.path.basename(file_path)
                base, _ = os.path.splitext(file_name)
                destination_path = os.path.join(output_dir, base + ".txt")

                with open(file_path, "r", encoding="utf-8", errors="ignore") as src_file:
                    content = src_file.read()

                with open(destination_path, "w", encoding="utf-8") as dest_file:
                    dest_file.write(content)

                index_file.write(f"{file_path} -> {base + '.txt'}\n")

            except Exception as e:
                error_msg = f" Error processing {file_path}: {e}"
                print(error_msg)
                index_file.write(error_msg + "\n")
    try:
        to_delete_1 = os.path.join(output_dir, "modified_files_index.txt")
        to_delete_2 = os.path.join(output_dir, "untracked_index.txt")

        for f in [to_delete_1, to_delete_2]:
            if os.path.exists(f):
                os.remove(f)
                # print(f"Deleted: {f}")
    except Exception as e:
        print(f"Error deleting one of the index files: {e}")

def extract_readme_file(repo_path,output_dir):
    """Extracts the ReadMe file from the repo and saves it in README_output.txt"""

    possible_names=["README.md","README.MD","readme.md","Readme.md","README.txt","readme.txt"]
    for name in possible_names:
        readme_path=os.path.join(repo_path,name)
        if os.path.isfile(readme_path):
            try:
                with open(readme_path,"r",encoding="utf-8",errors="ignore") as f:
                    content=f.read()
                output_path=os.path.join(output_dir,"ReadME.txt")
                with open(output_path,"w",encoding="utf-8") as op_file:
                    op_file.write(content)
                print(f"ReadMe file is successfully written to the file : {output_path}")
            except Exception as e:
                print(f"Error in reading README file : {e}")
            return
    print("README file not found in the repository.")

def extract_commit_messages(repo_url, op_file):
    """Fetches the latest commit messages from the GitHub repository."""

    try:
        api_url_for_commits = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/commits"
        response = requests.get(api_url_for_commits)

        if response.status_code == 200:
            commits = response.json()

            if not commits:
                print("\nNo commits found.")
                return  

            with open(op_file, "w") as output:  # <-- changed to overwrite
                output.write("Commit Messages:\n")
                output.write("-" * 50 + "\n")

                for commit in commits[:5]:
                    message = commit["commit"]["message"]
                    output.write(f"Message: {message}\n")
                    output.write("-" * 50 + "\n")

                print("\nCommit messages extracted successfully.")
        else:
            print(f"Failed to fetch commits. HTTP Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching commit messages: {e}")

if(len(sys.argv)!=4):
    print("Not sufficient arguments")
    sys.exit(1)

# repo_url = input("Enter the GitHub repository URL: ")

repo_url=sys.argv[1]
next_path = sys.argv[3]

if valid_github_url(repo_url):
    # repo_path = input("Enter the path to the cloned repository: ")
    repo_path=sys.argv[2]

    if os.path.isdir(repo_path):
        original_cwd = os.getcwd()
        print(f"The original directory is:{original_cwd}")  # debugging statement
        os.chdir(repo_path)

        output_file = os.path.join(original_cwd, "git_files.txt")
        output_dir = os.path.abspath(os.path.join(original_cwd, "Data_Extraction_Files"))
        print(f"Output directory is: {output_dir}")  # debugging statement
        output_commit_file = os.path.join(output_dir, "Commit_messages.txt")

        # Ensure the file is cleared before writing
        # open(output_file, "w").close()
        # open(output_commit_file, "w").close()

        modified_files = extract_files(" M")
        untracked_files = extract_files("??")

        if os.path.exists(output_dir):
            for file_name in os.listdir(output_dir):
                file_path=os.path.join(output_dir,file_name)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # delete the file
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # remove the subdirectory if anything is present

                except Exception as e:
                    print(f"Not able to delete the {file_path} because of the reason:{e}")

        write_to_file(modified_files, "Modified Files", output_dir)
        write_to_file(untracked_files, "Untracked", output_dir)

        extract_commit_messages(repo_url,output_commit_file)

        extract_readme_file(repo_path,output_dir)

        print(f"\n Output written to {output_file}")

        #os.chdir(original_cwd)
        #print(f"The original directory is:{original_cwd}")  # debugging statement

        llm_script=os.path.join(next_path,"code_documentation_generation_1.py")
        if os.path.exists(llm_script):
            print(f"Executing llm script:{llm_script}")
            subprocess.run([sys.executable,llm_script,repo_path,"client",next_path])
        else:
            print(f"LLM script not found:{llm_script}")

    else:
        print(f" The specified path does not exist or is not a directory: {repo_path}")

else:
    print(" No extraction performed due to invalid URL")