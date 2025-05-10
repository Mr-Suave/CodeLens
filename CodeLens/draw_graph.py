import sys
import os
import ast
import re
from collections import defaultdict
from typing import Optional
import networkx as nx
import matplotlib.pyplot as plt

# Directories to exclude from the analysis
EXCLUDED_DIRS = [...]

# File patterns to exclude from the analysis
EXCLUDED_FILE_PATTERNS = [...]

def clean_node_label(full_path_with_func):
    """Extracts filename and function name for cleaner node labels."""
    try:
        file_path, func_name = full_path_with_func.split("::")
        file_name = os.path.basename(file_path)
        return f"{file_name}::{func_name}"
    except ValueError:
        return full_path_with_func

def draw_call_graph(graph, max_nodes=200):
    """Draws the function call graph, limiting nodes and edges for performance."""
    print(f"Preparing to draw graph with {len(graph)} callers")
    
    # Limit nodes for large graphs
    if len(graph) > max_nodes:
        print(f"Graph too large ({len(graph)} nodes), limiting to {max_nodes} nodes for visualization")
        top_nodes = sorted(graph.items(), key=lambda x: len(x[1]), reverse=True)[:max_nodes]
        limited_graph = {caller: callees for caller, callees in top_nodes}
    else:
        limited_graph = graph
    
    G = nx.DiGraph()
    
    # Add edges, limiting count for performance
    edge_count = 0
    for caller, callees in limited_graph.items():
        clean_caller = clean_node_label(caller)
        # Limit edges per node
        for callee in callees[:10]:  
            clean_callee = clean_node_label(callee)
            G.add_edge(clean_caller, clean_callee)
            edge_count += 1
            # Break if too many edges
            if edge_count > 500:
                print("Limiting graph to 500 edges for performance")
                break
        if edge_count > 500:
            break
    
    print(f"Graph has {len(G.nodes())} nodes and {len(G.edges())} edges")
    
    try:
        # Draw and save the graph
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=0.3, iterations=20) 
        nx.draw(G, pos, with_labels=True, node_size=1500, node_color="skyblue",
                font_size=8, font_weight="bold", arrowsize=15, edge_color="gray")
        plt.title("Function Call Graph (Limited View)", fontsize=15)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig("function_call_graph.png", dpi=200)
        print("Graph saved as function_call_graph.png")
        plt.close() # Close to free memory
    except Exception as e:
        print(f"Error generating visualization: {e}")
        print("Continuing without visualization")

def get_source_files(repo_path):
    """Retrieves source files, excluding specified directories and patterns."""
    valid_ext = ('.py', '.java', '.js')
    files = []
    
    # Calculate total files for progress
    total_files = 0
    for root, dirs, filenames in os.walk(repo_path, topdown=True):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not any(
            excluded_dir in os.path.join(root, d).lower() for excluded_dir in EXCLUDED_DIRS
        )]
        total_files += len([f for f in filenames if f.endswith(valid_ext)])
    
    print(f"Found {total_files} source files to analyze after filtering")
    
    # Collect source files
    file_count = 0
    for root, dirs, filenames in os.walk(repo_path, topdown=True):

        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not any(
            excluded_dir in os.path.join(root, d).lower() for excluded_dir in EXCLUDED_DIRS
        )]
        
        for file in filenames:
            if file.endswith(valid_ext):
                file_path = os.path.join(root, file)
                
                # Exclude files matching patterns
                if any(re.match(pattern, file_path) for pattern in EXCLUDED_FILE_PATTERNS):
                    continue
                
                # Exclude large files
                try:
                    file_size = os.path.getsize(file_path) / (1024 * 1024) 
                    if file_size > 1:  # Skip files > 1MB
                        print(f"Skipping large file ({file_size:.1f}MB): {file_path}")
                        continue
                except Exception:
                    pass
                
                files.append(file_path)
                file_count += 1
                # Print progress
                if file_count % 50 == 0:
                    print(f"Collected {file_count}/{total_files} files...")
    
    return files

# --- PYTHON PARSER ---
class PythonFunctionVisitor(ast.NodeVisitor):
    """Extracts function definitions and calls from Python code."""
    def __init__(self, file_path):
        self.file_path = file_path
        self.functions = set()
        self.edges = []
        self.builtin_funcs = set(dir(__builtins__))
        self.current_function = None # Keep track of current function context

    def visit_FunctionDef(self, node):
        """Handles function definitions."""
        func_name = f"{self.file_path}::{node.name}"
        self.functions.add(func_name)

        previous_function = self.current_function # Save previous context
        self.current_function = func_name # Update the current function context

        self.generic_visit(node) # Visit function body

        self.current_function = previous_function  # Restore the context

    def visit_Call(self, node):
        """Handles function/method calls within functions."""
        if self.current_function is None: # Skip if not inside a function
            self.generic_visit(node)
            return
        
        # Check if a name node representing a function
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id

            if callee_name not in self.builtin_funcs:
                callee_path = f"{self.file_path}::{callee_name}"
                self.edges.append((self.current_function, callee_path))
        #Check if an attribute node representing a method.        
        elif isinstance(node.func, ast.Attribute):
            if hasattr(node.func, 'attr'):
                callee_name = node.func.attr
                callee_path = f"{self.file_path}::{callee_name}"
                self.edges.append((self.current_function, callee_path))

        self.generic_visit(node) #Handles other nested function calls

    def visit_AsyncFunctionDef(self, node):
        """Handles async function definitions."""
        self.visit_FunctionDef(node)  # Treat async functions same as regular functions


# --- JAVA PARSER ---
def parse_java_file(file_path):
    """Parses a Java file for function definitions and calls using regex."""
    functions = set()
    edges = []
    
    # Regex patterns for method declarations and calls
    method_pattern = r'(?:public|private|protected|static|\s)+(?:[\w\<\>\[\]]+\s+)*([\w]+)\s*\([^\)]*\)\s*(?:\{|throws)'
    call_pattern = r'(?:\s|\.|^)([a-zA-Z0-9_]+)\s*\('
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Find method declarations
        method_matches = re.finditer(method_pattern, content)
        for match in method_matches:
            method_name = match.group(1)
            full_name = f"{file_path}::{method_name}"
            functions.add(full_name)

            method_start = match.end()
            next_opening = content.find('{', method_start)
            if next_opening > 0:

                brace_count = 1
                method_end = next_opening + 1

                scan_limit = min(len(content), next_opening + 20000) #Avoid performance issues with large methods

                while brace_count > 0 and method_end < scan_limit:
                    if content[method_end] == '{':
                        brace_count += 1
                    elif content[method_end] == '}':
                        brace_count -= 1
                    method_end += 1
                
                #Look for calls within the current method body
                if method_end > next_opening + 1:
                    method_body = content[next_opening+1:method_end-1]
                    
                    call_matches = list(re.finditer(call_pattern, method_body))[:50] # Limit calls to 50
                    for call_match in call_matches:
                        called_method = call_match.group(1)
                        if called_method != method_name and not called_method.startswith(('if', 'for', 'while')):
                            edges.append((full_name, f"{file_path}::{called_method}"))
    
    except Exception as e:
        print(f"Error in parsing Java file {file_path}: {e}")
        
    return functions, edges


# --- JAVASCRIPT PARSER ---
def parse_js_file(file_path):
    """Parses a JavaScript file for function definitions and calls using regex."""
    functions = set()
    edges = []
    
    # Regex patterns for function declarations and calls (handles different JS syntax)
    func_patterns = [...]
    
    call_pattern = r'([a-zA-Z0-9_$]+)\s*\('
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Skip likely minified files
        lines = content.split('\n')
        if any(len(line) > 500 for line in lines[:20]):
            print(f"Skipping likely minified JS file: {file_path}")
            return functions, edges
        
        # Find function declarations
        current_functions = []
        for pattern in func_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                full_name = f"{file_path}::{func_name}"
                functions.add(full_name)
                current_functions.append((full_name, match.start(), match.end()))
        
        # Sort functions by start position
        current_functions.sort(key=lambda x: x[1])
        

        for i, (func_name, start_pos, func_start) in enumerate(current_functions):

            if i < len(current_functions) - 1:
                next_func_start = current_functions[i+1][1]
                func_content = content[func_start:next_func_start]
            else:
                func_content = content[func_start:min(func_start + 10000, len(content))]  # Limit scanning for last function

            call_matches = list(re.finditer(call_pattern, func_content))[:50] # Limit to 50 calls
            for call_match in call_matches:
                called_func = call_match.group(1)
                if called_func != func_name.split('::')[1] and not called_func.startswith(('if', 'for', 'while', 'switch')):
                    edges.append((func_name, f"{file_path}::{called_func}"))
    
    except Exception as e:
        print(f"Error in parsing JavaScript file {file_path}: {e}")
    
    return functions, edges


def extract_function_code(file_path: str, function_name: str) -> Optional[str]:
    """Extracts the code of a given function from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        for node in tree.body:
            #Checks for functions and async functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                start_line = node.lineno - 1
                end_line = node.end_lineno
                return "\n".join(source.splitlines()[start_line:end_line])
        return None
    except Exception as e:
        print(f"Error extracting {function_name} from {file_path}: {e}")
        return None


def get_code_blocks_for_nodes(nodes):
    """Extracts code blocks for given function nodes."""
    result = {}
    for path, func in nodes:
        code = extract_function_code(path, func)
        if code:
            result[f"{path}::{func}"] = code
    print("Reslt found")
    for path,func in result:
        print(f"Function name :{func}")
        print(f"Code for the function {func}: {code}")
    return result


def main(repo_path):
    """Main function to analyze the repository and generate the call graph."""
    graph = defaultdict(list)
    all_functions = set()
    function_code_blocks = {} # to store function code

    print(f"Analyzing repository: {repo_path}")
    print("Excluding directories:", ", ".join(EXCLUDED_DIRS))

    # Get source files
    source_files = get_source_files(repo_path)
    print(f"Found {len(source_files)} source files to analyze after filtering")

    file_count = 0
    for file_path in source_files:
        file_count += 1

        # Print progress
        if file_count % 10 == 0 or file_count == len(source_files):
            print(f"Processing file {file_count}/{len(source_files)}: {os.path.basename(file_path)}")

        try:
            if file_path.endswith('.py'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        # Parse Python files
                        source = f.read()
                        tree = ast.parse(source)
                        visitor = PythonFunctionVisitor(file_path)
                        visitor.visit(tree)
                        all_functions.update(visitor.functions)
                        for src, dst in visitor.edges:
                            graph[src].append(dst)

                        # Extract Python Code
                        for _, func in visitor.functions:
                            code = extract_function_code(file_path, func)

                            if code:
                                function_code_blocks[f"{file_path}::{func}"] = code

                    except Exception as e:
                        print(f"Error parsing Python file {file_path}: {e}")
                        continue

            elif file_path.endswith('.java'):
                # Parse Java files
                functions, edges = parse_java_file(file_path)
                all_functions.update(functions)
                for src, dst in edges:
                    graph[src].append(dst)
                # Extract Java Code
                code_blocks = get_code_blocks_for_nodes(functions)
                function_code_blocks.update(code_blocks)


            elif file_path.endswith('.js'):
                # Parse JavaScript files
                functions, edges = parse_js_file(file_path)
                all_functions.update(functions)
                for src, dst in edges:
                    graph[src].append(dst)

                # Extract js code blocks
                code_blocks = get_code_blocks_for_nodes(functions)
                function_code_blocks.update(code_blocks)

        except Exception as e:
            print(f"Unexpected error processing {file_path}: {e}")
            continue

    # Output all functions (limited to 100 for large projects)
    print("\n=== ALL FUNCTIONS ===")
    function_list = [clean_node_label(func) for func in sorted(all_functions)]
    if len(function_list) > 100:
        print(f"Found {len(function_list)} functions. Showing first 100:")
        for func in function_list[:100]:
            print(func)
        print(f"... and {len(function_list) - 100} more functions.")
    else:
        for func in function_list:
            print(func)

    print(f"\nTotal functions found: {len(all_functions)}")

    # Output call graph (adjacency list format, limited to 50 for large graphs)
    print("\n=== FUNCTION CALL GRAPH (Adjacency List) ===")
    graph_items = list(sorted(graph.items()))
    if len(graph_items) > 50:
        print(f"Found {len(graph_items)} function relationships. Showing first 50:")
        for func, callees in graph_items[:50]:
            if callees:
                print(f"{clean_node_label(func)} --> {', '.join(clean_node_label(c) for c in callees[:5])}{', ...' if len(callees) > 5 else ''}")
        print(f"... and {len(graph_items) - 50} more relationships.")
    else:
        for func, callees in graph_items:
            if callees:
                print(f"{clean_node_label(func)} --> {', '.join(clean_node_label(c) for c in callees)}")


    # Draw call graph
    if graph:
        print("\nGenerating call graph visualization...")
        try:
            draw_call_graph(graph)
        except Exception as e:
            print(f"Error generating graph visualization: {e}")
    else:
        print("\nNo function call relationships found to visualize.")

    # Write results to file
    with open("function_list.txt", "w", encoding="utf-8") as f:
        f.write("=== ALL FUNCTIONS ===\n")
        for func in sorted(all_functions):
            f.write(f"{clean_node_label(func)}\n")

        f.write("\n=== FUNCTION CALL GRAPH ===\n")
        for func in sorted(graph):
            if graph[func]:
                f.write(f"{clean_node_label(func)} --> {', '.join(clean_node_label(c) for c in graph[func])}\n")

    print("\nResults written to function_list.txt")


    print("\n=== EXTRACTED FUNCTION CODE BLOCKS (Sample) ===")
    # Displays a sample of up to 5 function code blocks. Adjust as needed
    if not function_code_blocks:
        print("No code blocks extracted.")
    else:
        sample_count = 5  # Adjust sample count here
        for i, (key, code) in enumerate(function_code_blocks.items()):
            print(f"\nFunction: {key}")
            print("Code:")
            print(code)
            print("-" * 40)
            if i + 1 >= sample_count:
                print(f"... and {len(function_code_blocks) - sample_count} more functions.\n")
                break


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python draw_graph.py <repo_path>")
        sys.exit(1)
    main(sys.argv[1])
