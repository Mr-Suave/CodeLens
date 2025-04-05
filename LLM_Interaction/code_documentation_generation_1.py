import time
import ollama
import os
import sys


def read_file(file_path):
    """Reads the contents of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading the file {file_path}: {e}")
        return None
    
def check_and_pull_model():
    """Check if deepseek-coder:6.7b is available or not"""
    model_list=os.popen("ollama list").read()
    if "deepseek-coder:6.7b" not in model_list:
        print("Pulling deepseek-coder model...")
        os.system("ollama pull deepseek-coder:6.7b")
    else:
        print("Model deepseek-coder:6.7b is already available")

def generate_documentation(user_type,repo_path):
    """Generates documentation using multiple sources and writes to Documentation to repo."""

    data_extraction_dir = os.path.join(repo_path,"Data_Extraction_Files")
    doc_file_path=os.path.join(repo_path,f"Documentation_{user_type}.txt")

    if not os.path.exists(data_extraction_dir):
        print(f"Error: Folder '{data_extraction_dir} not found' not found!")
        return
    check_and_pull_model()

    # Reading specific files
    commit_message = read_file(os.path.join(data_extraction_dir, "Commit_messages.txt")) or "No commit messages found."
    readme_content = read_file(os.path.join(data_extraction_dir, "ReadME.txt")) or "No README content found."
    existing_doc = read_file(doc_file_path) or "No existing documentation found."

    # Reading all the code files dynamically
    code_files_content=""
    for file_name in os.listdir(data_extraction_dir):
        if file_name.endswith(".txt") and file_name not in ["Commit_messages.txt", "ReadME.txt"]:
            file_path = os.path.join(data_extraction_dir, file_name)
            code_files_content += f"\n\n## {file_name}\n\n{read_file(file_path) or ''}"

    #constructing the documenatation prompt based on user type
    prompt_details ={
        "client": "Just give the basic overview of the contents in the files try to explain more functionality and uses but don't use technical terms.",
        "novice": "Give some nice explanation of the code in files, like what code is trying to do and also dependencies. Don't make it too long. Don't include the entire code just explain the critical paths of the code",
        "senior": "Dependencies, structure of the code(architecture), don't display the code just say what code do."
    }

    prompt= f"""
    Generate detailed documentation using the following sources:

    ### Commit messages:
    {commit_message}

    ### ReadME content:
    {readme_content}

    ### Existing documentation:
    {existing_doc}

    ### Code Files:
    {code_files_content}
    
    **Instructions:**
    - Write the documentation in **Markdown format**.
    - **Do NOT copy text directly from the files**. Instead, summarize key points concisely.
    - **DO NOT add any greetings or unnecessary text.**
    - Format the output in **bullet points** and **headings** for clarity.
    Provide documentation in Markdown format focused on: {prompt_details.get(user_type, 'General documentation')}.
    The documentation must start with the sentence "The documentation generated for {user_type} is as follow: ".
    """

    print("Generating the documentation")
    start_time=time.time()
    #response=ollama.generate(model="deepseek-coder:6.7b",prompt=prompt)
    # print("Done")
    # print(f"Time taken: {time.time() - start_time:.2f} seconds")

    # documentation_text = response.response.strip() if hasattr(response, "response") else "No documentation generated."
    
    # with open(doc_file_path, "w", encoding="utf-8") as doc_file:
    #     doc_file.write(documentation_text)
    
    # print(f"Documentation saved to {doc_file_path}")

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage: python generate_docs.py <path_to_cloned_repo> [user_type]")
        sys.exit(1)
    repo_path=os.path.abspath(sys.argv[1])
    user_type=sys.argv[2] if len(sys.argv) > 2 else "client"

    generate_documentation(user_type,repo_path)

    # calling the next step file
    cwd=os.getcwd()
    server_script_dir= os.path.abspath(os.path.join(cwd,"..","Server"))

    command=f"python app.py {sys.argv[1]}"

    print(f"Running: {command} in {server_script_dir}")
    try:
        os.chdir(server_script_dir)
        os.system(command)
    except Exception as e:
        print(f"Failed to run app.py: {e}")