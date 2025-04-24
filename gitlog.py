import os
import textwrap
from git import Repo
from graphviz import Digraph

# Setup paths
repo_path = os.getcwd()
output_file = "commit_graph"

try:
    repo = Repo(repo_path, search_parent_directories=True)
    git_root = repo.git.rev_parse("--show-toplevel")

    # Create directed Graphviz graph with spread layout and high resolution
    dot = Digraph(format='png')
    dot.attr(rankdir='TB', dpi='600')  # TB = top to bottom layout
    dot.attr('graph', ranksep='1.5', nodesep='1')  # spacing between nodes
    dot.attr('node', style='filled', fontname='Arial', fontsize='12',
             width='2', height='1', fixedsize='false')

    # Get latest 10 non-merge commits
    non_merge_commits = []
    for commit in repo.iter_commits():
        if len(commit.parents) <= 1:
            non_merge_commits.append(commit)
        if len(non_merge_commits) >= 5:
            break

    for i, commit in enumerate(non_merge_commits):
        commit_msg = commit.message.strip()
        wrapped_msg = '\n'.join(textwrap.wrap(commit_msg, width=30))
        commit_node_id = f"commit{i}"

        # Commit node (red)
        dot.node(commit_node_id, f"🔨 {wrapped_msg}", fillcolor='lightcoral', shape='ellipse')

        # Files changed (blue boxes)
        for file in commit.stats.files.keys():
            file_node_id = f"{commit_node_id}_{file}"
            dot.node(file_node_id, file, fillcolor='lightblue', shape='box')
            dot.edge(commit_node_id, file_node_id)

    # Render high-quality PNG with Cairo
    dot.render(output_file, format='png', renderer='cairo', cleanup=True)
    print(f"✅ High-quality commit graph saved as {output_file}.png")

except Exception as e:
    print("❌ Not a Git repository or error occurred.")
    print(str(e))
