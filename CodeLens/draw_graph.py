import sys, os, ast
import javalang
from collections import defaultdict
import graphviz
import networkx as nx
import matplotlib.pyplot as plt

import os
# ---- USING GRAPHVIZ
# def clean_node_label(full_path_with_func):
#     """
#     Takes a string like 'C:/path/to/file.py::function_name'
#     and returns 'file.py::function_name'
#     """
#     try:
#         file_path, func_name = full_path_with_func.split("::")
#         file_name = os.path.basename(file_path)
#         return f"{file_name}::{func_name}"
#     except ValueError:
#         # If it's not in 'file::func' format, return as is
#         return full_path_with_func


# def export_to_dot(graph, output_path="call_graph.dot"):
#     dot = graphviz.Digraph(comment="Function Call Graph")

#     # Add nodes and edges
#     for caller in graph:
#         dot.node(clean_node_label(caller))
#         for callee in graph[caller]:
#             dot.edge(clean_node_label(caller), clean_node_label(callee))


#     dot.render(output_path, view=False, format='png')
#     print(f"Call graph saved to {output_path}.png")

# --- USING NETWORKX
def clean_node_label(full_path_with_func):
    try:
        file_path, func_name = full_path_with_func.split("::")
        file_name = os.path.basename(file_path)
        return f"{file_name}::{func_name}"
    except ValueError:
        return full_path_with_func

def draw_call_graph(graph):
    G = nx.DiGraph()

    for caller, callees in graph.items():
        for callee in callees:
            G.add_edge(clean_node_label(caller), clean_node_label(callee))

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", 
            font_size=10, font_weight="bold", arrowsize=20, edge_color="gray")
    plt.title("Function Call Graph", fontsize=15)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def get_source_files(repo_path):
    valid_ext = ('.py', '.java')
    files = []
    for root, _, filenames in os.walk(repo_path, followlinks=True):
        for file in filenames:
            if file.endswith(valid_ext):
                files.append(os.path.join(root, file))
    return files
# --- PYTHON PARSER ---
class PythonFunctionVisitor(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.functions = set()
        self.edges = []
        self.builtin_funcs = set(dir(__builtins__))

    def visit_FunctionDef(self, node):
        func_name = f"{self.file_path}::{node.name}"
        self.functions.add(func_name)

        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Call):
                # Handle simple function calls like print(x)
                if isinstance(subnode.func, ast.Name):
                    callee_name = subnode.func.id
                    if callee_name not in self.builtin_funcs:
                        self.edges.append((func_name, callee_name))
                # Skip method calls like obj.foo()
                elif isinstance(subnode.func, ast.Attribute):
                    continue

        self.generic_visit(node)


# --- JAVA ---
def parse_java_file(file_path):
    with open(file_path, 'r') as f:
        code = f.read()
    try:
        tree = javalang.parse.parse(code)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return set(), []

    functions = set()
    edges = []

    for path, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            full_name = f"{file_path}::{node.name}"
            functions.add(full_name)

            # Handle method invocations within the method
            for child_path, child_node in node:
                if isinstance(child_node, javalang.tree.MethodInvocation):
                    edges.append((full_name, child_node.member))
    
    return functions, edges


# --- MAIN ---
def main(repo_path):
    graph = defaultdict(list)
    functions = set()

    for file_path in get_source_files(repo_path):
        if file_path.endswith('.py'):
            with open(file_path, 'r') as f:
                try:
                    tree = ast.parse(f.read())
                    visitor = PythonFunctionVisitor(file_path)
                    visitor.visit(tree)
                    functions.update(visitor.functions)
                    for src, dst in visitor.edges:
                        graph[src].append(dst)
                except:
                    continue

        elif file_path.endswith('.java'):
            fns, edges = parse_java_file(file_path)
            functions.update(fns)
            for src, dst in edges:
                graph[src].append(dst)

    print("\n=== FUNCTION CALL GRAPH (Adjacency List) ===")
    for func in sorted(graph):
        print(f"{func} --> {', '.join(graph[func])}")
    draw_call_graph(graph)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: draw_graph.py <repo_path>")
        sys.exit(1)
    main(sys.argv[1])
