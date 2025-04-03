param (
    [string]$Command
)

if ($Command -ne "generate") {
    Write-Host "This tool is created by Team 6 for the CodeLens project. Please use the 'generate' command to fulfill your wishes!"
    exit 1
}

# Check if in a Git repository
$RepoRoot = git rev-parse --show-toplevel 2>$null
if (-not $RepoRoot) {
    Write-Host "Error: Not in a Git repository"
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
$ScriptPath = Join-Path -Path $CodeLensPath -ChildPath "Script.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Host "Error: Script.py not found at $ScriptPath"
    exit 1
}

# Call the Python script with GitHub URL and Repo Root
py $ScriptPath $GitHubUrl $RepoRoot

Write-Host "Command completed!"
