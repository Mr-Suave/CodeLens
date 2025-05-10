param (
    [string]$Command,
    [string]$Arg1,
    [string]$Arg2
)
$ValidUserTypes = @("novice","senior","client")

function ShowRecentCommits{
    $commits = git log -n 10 --pretty=format:"%h %s"
    if(-not $commits){
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

function GenerateCommitGraph {
    # Get the repository root
    $RepoRoot = git rev-parse --show-toplevel 2>$null
    if (-not $RepoRoot) {
        Write-Host "Error: Cannot find GitHub repo."
        exit 1
    }

    # Get the GitHub remote URL
    $GitHubUrl = git config --get remote.origin.url
    if (-not $GitHubUrl) {
        Write-Host "Error: No GitHub remote URL found"
        exit 1
    }

    $GitHubUrl = $GitHubUrl -replace "^git@github.com:", "https://github.com/" -replace "\.git$", ""

    # Get the CODELENS_PATH environment variable
    $CodeLensPath = $env:CODELENS_PATH
    if (-not $CodeLensPath) {
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    # Path to the Python script
    $ScriptPath = Join-Path $CodeLensPath "github_commits.py"
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "Error: Required script not found: $ScriptPath"
        exit 1
    }

    # Run the Python script to generate the commit graph, passing the number of commits as an argument
    py $ScriptPath $RepoRoot $Arg1

    Write-Host "Commit graph generation triggered."
}

function GenerateDocumentationFromCommit {
    if (-not $Arg2) {
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

    py $ScriptPath $Arg2 $RepoRoot $Arg1 $CodeLensPath

    Write-Host "Documentation generation triggered for commit $Arg2"
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
function FindBug { 
    $Description = $Arg1
    $SuspectFunctions = $Arg2

    if(-not $Description -or -not $SuspectFunctions){
        Write-Host Write-Host "  Ex: codelens findbug `"App crashes when uploading image`" uploadImage handleImageInput sendToServer"
        exit 1
    }

    $CodeLensPath = $env:CODELENS_PATH
    if (-not $CodeLensPath) {
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    $RepoRoot = git rev-parse --show-toplevel 2>$null
    if (-not $RepoRoot) {
        Write-Host "Error: Cannot find GitHub repo."
        exit 1
    }

    $ScriptPath = Join-Path $CodeLensPath "fixbug.py"
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "Error: fixbug.py not found at $ScriptPath"
        exit 1
    }
    
    # Split the comma-separated function list
    $FunctionsList = $SuspectFunctions -split ',' | ForEach-Object { $_.Trim() }
    
    # Build the argument string for the Python script
    $FunctionsString = ($FunctionsList -join ',')

    $Arguments = @(
        "$RepoRoot"
        "--description", """$Description"""
        "--functions", """$FunctionsString"""
    )

    # Call Python script
    py $ScriptPath $Arguments

    Write-Host "Bug tracing initiated based on description and suspect functions..."
}
    
if ($Command -eq "generate" -and $Arg1 -and $Arg2){
    GenerateDocumentationFromCommit
}
elseif($Command -eq "generate"){
    if(-not $Arg1){
        Write-Host "Usage: codelens generate {user_type}"
        Write-Host "Usage: codelens generate {user_type} {commit_hash}"
        exit 1
    }

    # If user type not valid
    if($Arg1 -notin $ValidUserTypes){
        Write-Host "Error: Invalid user type. Valid options are 'novice','senior','client'."
        exit 1
    }

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
    py $ScriptPath $GitHubUrl $RepoRoot $CodeLensPath $Arg1

    Write-Host "Command completed!"
}
elseif($command -eq "regenerate"){
    ShowRecentCommits
}
elseif($Command -eq "commentify"){
    if(-not $Arg1){
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
    py $CommentScript $Arg1

    Write-Host "Commentify command completed!"
}
elseif($Command -eq "commit"){
    $CommitMessage = GenerateCommitMessage
    Write-Host "`nGenerated Commit Message:"
    Write-Host $CommitMessage

    git add .
    git commit -m "$CommitMessage"
    Write-Host "Commit completed!"

}
elseif ($Command -eq "findbug") {
    FindBug
}
elseif($Command -eq "commitgraph") {
    if (-not $Arg1){
        Write-Host "Error: Please specify the number of commits (N). Usage: codelens commitgraph N"
        exit 1  
    }
    # $NumCommits = [int]$Arg1
    GenerateCommitGraph
    # if (-not $NumCommits) {
    #     Write-Host "Error: Please specify the number of commits (N). Usage: codelens commitgraph N"
    #     exit 1
    # }
    
    # GenerateCommitGraph
}

else{
    Write-Host "WELCOME TO CODELENS - YOUR ONE STOP SOFTWARE DEVELOPMENT UTILITY. BE FAST. BE AMAZING. BE CODELENS."
    Write-Host "Usage:"
    Write-Host "  codelens generate {user_type}"
    Write-Host "  codelens commentify {file_path}"
    Write-Host "  codelens generate {user_type} {commit_hash}"
    Write-Host "  codelens regenerate"
    Write-Host "  codelens commit"
    Write-Host "  codelens findbug {description_string} {suspect_functions_list}"
    Write-Host "  Ex: codelens findbug `"App crashes when uploading image`" uploadImage,handleImageInput,sendToServer"
    Write-Host "  codelens commitgraph N"
    exit 1
}