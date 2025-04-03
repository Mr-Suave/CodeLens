import subprocess
import os
import requests
import sys

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

def write_to_file(file_list, label, op_file):
    """Write all the contents of the modified and untracked files into a text file"""
    
    # Overwrite the file for the first section, then append for the rest
    mode = "w" if label == "Modified Files" else "a"
    
    with open(op_file, mode) as output:
        output.write(f"\n {label} Files:\n")
        for file in file_list:
            output.write(f"File: {file}\n")
            try:
                with open(file, "r") as f:
                    output.write(f.read())
            except Exception as e:
                output.write(f"Error reading {file}: {e}\n")
            output.write("-" * 50 + "\n")

def extract_commit_messages(repo_url, op_file):
    """Fetches the latest commit messages from the GitHub repository."""

    try:
        api_url_for_commits = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/commits"
        response = requests.get(api_url_for_commits)

        if response.status_code == 200:
            commits = response.json()

            if not commits:  # Check if the list is empty
                print("\nNo commits found.")
                return  

            with open(op_file, "a") as output:
                output.write("\nCommit Messages:\n")  # Fixed newline issue

                for commit in commits[:5]:  # Get the latest 5 commits
                    message = commit["commit"]["message"]
                    author = commit["commit"]["author"]["name"]
                    date = commit["commit"]["author"]["date"]

                    output.write(f"Author: {author}\n")
                    output.write(f"Date: {date}\n")
                    output.write(f"Message: {message}\n")
                    output.write("-" * 50 + "\n")

                print("\nCommit messages extracted successfully.")
        else:
            print(f"Failed to fetch commits. HTTP Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching commit messages: {e}")

if(len(sys.argv)!=3):
    print("Not sufficient arguments")
    sys.exit(1)

# repo_url = input("Enter the GitHub repository URL: ")

repo_url=sys.argv[1]

if valid_github_url(repo_url):
    # repo_path = input("Enter the path to the cloned repository: ")
    repo_path=sys.argv[2]

    if os.path.isdir(repo_path):
        original_cwd = os.getcwd()

        os.chdir(repo_path)
        print(f"Changed directory to: {repo_path}")

        output_file = os.path.join(original_cwd, "git_files.txt")
        output_commit_file = os.path.join(original_cwd, "git_commit_files.txt")
        
        # Ensure the file is cleared before writing
        open(output_file, "w").close()
        open(output_commit_file, "w").close()

        modified_files = extract_files(" M")
        untracked_files = extract_files("??")

        write_to_file(modified_files, "Modified Files", output_file)
        write_to_file(untracked_files, "Untracked", output_file)

        extract_commit_messages(repo_url,output_commit_file)

        print(f"\n Output written to {output_file}")

        os.chdir(original_cwd)

    else:
        print(f" The specified path does not exist or is not a directory: {repo_path}")

else:
    print(" No extraction performed due to invalid URL")
