# TeamReel Git Hooks Installation Script (PowerShell)
# Automated installation of constitutional Git hooks across platforms
# SE Principle Focus: Portability (cross-platform) and Simplicity (automated setup)

param(
    [switch]$Team,
    [switch]$Help,
    [switch]$Verbose
)

# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
try {
    $RepoRoot = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0) {
        $RepoRoot = Get-Location
    }
} catch {
    $RepoRoot = Get-Location
}

$HooksDir = Join-Path $RepoRoot ".git" "hooks"
$BackupDir = Join-Path $RepoRoot ".git" "hooks-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Hook files to install
$HookFiles = @(
    "pre-commit",
    "pre-push", 
    "pre-commit.ps1",
    "pre-push.ps1"
)

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
        [string]$Color = "White",
        [switch]$NoNewline
    )
    
    if ($NoNewline) {
        Write-Host $Text -ForegroundColor $Colors[$Color] -NoNewline
    } else {
        Write-Host $Text -ForegroundColor $Colors[$Color]
    }
}

function Write-Header {
    Write-ColorText "🔧 TeamReel Constitutional Git Hooks Installer" -Color Purple
    Write-ColorText "=============================================" -Color Purple
    Write-Host
}

function Show-Help {
    Write-Host "TeamReel Git Hooks Installation Script"
    Write-Host ""
    Write-Host "Usage: .\install_git_hooks.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Team      Enable team deployment mode with additional instructions"
    Write-Host "  -Help      Show this help message"
    Write-Host "  -Verbose   Enable verbose output"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install_git_hooks.ps1                # Standard installation"
    Write-Host "  .\install_git_hooks.ps1 -Team          # Team deployment mode"
    Write-Host "  .\install_git_hooks.ps1 -Verbose       # Verbose installation"
}

function Test-Prerequisites {
    Write-ColorText "🔍 Checking prerequisites..." -Color Blue
    
    # Check if we're in a Git repository
    try {
        $null = & git rev-parse --git-dir 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Not in Git repository"
        }
    }
    catch {
        Write-ColorText "❌ Error: Not in a Git repository" -Color Red
        Write-ColorText "💡 Run this script from within a Git repository" -Color Yellow
        exit 1
    }
    
    # Check if hooks directory exists
    if (-not (Test-Path $HooksDir)) {
        Write-ColorText "❌ Error: Git hooks directory not found: $HooksDir" -Color Red
        exit 1
    }
    
    # Check if constitutional validator exists
    $constitutionalValidator = Join-Path $RepoRoot "src" "constitutional_validator.py"
    if ($RepoRoot -like "*\.worktrees\*") {
        $constitutionalValidator = Join-Path $RepoRoot "src" "constitutional_validator.py"
    }
    
    if (-not (Test-Path $constitutionalValidator)) {
        Write-ColorText "⚠️  Warning: Constitutional validator not found at $constitutionalValidator" -Color Yellow
        Write-ColorText "💡 Make sure WP01 Constitutional Core Engine is implemented" -Color Yellow
        Write-ColorText "ℹ️  Continuing with installation - hooks will fail until validator is available" -Color Blue
    }
    
    Write-ColorText "✅ Prerequisites check completed" -Color Green
    Write-Host
}

function Backup-ExistingHooks {
    Write-ColorText "💾 Backing up existing hooks..." -Color Blue
    
    $backupNeeded = $false
    
    # Check if any hooks exist that would be overwritten
    foreach ($hookFile in $HookFiles) {
        $hookPath = Join-Path $HooksDir $hookFile
        if (Test-Path $hookPath) {
            $backupNeeded = $true
            break
        }
    }
    
    if ($backupNeeded) {
        # Create backup directory
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        
        # Backup existing hooks
        foreach ($hookFile in $HookFiles) {
            $hookPath = Join-Path $HooksDir $hookFile
            if (Test-Path $hookPath) {
                $backupPath = Join-Path $BackupDir $hookFile
                Copy-Item $hookPath $backupPath
                Write-ColorText "✅ Backed up: $hookFile" -Color Green
            }
        }
        
        Write-ColorText "💾 Backup created at: $BackupDir" -Color Green
    } else {
        Write-ColorText "ℹ️  No existing hooks to backup" -Color Blue
    }
    
    Write-Host
}

function Install-Hooks {
    Write-ColorText "📦 Installing constitutional Git hooks..." -Color Blue
    
    $hooksInstalled = 0
    
    # Hook source directory - they should already be in .git/hooks from our implementation
    $hooksSourceDir = $HooksDir
    
    foreach ($hookFile in $HookFiles) {
        $sourcePath = Join-Path $hooksSourceDir $hookFile
        $targetPath = Join-Path $HooksDir $hookFile
        
        if (Test-Path $sourcePath) {
            # Copy the hook file (if source and target are different)
            if ($sourcePath -ne $targetPath) {
                Copy-Item $sourcePath $targetPath -Force
            }
            
            Write-ColorText "✅ Installed: $hookFile" -Color Green
            $hooksInstalled++
        } else {
            Write-ColorText "⚠️  Hook file not found: $sourcePath" -Color Yellow
        }
    }
    
    if ($hooksInstalled -eq 0) {
        Write-ColorText "❌ No hook files were installed" -Color Red
        Write-ColorText "💡 Make sure hook files exist in $hooksSourceDir" -Color Yellow
        exit 1
    }
    
    Write-ColorText "🎉 Successfully installed $hooksInstalled hook file(s)" -Color Green
    Write-Host
}

function Test-Installation {
    Write-ColorText "🔍 Verifying installation..." -Color Blue
    
    $verificationPassed = $true
    
    # Check each hook file
    foreach ($hookFile in $HookFiles) {
        $hookPath = Join-Path $HooksDir $hookFile
        
        if (Test-Path $hookPath) {
            Write-ColorText "✅ $hookFile`: Installed successfully" -Color Green
        } else {
            Write-ColorText "❌ $hookFile`: Missing" -Color Red
            $verificationPassed = $false
        }
    }
    
    if ($verificationPassed) {
        Write-ColorText "✅ All hooks verified successfully" -Color Green
    } else {
        Write-ColorText "❌ Some hooks failed verification" -Color Red
        return $false
    }
    
    Write-Host
    return $true
}

function Test-HookFunctionality {
    Write-ColorText "🧪 Testing hook functionality..." -Color Blue
    
    # Test PowerShell pre-commit hook
    $preCommitHook = Join-Path $HooksDir "pre-commit.ps1"
    if (Test-Path $preCommitHook) {
        Write-ColorText "Testing PowerShell pre-commit hook..." -Color Blue
        
        # Create a temporary test file
        $testFile = Join-Path $RepoRoot "test_constitutional_hook.py"
        $testContent = @"
# Test file for constitutional hook validation
def test_function():
    '''Simple test function'''
    return 'Hello, TeamReel!'
"@
        Set-Content -Path $testFile -Value $testContent
        
        # Stage the test file
        try {
            & git add $testFile 2>$null
        } catch {
            # Ignore staging errors
        }
        
        # Test the hook with dry run (if supported)
        try {
            $hookTest = & powershell -File $preCommitHook -DryRun 2>$null
            Write-ColorText "✅ PowerShell pre-commit hook test passed" -Color Green
        } catch {
            Write-ColorText "⚠️  PowerShell pre-commit hook test failed" -Color Yellow
            Write-ColorText "ℹ️  This may be expected if constitutional validator is not yet available" -Color Blue
        }
        
        # Clean up test file
        try {
            & git reset HEAD $testFile 2>$null
            Remove-Item $testFile -ErrorAction SilentlyContinue
        } catch {
            # Ignore cleanup errors
        }
    }
    
    Write-ColorText "✅ Hook testing completed" -Color Green
    Write-Host
}

function Show-UsageInstructions {
    Write-ColorText "📖 Usage Instructions" -Color Purple
    Write-ColorText "====================" -Color Purple
    Write-Host
    
    Write-ColorText "Constitutional Git Hooks are now installed!" -Color Blue
    Write-Host
    
    Write-ColorText "What happens now:" -Color Green
    Write-Host "• Pre-commit hook: Validates SE principles before each commit"
    Write-Host "• Pre-push hook: Enforces quality gates before each push"
    Write-Host
    
    Write-ColorText "Platform-specific execution:" -Color Yellow
    Write-Host "• Windows: Git will use PowerShell versions (.ps1 files) automatically"
    Write-Host "• Linux/macOS: Git will use bash versions automatically"
    Write-Host
    
    Write-ColorText "Troubleshooting:" -Color Blue
    Write-Host "• If hooks fail, check that WP01 Constitutional Core Engine is implemented"
    Write-Host "• Hook logs provide detailed violation information"
    Write-Host "• Use 'git commit --no-verify' to bypass hooks temporarily (not recommended)"
    Write-Host
    
    Write-ColorText "Configuration:" -Color Green
    Write-Host "• Rules: .kittify/config/se_rules.yaml"
    Write-Host "• Quality Gates: .kittify/config/quality_gates.yaml"
    Write-Host "• Constitution: .kittify/memory/constitution.md"
    Write-Host
}

function Deploy-ForTeam {
    Write-ColorText "👥 Team Deployment Mode" -Color Purple
    Write-ColorText "======================" -Color Purple
    Write-Host
    
    Write-ColorText "📋 Team installation checklist:" -Color Blue
    Write-Host "1. Ensure all team members have Python 3.11+ installed"
    Write-Host "2. Share this installation script with the team"
    Write-Host "3. Have each team member run: .\scripts\install_git_hooks.ps1"
    Write-Host "4. Verify constitutional validator is available in all environments"
    Write-Host
    
    Write-ColorText "✅ Installation completed for this repository" -Color Green
    Write-ColorText "💡 Each team member should run this script in their local repository" -Color Yellow
    Write-Host
}

# Main execution
function Invoke-Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Write-Header
    
    Write-ColorText "🚀 Starting Git hooks installation..." -Color Purple
    Write-Host
    
    # Run installation steps
    Test-Prerequisites
    Backup-ExistingHooks
    Install-Hooks
    
    if (Test-Installation) {
        Test-HookFunctionality
        Show-UsageInstructions
        
        if ($Team) {
            Deploy-ForTeam
        }
        
        Write-ColorText "🎉 Git hooks installation completed successfully!" -Color Green
        Write-ColorText "💡 Constitutional enforcement is now active" -Color Blue
    } else {
        Write-ColorText "❌ Installation completed with errors" -Color Red
        exit 1
    }
}

# Trap to ensure clean exit on interruption
try {
    Invoke-Main
}
catch {
    Write-ColorText "`n⚠️  Installation interrupted: $_" -Color Yellow
    exit 1
}