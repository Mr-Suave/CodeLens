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

MAX_PROMPT_LENGTH = 25000  # Conservative safe limit to avoid prompt size errors

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
        # Get the diff for the modified file from the last commit
        diff = subprocess.check_output(['git', 'diff', '--', file_path], universal_newlines=True)
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

def main():
    files = get_git_modified_and_untracked_files()
    if not files:
        print("No modified or untracked files found.")
        return

    print("Scanning modified files...\n")

    total_diff = ""
    fallback_comments = []

    for file in files:
        diff = get_git_diff(file)
        if diff:  # Proceed only if diff content is available
            total_diff += f"\n\n# FILE: {file}\n{diff}"

            pattern = COMMENT_PATTERNS.get(os.path.splitext(file)[1])
            if pattern:
                content = read_file(file)
                fallback_comments.extend(extract_comments(content, pattern))

    if len(total_diff) <= MAX_PROMPT_LENGTH:
        print("✅ Using diff content for commit generation.")
        prompt = f"""
You are an AI assistant. Based on the following git diffs of recently modified source code files,
generate a short and meaningful Git commit message summarizing the purpose of the changes.

Only return the commit message.

---
{total_diff}
---
"""
        commit_message = generate_commit_message_from_prompt(prompt)
    elif fallback_comments:
        print("Prompt too long. Falling back to comments.")
        prompt = f"""
You are an AI assistant. Based on the following comments extracted from recently modified source code files,
generate a short and meaningful Git commit message that summarizes the purpose of the changes.

Only return the commit message.

---
{chr(10).join(fallback_comments)}
---
"""
        commit_message = generate_commit_message_from_prompt(prompt)
    else:
        print("No valid content or comments found. Defaulting.")
        commit_message = "Update project files."

    print("\nSuggested Commit Message:\n")
    print(f"\"{commit_message}\"\n")

if __name__ == "__main__":
    if "--generate-only" in sys.argv:
        files = get_git_modified_and_untracked_files()
        total_diff = ""
        fallback_comments = []

        for file in files:
            diff = get_git_diff(file)
            if diff:  # Proceed only if diff content is available
                total_diff += f"\n\n# FILE: {file}\n{diff}"

                pattern = COMMENT_PATTERNS.get(os.path.splitext(file)[1])
                if pattern:
                    content = read_file(file)
                    fallback_comments.extend(extract_comments(content, pattern))

        if len(total_diff) <= MAX_PROMPT_LENGTH:
            prompt = f"""
You are an AI assistant. Based on the following git diffs of recently modified source code files,
generate a short and meaningful Git commit message summarizing the purpose of the changes.

Only return the commit message.

---
{total_diff}
---
"""
            print(generate_commit_message_from_prompt(prompt))
        elif fallback_comments:
            prompt = f"""
You are an AI assistant. Based on the following comments extracted from recently modified source code files,
generate a short and meaningful Git commit message that summarizes the purpose of the changes.

Only return the commit message.

---
{chr(10).join(fallback_comments)}
---
"""
            print(generate_commit_message_from_prompt(prompt))
        else:
            print("Update project files.")
    else:
        main()
