import time
import ollama
import os

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
DATA_EXTRACTION_DIR = os.path.join(BASE_DIR, "Data_Extraction_Files")
DOC_FILE_PATH = os.path.join(BASE_DIR, "Documentation.txt")

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

def generate_documentation(user_type):
    """Generates documentation using multiple sources and writes to Documentation.txt."""
    if not os.path.exists(DATA_EXTRACTION_DIR):
        print(f"Error: Folder '{DATA_EXTRACTION_DIR}' not found!")
        return
    check_and_pull_model()

    # Reading specific files
    commit_message = read_file(os.path.join(DATA_EXTRACTION_DIR, "sample_code_commits.txt")) or "No commit messages found."
    readme_content = read_file(os.path.join(DATA_EXTRACTION_DIR, "sample_Readme.txt")) or "No README content found."
    existing_doc = read_file("Documentation.txt") or "No existing documentation found."

    # Reading all the code files dynamically
    code_files_content=""
    for file_name in os.listdir(DATA_EXTRACTION_DIR):
        if file_name.endswith(".txt"):
            file_path = os.path.join(DATA_EXTRACTION_DIR, file_name)
            code_files_content += f"\n\n## {file_name}\n\n{read_file(file_path) or ''}"

    #constructing the documenatation prompt based on user type
    prompt_details ={
        "client": "Just give the basic overview of the contents in the files try to explain more functionality and uses but don't use technical terms.",
        "novice": "Give some nice explanation of the code in files, like what code is trying to do and also dependencies. Don't make it too long.",
        "senior": "Dependencies, structure of the code"
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
    
    Provide documentation in Markdown format focused on: {prompt_details.get(user_type, 'General documentation')}.
    Try to give in points.
    Apart from documentation text don't give any other text.It is a strict rule for example don't say things like sure here is the explanation etc.
    """

    print("Generating the documentation")
    start_time=time.time()
    response=ollama.generate(model="deepseek-coder:6.7b",prompt=prompt)
    print("Done")
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

    documentation_text = response.response.strip() if hasattr(response, "response") else "No documentation generated."
    
    with open("Documentation.txt", "w", encoding="utf-8") as doc_file:
        doc_file.write(documentation_text)
    
    print("Documentation saved to Documentation.txt")

# Set user type
user_type = "senior"
generate_documentation(user_type)