import os
import sys
from git import Repo
from graphviz import Digraph

def fetch_commit_graph(repo_path, num_commits=10):
    try:
        repo = Repo(repo_path)
        if repo.bare:
            raise ValueError("Repository is bare")
    except Exception as e:
        print(f"Error: {e}")
        return

    graph = Digraph(format="png", engine="dot")

    commits_added = 0
    for commit in repo.iter_commits('HEAD', max_count=num_commits):
        if commits_added >= num_commits:
            break
        if commit.message.startswith("Merge"):
            continue

        message = commit.message.strip().split('\n')[0][:40]  # Use first 40 chars of the message
        sanitized_message = message.replace("'", "").replace('"', "").replace("//", "_").replace(":", "_")
        sanitized_message = sanitized_message.replace(" ", "_")

        graph.node(sanitized_message, message, fillcolor='lightcoral', shape='ellipse', style='filled')

        # Add parent commit edge
        parents = commit.parents
        if parents:
            parent_msg = parents[0].message.strip().split('\n')[0][:40]
            sanitized_parent_msg = parent_msg.replace("'", "").replace('"', "").replace("//", "_").replace(":", "_")
            sanitized_parent_msg = sanitized_parent_msg.replace(" ", "_")
            graph.edge(sanitized_parent_msg, sanitized_message)

        commits_added += 1

    # Save the commit graph to a .ps file
    output_dir = os.path.join(repo_path, 'commit_graph')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_ps_file = os.path.join(output_dir, 'commit_history.ps')
    try:
        graph.render(output_ps_file, format='ps', cleanup=True)
        print(f"Commit graph generated: {output_ps_file}.ps")
    except Exception as e:
        print(f"Error generating commit graph: {e}")

if __name__ == "__main__":
    repo_path = sys.argv[1]  # Get repo path from the argument
    num_commits = int(sys.argv[2]) if len(sys.argv) > 2 else 10  # Default to 10 if no number is provided
    fetch_commit_graph(repo_path, num_commits)
