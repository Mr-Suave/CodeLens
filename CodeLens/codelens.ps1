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

function FindBug { 
    $Description = $Arg1
    $SuspectsJson = $Arg2

    if(-not $Description -or -not $SuspectsJson){
        Write-Host "Usage: codelens findbug {description_string} {suspect_functions_json}"
        exit 1
    }

    $CodeLensPath = $env:CODELENS_PATH
    if (-not $CodeLensPath) {
        Write-Host "Error: CODELENS_PATH environment variable not set"
        exit 1
    }

    $ScriptPath = Join-Path $CodeLensPath "draw_graph.py"
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "Error: findbug.py not found at $ScriptPath"
        exit 1
    }

    # Call Python script with bug description and suspects
    py $ScriptPath "`"$Description`"" "`"$SuspectsJson`"" $CodeLensPath

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
elseif ($Command -eq "findbug") {
    FindBug
}
else{
    Write-Host "Usage:"
    Write-Host "  codelens generate {user_type}"
    Write-Host "  codelens commentify {file_path}"
    Write-Host "  codelens generate {user_type} {commit_hash}"
    Write-Host "  codelens regenerate"
    Write-Host "  codelens findbug {description_string} {suspect_functions_json}"
    Write-Host "  Ex: codelens findbug `"App crashes when uploading image`" '[`"uploadImage`", `"handleImageInput`", `"sendToServer`"]'"
    exit 1
}
