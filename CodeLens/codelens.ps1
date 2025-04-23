param (
    [string]$Command,
    [string]$Arg1,
    [string]$CommitNumber
)

$ValidUserTypes = @("novice", "senior", "client")

function ShowRecentCommits {
    $commits = git log -n 10 --pretty=format:"%h %s"
    if (-not $commits) {
        Write-Host "Error: Couldn't fetch Git commits"
        exit 1
    }

    $i = 1
    foreach ($line in $commits) {
        Write-Host "$i. $line"
        $i++
    }

    Write-Host "`nTo document a commit, run:"
    Write-Host "  codelens generate novice {commit_hash}"
}

function GenerateDocumentationFromCommit {
    if (-not $CommitNumber) {
        Write-Host "Usage: codelens generate novice {commit_hash}"
        exit 1
    }

    $RepoRoot = git rev-parse --show-toplevel 2>$null
    if (-not $RepoRoot) {
        Write-Host "Error: Cannot find GitHub repo."
        exit 1
    }

    $GitHubUrl = git config --get remote.origin.url
    if (-not $GitHubUrl) {
        Write-Host "Error: No GitHub remote URL found"
        exit 1
    }

    $GitHubUrl = $GitHubUrl -replace "^git@github.com:", "https://github.com/" -replace "\.git$", ""

    $CodeLensPath = $env:CODELENS_PATH
    if (-not $CodeLensPath) {
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    $ScriptPath = Join-Path $CodeLensPath "track_commit_files.py"
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "Error: Required script not found: $ScriptPath"
        exit 1
    }

    py $ScriptPath $CommitNumber $RepoRoot $Arg1 $CodeLensPath

    Write-Host "Documentation generation triggered for commit $CommitNumber"
}

function GenerateCommitMessage {
    $CodeLensPath = $env:CODELENS_PATH
    if (-not $CodeLensPath) {
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    $CommitScript = Join-Path -Path $CodeLensPath -ChildPath "commit_msg_generation.py"
    if (-not (Test-Path $CommitScript)) {
        Write-Host "Error: commit_msg_generation.py not found at $CommitScript"
        exit 1
    }

    $CommitMessage = py $CommitScript --generate-only
    if (-not $CommitMessage -or $CommitMessage.Trim() -eq "") {
        Write-Host "Commit message could not be generated."
        exit 1
    }

    return $CommitMessage
}

switch ($Command) {
    "generate" {
        if ($Arg1 -and $CommitNumber) {
            GenerateDocumentationFromCommit
        }
        elseif (-not $Arg1) {
            Write-Host "Usage: codelens generate {user_type}"
            Write-Host "Usage: codelens generate {user_type} {commit_hash}"
            exit 1
        }
        elseif ($Arg1 -notin $ValidUserTypes) {
            Write-Host "Error: Invalid user type. Valid options are 'novice','senior','client'."
            exit 1
        }
        else {
            $RepoRoot = git rev-parse --show-toplevel 2>$null
            if (-not $RepoRoot) {
                Write-Host "Error: Cannot find GitHub repo."
                exit 1
            }

            $GitHubUrl = git config --get remote.origin.url
            if (-not $GitHubUrl) {
                Write-Host "Error: No GitHub remote URL found"
                exit 1
            }

            $GitHubUrl = $GitHubUrl -replace "^git@github.com:", "https://github.com/" -replace "\.git$", ""

            $CodeLensPath = $env:CODELENS_PATH
            if (-not $CodeLensPath) {
                Write-Host "Error: CODELENS_PATH environment variable not set"
                exit 1
            }

            $ScriptPath = Join-Path -Path $CodeLensPath -ChildPath "script.py"
            if (-not (Test-Path $ScriptPath)) {
                Write-Host "Error: Script.py not found at $ScriptPath"
                exit 1
            }

            py $ScriptPath $GitHubUrl $RepoRoot $CodeLensPath $Arg1
            Write-Host "Command completed!"
        }
    }

    "regenerate" {
        ShowRecentCommits
    }

    "commentify" {
        if (-not $Arg1) {
            Write-Host "Usage: codelens commentify {file_name}"
            exit 1
        }

        $CodeLensPath = $env:CODELENS_PATH
        if (-not $CodeLensPath) {
            Write-Host "Error: CODELENS_PATH environment variable not set"
            exit 1
        }

        $CommentScript = Join-Path -Path $CodeLensPath -ChildPath "commentify.py"
        if (-not (Test-Path $CommentScript)) {
            Write-Host "Error: commentify.py not found at $CommentScript"
            exit 1
        }

        py $CommentScript $Arg1
        Write-Host "Commentify command completed!"
    }

    "commit" {
        $CommitMessage = GenerateCommitMessage
        Write-Host "`nGenerated Commit Message:"
        Write-Host $CommitMessage

        git add .
        git commit -m "$CommitMessage"
        Write-Host "Commit completed!"
    }

    "drawgraph" {
        $RepoRoot = git rev-parse --show-toplevel 2>$null
        if (-not $RepoRoot) {
            Write-Host "Error: Cannot find GitHub repo."
            exit 1
        }

        $CommitMessage = GenerateCommitMessage
        Write-Host "`nGenerated Commit Message:"
        Write-Host $CommitMessage

        git commit -a -m "$CommitMessage"

        $CodeLensPath = $env:CODELENS_PATH
        $GraphScript = Join-Path -Path $CodeLensPath -ChildPath "draw_graph.py"
        if (-not (Test-Path $GraphScript)) {
            Write-Host "Error: draw_graph.py not found at $GraphScript"
            exit 1
        }

        py $GraphScript $RepoRoot
        Write-Host "Function call graph generation triggered!"
    }

    Default {
        Write-Host "Usage:"
        Write-Host "  codelens generate {user_type}"
        Write-Host "  codelens generate {user_type} {commit_hash}"
        Write-Host "  codelens regenerate"
        Write-Host "  codelens commentify {file_path}"
        Write-Host "  codelens drawgraph"
        Write-Host "  codelens commit"
        exit 1
    }
}
