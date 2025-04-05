import time
import ollama
import os
import json
import sys

if len(sys.argv)<3:
    print("Usage: python script.py <path_to_user_repo> <doc_type>")
    sys.exit(1)

USER_REPO_DIR = os.path.abspath(sys.argv[1])
user_type = sys.argv[2].lower()

# --- Paths ---
DATA_EXTRACTION_DIR = os.path.join(USER_REPO_DIR, "Data_Extraction_Files")
JSON_FILE_PATH = os.path.join(USER_REPO_DIR, f".Documentation_{user_type}.json")
DOC_FILE_PATH = os.path.join(USER_REPO_DIR, f"Documentation_{user_type}.txt")


def read_file(file_path):
    """Reads the contents of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading the file {file_path}: {e}")
        return None
    
def load_json(file_path):
    """Loads JSON data from a file, or returns an empty dictionary if the file doesn't exist."""
    if os.path.exists(file_path):
        try:
            with open(file_path,"r",encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}. Resetting to empty JSON.")
            return {}
    return {}

def save_json(file_path,data):
    """Saves the given dictionary as a JSON file"""
    with open(file_path,"w",encoding="utf-8") as file:
        json.dump(data,file,indent=4)

def check_and_pull_model():
    """Check if deepseek-coder:6.7b is available or not"""
    model_list=os.popen("ollama list").read()
    if "deepseek-coder:6.7b" not in model_list:
        print("Pulling deepseek-coder model...")
        os.system("ollama pull deepseek-coder:6.7b")
    else:
        print("Model deepseek-coder:6.7b is already available")

def generate_documentation():
    """Generates documentation using multiple sources and writes to Documentation.txt."""
    if not os.path.exists(DATA_EXTRACTION_DIR):
        print(f"Error: Folder '{DATA_EXTRACTION_DIR}' not found!")
        return
    
    check_and_pull_model()
    
    # Load existing JSON documentation
    documentation_data=load_json(JSON_FILE_PATH)

    # Reading specific files
    commit_message = read_file(os.path.join(DATA_EXTRACTION_DIR, "Commit_messages.txt")) or "No commit messages found."
    readme_content = read_file(os.path.join(DATA_EXTRACTION_DIR, "ReadME.txt")) or "No README content found."

    # Reading all the code files dynamically
    code_files_content={}
    for file_name in os.listdir(DATA_EXTRACTION_DIR):
        if file_name.endswith(".txt"):
            base_name=os.path.splitext(file_name)[0]
            file_path = os.path.join(DATA_EXTRACTION_DIR, file_name)
            file_content=read_file(file_path) or ""

            # check if this file documentation is already in json if not initialize
            if file_name not in documentation_data:
                documentation_data[base_name] = {"summary": "No documentation available currently"}
            
            # Store code content for LLM processing
            code_files_content[base_name]=file_content
    print("****Source Code*****")
    print(code_files_content)
    print("****Documentation Content*****")
    print(documentation_data)
    print("****Commit Messages*****")
    print(commit_message)
    print("*****ReadMe content*****")
    print(readme_content)

    #constructing the documenatation prompt based on user type
    prompt_details ={
        "client": "Just give the basic overview of the contents in the files try to explain more functionality and uses but don't use technical terms.",
        "novice": "Give some nice explanation of the code in files, like what code is trying to do and also dependencies. Don't make it too long. Don't include the entire code just explain the critical paths of the code",
        "senior": "Dependencies, structure of the code(architecture), don't display the code just say what code do."
    }

    prompt= f"""
    Generate JSON-Based detailed documentation for each file based on its content:

    ### Commit messages:
    {commit_message}

    ### ReadME content:
    {readme_content}

    ### Existing documentation:
    {json.dumps(documentation_data,indent=4)}

    ### Source code:
    {json.dumps(code_files_content,indent=4)}
    '
    **Instructions:**
    - **Strictly return a valid JSON object. Do NOT include any extra text, explanations, or preambles.**
    - **Each file name from "Source Code" must be used as a JSON key in the output. Do NOT modify or generate new keys.**
    - In "Source code" there is 'name of file':content regarding that , and your json should include the same 'name of file':modified content of the previous content that you get in existing documentation.
    - Don't make the documentation too small, be a bit creative in expressing here.  
    - Each file name should be a JSON key.
    - Also put the readme and commit messages related documentation in the json.
    - Each file should contain a `"summary"` field explaining its purpose.
    - The output **must be valid JSON**, with proper syntax and structure.
    - Follow the documentation style for {user_type}: {prompt_details.get(user_type, 'General documentation')}.

    **Return JSON only. Do not include any introductory or explanatory text.**
    """

    print(f"Generating {user_type} documentation")
    start_time=time.time()
    response=ollama.generate(model="deepseek-coder:6.7b",prompt=prompt)
    print("Done")
    print(f"Time taken: {time.time() - start_time:.2f} seconds")
    print("Raw LLM Response:")
    print(response.response) # debugging

    # Extract JSON response
    if hasattr(response,"response"):
        try:
            generated_json=json.loads(response.response.strip())
        except json.JSONDecodeError:
            print("Error: LLM output is not valid JSON.")
            return
    else: 
        print("Error: No response from LLM.")
        return
    
    # Merge new documentation with existing JSON data
    documentation_data.update(generated_json)

    # Save the updated JSON
    save_json(JSON_FILE_PATH,documentation_data)

    markdown_content=json_to_markdown(documentation_data,user_type)
    with open(DOC_FILE_PATH,"w",encoding="utf-8") as doc_file:
        doc_file.write(markdown_content)
    print(f"Documentation saved to {DOC_FILE_PATH}")

def json_to_markdown(json_data,user_type):
    """Converts JSON documentation to Markdown format."""
    md_content=f"# Documentation for {user_type} \n\n"

    for file_name, details in json_data.items():
        md_content+=f"## {file_name}\n\n"
        if isinstance(details,dict):
            for key, value in details.items():
                md_content+=f"{value}\n\n"
        else:
            md_content += f"{details}\n\n"
    return md_content

generate_documentation()