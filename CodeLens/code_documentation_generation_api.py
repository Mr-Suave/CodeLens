import os
import sys
import time
import google.generativeai as genai

# Set your Gemini API Key
GEMINI_API_KEY = "AIzaSyDl8h1PkdfpzzFsZg5IkkeGe7QF5bYuvMI"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-pro-002")

def query_model(prompt):
    """Send a request to Gemini API."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API call failed: {e}")
        return "Failed to generate documentation."

def read_file(file_path):
    """Read the content of a file and return it."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def generate_documentation(user_type, repo_path):
    data_extraction_dir = os.path.join(repo_path, "Data_Extraction_Files")
    doc_file_path = os.path.join(repo_path, f"Documentation_{user_type}.md")

    if not os.path.exists(data_extraction_dir):
        print(f"Error: Folder '{data_extraction_dir}' not found!")
        return

    commit_message = read_file(os.path.join(data_extraction_dir, "Commit_messages.txt")) or "No commit messages found."
    readme_content = read_file(os.path.join(data_extraction_dir, "ReadME.txt")) or "No README content found."
    existing_doc = read_file(doc_file_path) or "No existing documentation found."

    code_files_content = ""
    for file_name in os.listdir(data_extraction_dir):
        if file_name.endswith(".txt") and file_name not in ["Commit_messages.txt", "ReadME.txt"]:
            file_path = os.path.join(data_extraction_dir, file_name)
            code_files_content += f"\n\n## {file_name}\n\n{read_file(file_path) or ''}"

    prompt_details = {
        "client": "Just give the basic overview of the contents in the files. Try to explain more functionality, uses and features that are developed, but don't use technical terms.",
        "novice": "Give some nice explanation of the code in files, like what the code is trying to do and also dependencies with the other code files you will be given. Don't make it too long. Don't include the entire code – just explain the critical parts of the code. You are allowed to use the technical terms that a novice developer is expected to know and understand like framework etc.",
        "senior": "Give the dependencies, structure of the code and the architecture based on the code files given to you, don't display the code – just say what the code does. Also include the details of the frameworks, languages used in the project. The level of the documentation should be at the level of senior developer in the organisation"
    }

    prompt = f"""
You are an AI documentation expert. Your task is to generate technical documentation in *Markdown format* based on code, README, commit messages, and existing documentation which was previously generated.
We are using the already existing documentation as one of the inputs so that the output obtained includes the documentation of all the changes made till now. This documentation stands as the entire documentaion of the repo.
---
###  Available Inputs:

####  Commit messages:
{commit_message}

####  README content:
{readme_content}

#### Existing documentation previously:
{existing_doc}

#### Code Files Summary (Do NOT repeat the code):
{code_files_content}

---
### Output Instructions:
- Do *NOT* include or repeat any code from the inputs.
- Do *NOT* list file contents directly.
- Use the information to summarize *what the code does*, not what it contains.
- Describe key *functionalities, **dependencies, and **critical logic parts*.
- Do NOT greet or conclude, output only the documentation.
- Use bullet points, headers, and subheaders to format your response clearly.

Start your response with:
The documentation generated for {user_type} is as follows:

Then continue with the structured explanation for the following audience type: *{user_type.upper()}*

###  Audience Guide:
{prompt_details.get(user_type, 'General purpose documentation')}

Provide clear, concise, and audience-specific documentation.
"""

    print("Generating the documentation using Gemini API...")
    start_time = time.time()
    documentation_text = query_model(prompt)
    print("Done")
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

    with open(doc_file_path, "w", encoding="utf-8") as doc_file:
        doc_file.write(documentation_text)

    print(f" Documentation saved to {doc_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_docs.py <path_to_cloned_repo> [user_type] [cwd_path]")
        sys.exit(1)

    repo_path = os.path.abspath(sys.argv[1])
    user_type = sys.argv[2] if len(sys.argv) > 2 else "client"
    generate_documentation(user_type, repo_path)

    cwd = sys.argv[3] if len(sys.argv) > 3 else None
    if cwd:
        server_script_dir = os.path.abspath(os.path.join(cwd, "Server"))
        print(f"Server script directory: {server_script_dir}")
        command = f"py app.py {sys.argv[1]}"

        print(f"Running: {command} in {server_script_dir}")
        try:
            os.chdir(server_script_dir)
            os.system(command)
        except Exception as e:
            print(f" Failed to run app.py: {e}")