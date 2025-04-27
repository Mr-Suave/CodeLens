import sys
import os
import ast
import re
from collections import defaultdict
from typing import Optional
import networkx as nx
import matplotlib.pyplot as plt

# Directories to exclude from analysis
EXCLUDED_DIRS = [
    'node_modules',
    'dist',
    'build',
    'venv',
    '.git',
    '__pycache__',
    '.gradle',
    '.idea',
    '.vscode',
    'vendor',
    'bin',
    'obj',
    'target',
    '.dart_tool',
    '.pub-cache',
    'android/app/build',
    'ios/Pods',
    'lib/generated',
    'gen',
    'out',
    'cmake-build',
    'bazel-out',
    'build-output',
    'generated_plugin_registrant'
]

# File patterns to exclude
EXCLUDED_FILE_PATTERNS = [
    r'.*\.min\.js$',
    r'.*\.bundle\.js$',
    r'.*generated.*\.dart$',
    r'.*\.g\.dart$',
    r'.*\.freezed\.dart$',
    r'.*\.pb\..*$',
    r'.*_generated\..*$',
    r'R\.java$',
    r'BuildConfig\.java$',
    r'.*\.designer\.cs$',
    r'AndroidManifest\.xml$'
]

def clean_node_label(full_path_with_func):
    """Create a cleaner node label by extracting just the filename and function name."""
    try:
        file_path, func_name = full_path_with_func.split("::")
        file_name = os.path.basename(file_path)
        return f"{file_name}::{func_name}"
    except ValueError:
        return full_path_with_func

def draw_call_graph(graph, max_nodes=200):
    """Draw the function call graph using NetworkX with size limits for performance."""
    print(f"Preparing to draw graph with {len(graph)} callers")
    
    # If graph is too big, limit it for visualization
    if len(graph) > max_nodes:
        print(f"Graph too large ({len(graph)} nodes), limiting to {max_nodes} nodes for visualization")
        # Take the nodes with the most connections
        top_nodes = sorted(graph.items(), key=lambda x: len(x[1]), reverse=True)[:max_nodes]
        limited_graph = {caller: callees for caller, callees in top_nodes}
    else:
        limited_graph = graph
    
    G = nx.DiGraph()
    
    # Add edges to the graph
    edge_count = 0
    for caller, callees in limited_graph.items():
        clean_caller = clean_node_label(caller)
        # Limit edges per node for performance
        for callee in callees[:10]:  
            clean_callee = clean_node_label(callee)
            G.add_edge(clean_caller, clean_callee)
            edge_count += 1
            
            # Break if we exceed a reasonable edge count
            if edge_count > 500:
                print("Limiting graph to 500 edges for performance")
                break
        
        if edge_count > 500:
            break
    
    print(f"Graph has {len(G.nodes())} nodes and {len(G.edges())} edges")
    
    try:
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=0.3, iterations=20)  # Reduced iterations for speed
        nx.draw(G, pos, with_labels=True, node_size=1500, node_color="skyblue",
                font_size=8, font_weight="bold", arrowsize=15, edge_color="gray")
        plt.title("Function Call Graph (Limited View)", fontsize=15)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig("function_call_graph.png", dpi=200)
        print("Graph saved as function_call_graph.png")
        
        # Close the figure to free memory
        plt.close()
    except Exception as e:
        print(f"Error generating visualization: {e}")
        print("Continuing without visualization")

def get_source_files(repo_path):
    """Get all source files with supported extensions from the repository, excluding unwanted directories."""
    valid_ext = ('.py', '.java', '.js')
    files = []
    
    # Calculate total files for progress reporting
    total_files = 0
    for root, dirs, filenames in os.walk(repo_path, topdown=True):
        # Remove excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not any(
            excluded_dir in os.path.join(root, d).lower() for excluded_dir in EXCLUDED_DIRS
        )]
        
        total_files += len([f for f in filenames if f.endswith(valid_ext)])
    
    print(f"Found {total_files} source files to analyze after filtering")
    
    # Get the actual file list
    file_count = 0
    for root, dirs, filenames in os.walk(repo_path, topdown=True):
        # Filter dirs in-place to prevent descent into excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not any(
            excluded_dir in os.path.join(root, d).lower() for excluded_dir in EXCLUDED_DIRS
        )]
        
        for file in filenames:
            if file.endswith(valid_ext):
                file_path = os.path.join(root, file)
                
                # Skip files matching excluded patterns
                if any(re.match(pattern, file_path) for pattern in EXCLUDED_FILE_PATTERNS):
                    continue
                
                # Skip very large files (probably generated or not worth parsing)
                try:
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
                    if file_size > 1:  # Skip files larger than 1MB
                        print(f"Skipping large file ({file_size:.1f}MB): {file_path}")
                        continue
                except Exception:
                    pass
                
                files.append(file_path)
                file_count += 1
                
                # Show progress every 50 files
                if file_count % 50 == 0:
                    print(f"Collected {file_count}/{total_files} files...")
    
    return files

# --- PYTHON PARSER ---
class PythonFunctionVisitor(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.functions = set()
        self.edges = []
        self.builtin_funcs = set(dir(__builtins__))
        self.current_function = None

    def visit_FunctionDef(self, node):
        func_name = f"{self.file_path}::{node.name}"
        self.functions.add(func_name)
        
        # Save the current function context
        previous_function = self.current_function
        self.current_function = func_name
        
        # Process function body
        self.generic_visit(node)
        
        # Restore previous function context
        self.current_function = previous_function

    def visit_Call(self, node):
        """Visit call nodes to extract function calls."""
        if self.current_function is None:
            # Skip if we're not in a function context
            self.generic_visit(node)
            return

        # Handle function calls
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
            if callee_name not in self.builtin_funcs:
                callee_path = f"{self.file_path}::{callee_name}"
                self.edges.append((self.current_function, callee_path))
        
        # Handle method calls (obj.method())
        elif isinstance(node.func, ast.Attribute):
            if hasattr(node.func, 'attr'):
                callee_name = node.func.attr
                callee_path = f"{self.file_path}::{callee_name}"
                self.edges.append((self.current_function, callee_path))

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Handle async functions in Python."""
        self.visit_FunctionDef(node)  # Same processing as regular functions


# --- JAVA PARSER ---
def parse_java_file(file_path):
    """Parse a Java file to extract function names and calls using regex."""
    functions = set()
    edges = []
    
    # Pattern for method declarations
    method_pattern = r'(?:public|private|protected|static|\s)+(?:[\w\<\>\[\]]+\s+)*([\w]+)\s*\([^\)]*\)\s*(?:\{|throws)'
    
    # Pattern for method calls
    call_pattern = r'(?:\s|\.|^)([a-zA-Z0-9_]+)\s*\('
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Find all method declarations
        method_matches = re.finditer(method_pattern, content)
        for match in method_matches:
            method_name = match.group(1)
            full_name = f"{file_path}::{method_name}"
            functions.add(full_name)
            
            # Look for method calls within this method - simplified approach
            method_start = match.end()
            # Find the end of method with a basic approach (not perfect but fast)
            next_opening = content.find('{', method_start)
            if next_opening > 0:
                brace_count = 1
                method_end = next_opening + 1
                # Limit scanning to avoid performance issues with large methods
                scan_limit = min(len(content), next_opening + 20000)
                while brace_count > 0 and method_end < scan_limit:
                    if content[method_end] == '{':
                        brace_count += 1
                    elif content[method_end] == '}':
                        brace_count -= 1
                    method_end += 1
                
                if method_end > next_opening + 1:
                    method_body = content[next_opening+1:method_end-1]
                    # Limit number of calls to avoid performance issues
                    call_matches = list(re.finditer(call_pattern, method_body))[:50]
                    for call_match in call_matches:
                        called_method = call_match.group(1)
                        if called_method != method_name and not called_method.startswith(('if', 'for', 'while')):
                            edges.append((full_name, f"{file_path}::{called_method}"))
    
    except Exception as e:
        print(f"Error in parsing Java file {file_path}: {e}")
        
    return functions, edges


# --- JAVASCRIPT PARSER ---
def parse_js_file(file_path):
    """Parse a JavaScript file to extract function names and calls using regex."""
    functions = set()
    edges = []
    
    # Pattern for function declarations (various forms)
    func_patterns = [
        r'function\s+([a-zA-Z0-9_$]+)\s*\(', # function name()
        r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*function\s*\(', # const name = function()
        r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*\([^)]*\)\s*=>', # const name = () =>
        r'(?:class|Object)\.([a-zA-Z0-9_$]+)\s*=\s*function', # Class.name = function
        r'([a-zA-Z0-9_$]+):\s*function\s*\(' # name: function()
    ]
    
    # Pattern for function calls
    call_pattern = r'([a-zA-Z0-9_$]+)\s*\('
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Skip minified files based on line length
        lines = content.split('\n')
        if any(len(line) > 500 for line in lines[:20]):
            print(f"Skipping likely minified JS file: {file_path}")
            return functions, edges
        
        # Extract all function declarations
        current_functions = []
        for pattern in func_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                func_name = match.group(1)
                full_name = f"{file_path}::{func_name}"
                functions.add(full_name)
                current_functions.append((full_name, match.start(), match.end()))
        
        # Sort functions by position in file
        current_functions.sort(key=lambda x: x[1])
        
        # Process function bodies (simplified approach)
        for i, (func_name, start_pos, func_start) in enumerate(current_functions):
            # Determine end of function (either next function or reasonable limit)
            if i < len(current_functions) - 1:
                next_func_start = current_functions[i+1][1]
                func_content = content[func_start:next_func_start]
            else:
                # For the last function, limit scanning
                func_content = content[func_start:min(func_start + 10000, len(content))]
            
            # Find function calls
            call_matches = list(re.finditer(call_pattern, func_content))[:50]  # Limit calls per function
            for call_match in call_matches:
                called_func = call_match.group(1)
                if called_func != func_name.split('::')[1] and not called_func.startswith(('if', 'for', 'while', 'switch')):
                    edges.append((func_name, f"{file_path}::{called_func}"))
    
    except Exception as e:
        print(f"Error in parsing JavaScript file {file_path}: {e}")
    
    return functions, edges

def extract_function_code(file_path: str, function_name: str) -> Optional[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                    start_line = node.lineno - 1
                    end_line = node.end_lineno
                    return "\n".join(source.splitlines()[start_line:end_line])
            return None
        except Exception as e:
            print(f"Error extracting {function_name} from {file_path}: {e}")
            return None
        
# dummy comment

def get_code_blocks_for_nodes(nodes: ast.Set[ast.Tuple[str, str]]) -> ast.Dict[str, str]:
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

# BOOM
def main(repo_path):
    """Main function to parse a repository and generate a call graph."""
    graph = defaultdict(list)
    all_functions = set()
    function_code_blocks = {}

    print(f"Analyzing repository: {repo_path}")
    print("Excluding directories:", ", ".join(EXCLUDED_DIRS))

    # Get source files with exclusions
    source_files = get_source_files(repo_path)
    print(f"Found {len(source_files)} source files to analyze after filtering")

    file_count = 0
    for file_path in source_files:
        file_count += 1

        if file_count % 10 == 0 or file_count == len(source_files):
            print(f"Processing file {file_count}/{len(source_files)}: {os.path.basename(file_path)}")

        try:
            if file_path.endswith('.py'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        source = f.read()
                        tree = ast.parse(source)
                        visitor = PythonFunctionVisitor(file_path)
                        visitor.visit(tree)
                        all_functions.update(visitor.functions)
                        for src, dst in visitor.edges:
                            graph[src].append(dst)

                        # Extract code for each Python function
                        for _, func in visitor.functions:
                            code = extract_function_code(file_path, func)
                            if code:
                                function_code_blocks[f"{file_path}::{func}"] = code

                    except Exception as e:
                        print(f"Error parsing Python file {file_path}: {e}")
                        continue

            elif file_path.endswith('.java'):
                functions, edges = parse_java_file(file_path)
                all_functions.update(functions)
                for src, dst in edges:
                    graph[src].append(dst)

                # Extract Java code blocks
                code_blocks = get_code_blocks_for_nodes(functions)
                function_code_blocks.update(code_blocks)

            elif file_path.endswith('.js'):
                functions, edges = parse_js_file(file_path)
                all_functions.update(functions)
                for src, dst in edges:
                    graph[src].append(dst)

                # Extract JavaScript code blocks
                code_blocks = get_code_blocks_for_nodes(functions)
                function_code_blocks.update(code_blocks)

        except Exception as e:
            print(f"Unexpected error processing {file_path}: {e}")
            continue

    # Output all functions
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

    # Output call graph
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

    # Visualization
    if graph:
        print("\nGenerating call graph visualization...")
        try:
            draw_call_graph(graph, function_code_blocks)
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
    if not function_code_blocks:
        print("No code blocks extracted.")
    else:
        sample_count = 5  # adjust if you want to see more
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