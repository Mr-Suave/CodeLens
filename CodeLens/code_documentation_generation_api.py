import os
import sys
import time
import google.generativeai as genai
from collections import defaultdict

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

def extract_adjacency_list(function_list_path):
    """
    Extract the adjacency list from the function_list.txt file.
    Returns tuple of (all_functions, call_graph)
    """
    if not os.path.exists(function_list_path):
        print(f"Error: Function list file not found at {function_list_path}")
        return [], {}
    
    try:
        with open(function_list_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all functions
        all_functions = []
        if "=== ALL FUNCTIONS ===" in content:
            functions_section = content.split("=== ALL FUNCTIONS ===")[1].split("===")[0].strip()
            all_functions = [line.strip() for line in functions_section.split("\n") if line.strip()]
        
        # Extract call graph
        call_graph = {}
        if "=== FUNCTION CALL GRAPH ===" in content:
            graph_section = content.split("=== FUNCTION CALL GRAPH ===")[1].strip()
            for line in graph_section.split("\n"):
                line = line.strip()
                if not line or "-->" not in line:
                    continue
                caller, callees_str = line.split("-->")
                caller = caller.strip()
                callees = [c.strip() for c in callees_str.split(",")]
                call_graph[caller] = callees
        
        return all_functions, call_graph
    
    except Exception as e:
        print(f"Error parsing function list file: {e}")
        return [], {}

def generate_dependency_analysis(repo_path, user_type):
    """
    Generate a dependency analysis for the given repository and user type.
    Makes a separate API call for this analysis.
    """
    function_list_path = os.path.join(repo_path, "function_list.txt")
    all_functions, call_graph = extract_adjacency_list(function_list_path)
    
    if not all_functions:
        print("No functions found in function list file.")
        return "No function dependency analysis available."
    
    # Prepare statistics for the prompt
    stats = {
        "total_functions": len(all_functions),
        "functions_with_dependencies": len(call_graph),
        "orphaned_functions": len(all_functions) - len(call_graph)
    }
    
    # Find most called functions
    function_calls = defaultdict(int)
    for caller, callees in call_graph.items():
        for callee in callees:
            function_calls[callee] += 1
    
    top_called = sorted(function_calls.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Find functions with most dependencies
    top_callers = sorted(call_graph.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    
    # Create a concise representation of the graph for the API
    # Instead of sending the entire adjacency list, we'll send summaries
    graph_summary = {
        "statistics": stats,
        "top_called_functions": [{"name": name, "call_count": count} for name, count in top_called],
        "top_callers": [{"name": caller, "dependencies": len(callees)} for caller, callees in top_callers],
        "selected_paths": []
    }
    
    # Add a few selected paths for illustration
    for caller, callees in list(call_graph.items())[:5]:
        if callees:
            graph_summary["selected_paths"].append({
                "caller": caller,
                "callees": callees[:5]
            })
    
    # Create prompts based on user type
    user_prompts = {
        "client": """
Generate a function dependency analysis for a non-technical client. 
Explain in simple terms how different parts of the software work together.
Avoid technical jargon. Focus on explaining the purpose and relationships 
between components rather than implementation details.
""",
        "novice": """
Generate a function dependency analysis for a novice developer.
Explain how functions in the codebase depend on each other and what this means
for the overall structure. You can use basic technical terms (like "function call",
"dependency", etc.) but explain any architectural patterns or implications.
""",
        "senior": """
Generate a detailed function dependency analysis for a senior developer.
Analyze code coupling, identify key entry points, assess architectural patterns revealed
by the call graph, and suggest potential improvements or refactorings based on the dependency structure.
Discuss implications for maintainability, extensibility, and adherence to design principles.
"""
    }
    
    prompt = f"""
You are an expert code analyst. Your task is to analyze a function call graph and provide insights
about the codebase structure.

Below is a summary of the function call graph:

1. Statistics:
- Total functions: {stats["total_functions"]}
- Functions with dependencies: {stats["functions_with_dependencies"]}
- Functions without dependencies (orphaned): {stats["orphaned_functions"]}

2. Most frequently called functions (potential utilities or core components):
{", ".join([f"{name} ({count} calls)" for name, count in top_called[:5]])}

3. Functions with most dependencies (potential controllers or entry points):
{", ".join([f"{caller} ({len(callees)} dependencies)" for caller, callees in top_callers[:5]])}

4. Selected call paths (how some functions connect):
{", ".join([f"{path['caller']} → {', '.join(path['callees'][:3])}" for path in graph_summary["selected_paths"][:3]])}

{user_prompts.get(user_type, user_prompts["client"])}

Output a markdown-formatted analysis with appropriate headers and bullet points.
Focus on providing actionable insights rather than just restating the provided statistics.
"""

    print(f"Generating dependency analysis for {user_type}...")
    start_time = time.time()
    dependency_analysis = query_model(prompt)
    print(f"Dependency analysis generated in {time.time() - start_time:.2f} seconds")
    
    # Save the analysis to a file in the root directory instead of Data_Extraction_Files
    analysis_file = os.path.join(repo_path, f"Dependency_Analysis_{user_type}.md")
    
    with open(analysis_file, "w", encoding="utf-8") as f:
        f.write(dependency_analysis)
    
    print(f"Dependency analysis saved to {analysis_file}")
    return dependency_analysis

def generate_documentation(user_type, repo_path):
    """Generate documentation for the repository."""
    data_extraction_dir = os.path.join(repo_path, "Data_Extraction_Files")
    doc_file_path = os.path.join(repo_path, f"Documentation_{user_type}.md")
    
    # Ensure the data extraction directory exists
    os.makedirs(data_extraction_dir, exist_ok=True)

    if not os.path.exists(data_extraction_dir):
        print(f"Error: Folder '{data_extraction_dir}' not found!")
        return

    # First, generate the dependency analysis with a separate API call
    dependency_analysis = generate_dependency_analysis(repo_path, user_type)
    
    # Then proceed with the main documentation generation
    commit_message = read_file(os.path.join(data_extraction_dir, "Commit_messages.txt")) or "No commit messages found."
    readme_content = read_file(os.path.join(data_extraction_dir, "ReadME.txt")) or "No README content found."
    existing_doc = read_file(doc_file_path) or "No existing documentation found."

    code_files_content = ""
    for file_name in os.listdir(data_extraction_dir):
        if file_name.endswith(".txt") and file_name not in ["Commit_messages.txt", "ReadME.txt"]:
            file_path = os.path.join(data_extraction_dir, file_name)
            code_files_content += f"\n\n## {file_name}\n\n{read_file(file_path) or ''}"

    prompt_details = {
        "client": "Just give the basic overview of the contents in the files. Try to explain more functionality, uses and features that are developed, but don't use technical terms. Reference the separate dependency analysis to explain how components work together.",
        "novice": "Give some nice explanation of the code in files, like what the code is trying to do. Don't make it too long. Don't include the entire code – just explain the critical parts of the code. Reference the provided dependency analysis to explain how functions interact. You are allowed to use the technical terms that a novice developer is expected to know and understand like framework etc.",
        "senior": "Give the structure of the code and the architecture based on the code files given to you, don't display the code, but you can display code snippets and important lines of code and explain it line wize for example if you have a file app.py, then you can give few lines of app.py and explain what they do. Also include the details of the frameworks, languages used in the project. Incorporate insights from the separate dependency analysis section. The level of the documentation should be at the level of senior developer in the organisation"
    }

    prompt = f"""
You are an AI documentation expert. Your task is to generate technical documentation in *Markdown format* based on code, README, commit messages, existing documentation which was previously generated, and a separate dependency analysis.
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
- Describe key functionalities and critical logic parts.
- Reference the function dependency analysis (which is provided in a separate section) when discussing architecture.
- Do NOT greet or conclude, output only the documentation.
- Use bullet points, headers, and subheaders to format your response clearly.

Start your response with:
The documentation generated for {user_type} is as follows:

Then continue with the structured explanation for the following audience type: *{user_type.upper()}*

###  Audience Guide:
{prompt_details.get(user_type, 'General purpose documentation')}

Provide clear, concise, and audience-specific documentation.
"""

    print("Generating the main documentation using Gemini API...")
    start_time = time.time()
    documentation_text = query_model(prompt)
    print("Done")
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

    # Combine the main documentation with the dependency analysis
    full_documentation = f"""
{documentation_text}

## Function Dependency Analysis

{dependency_analysis}
"""

    with open(doc_file_path, "w", encoding="utf-8") as doc_file:
        doc_file.write(full_documentation)

    print(f"Complete documentation saved to {doc_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py code_documentation_generation_api.py <path_to_cloned_repo> [user_type] [cwd_path]")
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