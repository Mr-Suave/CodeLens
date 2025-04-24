import networkx as nx
from git import Repo
import os
import matplotlib.pyplot as plt

# Automatically find the current working directory
repo_path = os.getcwd()

# Create a directed graph for parent-child structure
G = nx.DiGraph()

try:
    repo = Repo(repo_path, search_parent_directories=True)
    git_root = repo.git.rev_parse("--show-toplevel")
    
    # Limit to the latest 5 commits
    commits = list(repo.iter_commits())[:3]
    
    for commit in commits:
        commit_msg = commit.message.strip()
        commit_node = f"🔨 {commit_msg[:40]}..." if len(commit_msg) > 40 else f"🔨 {commit_msg}"
        
        # Add commit node
        G.add_node(commit_node, color='lightcoral')
        
        # Get changed files
        files_changed = list(commit.stats.files.keys())
        
        # Add edges from commit to files
        for file in files_changed:
            G.add_node(file, color='lightblue')  # ensure file node exists
            G.add_edge(commit_node, file)        # edge from commit to file

    # Get node colors from attributes
    node_colors = [G.nodes[n].get('color', 'lightgray') for n in G.nodes()]

    # Draw the graph
    pos = nx.spring_layout(G, k=0.7, seed=42)
    plt.figure(figsize=(12, 10))
    nx.draw(G, pos, with_labels=True, node_size=2500, node_color=node_colors,
            font_size=9, font_weight='bold', edge_color='gray', arrows=True)

    plt.title("Git Commit Tree (Commits → Files Changed)", fontsize=14)
    plt.show()

except Exception as e:
    print("❌ Not a Git repository or error occurred.")
    print(str(e))
