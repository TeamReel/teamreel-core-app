# TeamReel Constitutional Pre-commit Hook (PowerShell)
# Validates SE principles before allowing commits
# SE Principle Focus: Defensibility (secure git operations) and Simplicity (fast feedback)

param(
    [switch]$DryRun
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

function Test-ConstitutionalValidator {
    param([string]$PythonCmd)
    
    if (-not (Test-Path $ConstitutionalValidator)) {
        Write-ColorText "❌ Error: Constitutional validator not found at $ConstitutionalValidator" -Color Red
        Write-ColorText "💡 Make sure WP01 Constitutional Core Engine is implemented" -Color Yellow
        exit 1
    }
    
    # Test if the validator can be imported
    $testScript = @"
import sys
import os
sys.path.insert(0, r'$RepoRoot')
try:
    from src.constitutional_validator import ConstitutionalValidator
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@
    
    $result = & $PythonCmd -c $testScript 2>&1
    if ($LASTEXITCODE -ne 0 -or $result -ne "OK") {
        Write-ColorText "❌ Error: Constitutional validator cannot be imported" -Color Red
        Write-ColorText "💡 Check Python dependencies and module structure" -Color Yellow
        exit 1
    }
}

function Get-StagedFiles {
    # Get all staged files, excluding deleted files
    $stagedFiles = & git diff --cached --name-only --diff-filter=ACM 2>$null
    if ($LASTEXITCODE -eq 0) {
        return $stagedFiles | Where-Object { $_ -and $_.Trim() }
    }
    return @()
}

function Invoke-ConstitutionalValidation {
    param(
        [string]$PythonCmd,
        [string[]]$StagedFiles
    )
    
    if ($StagedFiles.Count -eq 0) {
        Write-ColorText "No staged files to validate" -Color Blue
        return $true
    }
    
    Write-ColorText "🔍 Running constitutional validation on $($StagedFiles.Count) staged file(s)..." -Color Blue
    
    # Create temporary validation script
    $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
    
    $validationScript = @"
import sys
import os
sys.path.insert(0, r'$RepoRoot')

from src.constitutional_validator import ConstitutionalValidator
from src.git_reporter import GitViolationReporter, GitReportFormat

def main():
    # Initialize validator and reporter
    try:
        validator = ConstitutionalValidator()
        reporter = GitViolationReporter(GitReportFormat.TERMINAL)
    except Exception as e:
        print(f'❌ Error initializing validator: {e}')
        return 1
    
    # Get staged files from command line args
    staged_files = sys.argv[1:]
    
    if not staged_files:
        print('ℹ️  No files to validate')
        return 0
    
    # Validate each staged file
    violations_found = False
    for file_path in staged_files:
        if os.path.exists(file_path):
            try:
                # Run validation
                result = validator.validate_file(file_path)
                
                if result.violations:
                    violations_found = True
                    # Report violations using git reporter
                    reporter.report_file_violations(file_path, result.violations)
                    
            except Exception as e:
                print(f'⚠️  Warning: Could not validate {file_path}: {e}')
    
    if violations_found:
        print('\n❌ Constitutional violations detected. Commit blocked.')
        print('💡 Fix the violations above and try committing again.')
        return 1
    else:
        print('✅ Constitutional validation passed')
        return 0

if __name__ == '__main__':
    sys.exit(main())
"@
    
    Set-Content -Path $tempScript -Value $validationScript -Encoding UTF8
    
    try {
        # Convert PowerShell array to individual arguments
        $fileArgs = @()
        foreach ($file in $StagedFiles) {
            $fileArgs += $file
        }
        
        # Run validation
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
    Write-ColorText "🏛️  TeamReel Constitutional Pre-commit Hook" -Color Blue
    Write-ColorText "==================================" -Color Blue
    
    # Perform prerequisite checks
    $pythonCmd = Test-Python
    Test-ConstitutionalValidator -PythonCmd $pythonCmd
    
    # Get staged files
    $stagedFiles = Get-StagedFiles
    
    # Run constitutional validation
    if (Invoke-ConstitutionalValidation -PythonCmd $pythonCmd -StagedFiles $stagedFiles) {
        Write-ColorText "🎉 Pre-commit validation completed successfully" -Color Green
        exit 0
    } else {
        Write-ColorText "💥 Pre-commit validation failed" -Color Red
        exit 1
    }
}

# Execute main function
Main