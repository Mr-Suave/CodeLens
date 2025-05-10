import subprocess
import os
import re
import google.generativeai as genai
import sys

# Supported file extensions and corresponding comment patterns
COMMENT_PATTERNS = {
    '.py': r'#.*',
    '.js': r'//.*|/\*[\s\S]*?\*/',
    '.cpp': r'//.*|/\*[\s\S]*?\*/',
    '.java': r'//.*|/\*[\s\S]*?\*/',
    '.ts': r'//.*|/\*[\s\S]*?\*/',
    '.html': r'<!--[\s\S]*?-->',
    '.css': r'/\*[\s\S]*?\*/',
}

# Set Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyDl8h1PkdfpzzFsZg5IkkeGe7QF5bYuvMI"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-pro-002")

MAX_PROMPT_LENGTH = 25000  # Safe limit for prompt size

def get_git_modified_and_untracked_files():
    try:
        output = subprocess.check_output(['git', 'status', '--porcelain'], universal_newlines=True)
        files = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            status, file_path = line.split(" ", 1)
            if status.strip() in {'M', 'A', '??'}:
                files.append(file_path)
        return files
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
        return []

def get_git_diff(file_path):
    try:
        diff = subprocess.check_output(['git', 'diff', '--', file_path], encoding='utf-8', errors='ignore')
        return diff
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff for {file_path}: {e}")
        return ""

def read_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return ""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def extract_comments(content, pattern):
    return re.findall(pattern, content)

def generate_commit_message_from_prompt(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating commit message: {e}")
        return "Update project files."

def build_prompt_data():
    files = get_git_modified_and_untracked_files()
    full_contents = []
    diffs = []
    fallback_comments = []

    for file in files:
        ext = os.path.splitext(file)[1]
        file_content = read_file(file)
        if file_content:
            full_contents.append(f"\n\n# FILE CONTENT: {file}\n{file_content}")
            pattern = COMMENT_PATTERNS.get(ext)
            if pattern:
                fallback_comments.extend(extract_comments(file_content, pattern))

        file_diff = get_git_diff(file)
        if file_diff:
            diffs.append(f"\n\n# DIFF: {file}\n{file_diff}")

    return full_contents, diffs, fallback_comments

def generate_commit_message(full_contents, diffs, fallback_comments):
    full_prompt = "\n".join(full_contents + diffs)

    if len(full_prompt) <= MAX_PROMPT_LENGTH:
        # print("Using full content + diffs for commit generation.")
        prompt = f"""
You are an AI assistant. Based on the following contents and diffs of recently modified and untracked files,
generate a short and meaningful Git commit message summarizing the purpose of the changes.
Only return the commit message. Don't include any acknowledgement in the commit message as this would directly go to the github repo. So generate only a commit message. You can think of as you are writing a commit message when you are committing in a git hub repo.
You will be given the difference between the files that are changed in the git hub from last commit to this commit. You will also be given the files that are untracked and modified files that are newly going to the repo.
Final word generate responsibly.

Only return the commit message.

---
{full_prompt}
---
"""
        return generate_commit_message_from_prompt(prompt)
    elif fallback_comments:
        print(" Prompt too long. Falling back to extracted comments.")
        prompt = f"""
You are an AI assistant. Based on the following comments extracted from recently modified or untracked source code files,
generate a short and meaningful Git commit message that summarizes the purpose of the changes.

---
{chr(10).join(fallback_comments)}
---
"""
        return generate_commit_message_from_prompt(prompt)
    else:
        print(" No valid data found. Using default commit message.")
        return "Update project files."

def main():
    full_contents, diffs, fallback_comments = build_prompt_data()
    if not full_contents and not diffs:
        print("No modified or untracked files found.")
        return

    commit_message = generate_commit_message(full_contents, diffs, fallback_comments)

    print("\nSuggested Commit Message:\n")
    print(f"\"{commit_message}\"\n")

if __name__ == "__main__":
    if "--generate-only" in sys.argv:
        full_contents, diffs, fallback_comments = build_prompt_data()
        print(generate_commit_message(full_contents, diffs, fallback_comments))
    else:
        main()
