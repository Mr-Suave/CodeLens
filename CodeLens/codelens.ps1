param (
    [string]$Command,
    [string]$FileName
)

if($Command -eq "generate"){
    # Check if in a Git repository
    $RepoRoot = git rev-parse --show-toplevel 2>$null
    if (-not $RepoRoot) {
        Write-Host "Error: Cannot find GitHub repo."
        exit 1
    }

    # Get GitHub URL
    $GitHubUrl = git config --get remote.origin.url
    if (-not $GitHubUrl) {
        Write-Host "Error: No GitHub remote URL found"
        exit 1
    }

    # Convert SSH URL to HTTPS (if needed)
    $GitHubUrl = $GitHubUrl -replace "^git@github.com:", "https://github.com/" -replace "\.git$", ""

    # Check for CODELENS_PATH environment variable
    $CodeLensPath = $env:CODELENS_PATH
    if (-not $CodeLensPath) {
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    # Verify if Script.py exists
    $ScriptPath = Join-Path -Path $CodeLensPath -ChildPath "script.py"
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "Error: Script.py not found at $ScriptPath"
        exit 1
    }

    # Call the Python script with GitHub URL and Repo Root
    py $ScriptPath $GitHubUrl $RepoRoot $CodeLensPath

    Write-Host "Command completed!"
}
elseif($Command -eq "commentify"){
    if(-not $FileName){
        Write-Host "Usage: codelens commentify {file_name}"
        exit 1
    }

    # Check for CODELENS_PATH environmental variable
    $CodeLensPath = $env:CODELENS_PATH
    if(-not $CodeLensPath){
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    # Path to commentify.py
    $CommentScript= Join-Path -Path $CodeLensPath -ChildPath "commentify.py"
    if(-not (Test-Path $CommentScript)){
        Write-Host "Error: commentify.py not found at $CommentScript"
        exit 1
    }

    # Call the commentify script
    py $CommentScript $FileName

    Write-Host "Commentify command completed!"
}
elseif ($Command -eq "commit") {
    # Check for CODELENS_PATH environment variable
    $CodeLensPath = $env:CODELENS_PATH
    if (-not $CodeLensPath) {
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    # Path to commit message generation script
    $CommitScript = Join-Path -Path $CodeLensPath -ChildPath "commit_msg_generation.py"
    if (-not (Test-Path $CommitScript)) {
        Write-Host "Error: commit_generation_file.py not found at $CommitScript"
        exit 1
    }

    # Call the script and capture the commit message
    $CommitMessage = py $CommitScript --generate-only

    if (-not $CommitMessage -or $CommitMessage.Trim() -eq "") {
        Write-Host " Commit message could not be generated."
        exit 1
    }

    Write-Host "`n Generated Commit Message:"
    Write-Host $CommitMessage

    # Run the actual Git commit
    git commit -a -m "$CommitMessage"
}
else {
    Write-Host "Usage:"
    Write-Host "  codelens generate"
    Write-Host "  codelens commentify {file_name}"
    Write-Host "  codelens commit"
    exit 1
}
