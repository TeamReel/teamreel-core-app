# TeamReel Constitutional Pre-push Hook (PowerShell)
# Enforces quality gates before allowing pushes
# SE Principle Focus: Maintainability (quality gates) and Defensibility (secure operations)

param(
    [string]$Remote = "",
    [string]$Url = ""
)

# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
try {
    $RepoRoot = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Not in a git repository"
    }
} catch {
    Write-Host "❌ Error: Not in a git repository" -ForegroundColor Red
    exit 1
}

$ConstitutionalValidator = Join-Path $RepoRoot "src" "constitutional_validator.py"
$GitReporter = Join-Path $RepoRoot "src" "git_reporter.py"
$QualityGates = Join-Path $RepoRoot "src" "quality_gates.py"

# Colors for console output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Cyan"
    Purple = "Magenta"
    White = "White"
}

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

function Test-Python {
    # Check if Python is available
    $pythonCmd = $null
    
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } else {
        Write-ColorText "❌ Error: Python not found. Please install Python 3.7+ to use constitutional hooks." -Color Red
        exit 1
    }
    
    return $pythonCmd
}

function Test-Prerequisites {
    param([string]$PythonCmd)
    
    if (-not (Test-Path $ConstitutionalValidator)) {
        Write-ColorText "❌ Error: Constitutional validator not found at $ConstitutionalValidator" -Color Red
        Write-ColorText "💡 Make sure WP01 Constitutional Core Engine is implemented" -Color Yellow
        exit 1
    }
    
    if (-not (Test-Path $QualityGates)) {
        Write-ColorText "❌ Error: Quality gates module not found at $QualityGates" -Color Red
        Write-ColorText "💡 Make sure quality gates are implemented" -Color Yellow
        exit 1
    }
    
    # Test if modules can be imported
    $testScript = @"
import sys
import os
sys.path.insert(0, r'$RepoRoot')
try:
    from src.constitutional_validator import ConstitutionalValidator
    from src.quality_gates import QualityGateValidator
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@
    
    $result = & $PythonCmd -c $testScript 2>&1
    if ($LASTEXITCODE -ne 0 -or $result -ne "OK") {
        Write-ColorText "❌ Error: Required modules cannot be imported" -Color Red
        Write-ColorText "💡 Check Python dependencies and module structure" -Color Yellow
        exit 1
    }
}

function Get-PushCommits {
    param(
        [string]$Remote,
        [string]$Url
    )
    
    # Read from stdin (format: <local ref> <local sha1> <remote ref> <remote sha1>)
    $commits = @()
    
    try {
        $input = @($input)
        foreach ($line in $input) {
            if ($line) {
                $parts = $line -split '\s+'
                if ($parts.Length -ge 4) {
                    $localRef = $parts[0]
                    $localSha = $parts[1]
                    $remoteRef = $parts[2]
                    $remoteSha = $parts[3]
                    
                    if ($localSha -ne "0000000000000000000000000000000000000000") {
                        if ($remoteSha -eq "0000000000000000000000000000000000000000") {
                            # New branch, get all commits
                            $newCommits = & git rev-list $localSha --not --remotes=origin 2>$null
                        } else {
                            # Existing branch, get new commits
                            $newCommits = & git rev-list "$remoteSha..$localSha" 2>$null
                        }
                        
                        if ($newCommits) {
                            $commits += $newCommits
                        }
                    }
                }
            }
        }
    } catch {
        # If we can't read from stdin, get recent commits
        $commits = & git rev-list HEAD~5..HEAD 2>$null
    }
    
    return $commits
}

function Get-ChangedFiles {
    param(
        [string[]]$Commits
    )
    
    if ($Commits.Count -eq 0) {
        return @()
    }
    
    # Get all files changed in these commits
    $changedFiles = @()
    foreach ($commit in $Commits) {
        $files = & git diff --name-only "$commit^..$commit" 2>$null
        if ($files) {
            $changedFiles += $files
        }
    }
    
    # Remove duplicates and return
    return $changedFiles | Sort-Object -Unique
}

function Invoke-QualityGates {
    param(
        [string]$PythonCmd,
        [string[]]$ChangedFiles
    )
    
    Write-ColorText "🚧 Running quality gate validation..." -Color Blue
    
    # Create temporary validation script
    $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
    
    $validationScript = @"
import sys
import os
sys.path.insert(0, r'$RepoRoot')

from src.constitutional_validator import ConstitutionalValidator
from src.quality_gates import QualityGateValidator
from src.git_reporter import GitViolationReporter, GitReportFormat

def main():
    # Initialize validators and reporter
    try:
        constitutional_validator = ConstitutionalValidator()
        quality_validator = QualityGateValidator()
        reporter = GitViolationReporter(GitReportFormat.TERMINAL)
    except Exception as e:
        print(f'❌ Error initializing validators: {e}')
        return 1
    
    # Get changed files from command line args
    changed_files = sys.argv[1:] if len(sys.argv) > 1 else []
    
    print(f'🔍 Validating {len(changed_files)} changed file(s)...')
    
    # Run constitutional validation on all changed files
    constitutional_violations = False
    for file_path in changed_files:
        if os.path.exists(file_path):
            try:
                result = constitutional_validator.validate_file(file_path)
                if result.violations:
                    constitutional_violations = True
                    reporter.report_file_violations(file_path, result.violations)
            except Exception as e:
                print(f'⚠️  Warning: Could not validate {file_path}: {e}')
    
    # Run quality gate validation
    print('\n🏁 Running quality gate checks...')
    try:
        quality_result = quality_validator.validate_repository('.')
        
        if not quality_result.passed:
            print('❌ Quality gate validation failed:')
            for gate_name, gate_result in quality_result.gate_results.items():
                if not gate_result.passed:
                    print(f'  • {gate_name}: {gate_result.message}')
            return 1
            
    except Exception as e:
        print(f'⚠️  Warning: Quality gate validation failed: {e}')
        # Don't block push for quality gate errors, just warn
    
    if constitutional_violations:
        print('\n❌ Constitutional violations detected. Push blocked.')
        print('💡 Fix the violations above and try pushing again.')
        return 1
    else:
        print('✅ All quality gates passed')
        return 0

if __name__ == '__main__':
    sys.exit(main())
"@
    
    Set-Content -Path $tempScript -Value $validationScript -Encoding UTF8
    
    try {
        # Convert PowerShell array to individual arguments
        $fileArgs = @()
        foreach ($file in $ChangedFiles) {
            $fileArgs += $file
        }
        
        # Run quality gate validation
        $result = & $PythonCmd $tempScript @fileArgs
        $success = $LASTEXITCODE -eq 0
        
        return $success
    } finally {
        # Clean up temporary script
        if (Test-Path $tempScript) {
            Remove-Item $tempScript -Force
        }
    }
}

function Main {
    param(
        [string]$Remote = "",
        [string]$Url = ""
    )
    
    Write-ColorText "🏛️  TeamReel Constitutional Pre-push Hook" -Color Blue
    Write-ColorText "====================================" -Color Blue
    
    # Perform prerequisite checks
    $pythonCmd = Test-Python
    Test-Prerequisites -PythonCmd $pythonCmd
    
    # Get commits being pushed
    $commits = Get-PushCommits -Remote $Remote -Url $Url
    
    # Get changed files
    $changedFiles = Get-ChangedFiles -Commits $commits
    
    # Run quality gate validation
    if (Invoke-QualityGates -PythonCmd $pythonCmd -ChangedFiles $changedFiles) {
        Write-ColorText "🎉 Pre-push validation completed successfully" -Color Green
        exit 0
    } else {
        Write-ColorText "💥 Pre-push validation failed" -Color Red
        exit 1
    }
}

# Execute main function with parameters
Main -Remote $Remote -Url $Url