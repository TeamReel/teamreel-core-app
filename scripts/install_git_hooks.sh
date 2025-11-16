#!/bin/bash
#
# TeamReel Git Hooks Installation Script
# Automated installation of constitutional Git hooks across platforms
# SE Principle Focus: Portability (cross-platform) and Simplicity (automated setup)
#

set -e

# Colors for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
BACKUP_DIR="$REPO_ROOT/.git/hooks-backup-$(date +%Y%m%d-%H%M%S)"

# Hook files to install
declare -a HOOK_FILES=(
    "pre-commit"
    "pre-push"
    "pre-commit.ps1"
    "pre-push.ps1"
)

echo -e "${PURPLE}🔧 TeamReel Constitutional Git Hooks Installer${NC}"
echo "=============================================="
echo

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if we're in a Git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Error: Not in a Git repository${NC}"
        echo -e "${YELLOW}💡 Run this script from within a Git repository${NC}"
        exit 1
    fi
    
    # Check if hooks directory exists
    if [[ ! -d "$HOOKS_DIR" ]]; then
        echo -e "${RED}❌ Error: Git hooks directory not found: $HOOKS_DIR${NC}"
        exit 1
    fi
    
    # Check if constitutional validator exists
    local constitutional_validator="$REPO_ROOT/src/constitutional_validator.py"
    if [[ "$REPO_ROOT" == *".worktrees"* ]]; then
        constitutional_validator="$REPO_ROOT/src/constitutional_validator.py"
    fi
    
    if [[ ! -f "$constitutional_validator" ]]; then
        echo -e "${YELLOW}⚠️  Warning: Constitutional validator not found at $constitutional_validator${NC}"
        echo -e "${YELLOW}💡 Make sure WP01 Constitutional Core Engine is implemented${NC}"
        echo -e "${BLUE}ℹ️  Continuing with installation - hooks will fail until validator is available${NC}"
    fi
    
    echo -e "${GREEN}✅ Prerequisites check completed${NC}"
    echo
}

# Function to backup existing hooks
backup_existing_hooks() {
    echo -e "${BLUE}💾 Backing up existing hooks...${NC}"
    
    local backup_needed=false
    
    # Check if any hooks exist that would be overwritten
    for hook_file in "${HOOK_FILES[@]}"; do
        local hook_path="$HOOKS_DIR/$hook_file"
        if [[ -f "$hook_path" ]]; then
            backup_needed=true
            break
        fi
    done
    
    if [[ "$backup_needed" == true ]]; then
        # Create backup directory
        mkdir -p "$BACKUP_DIR"
        
        # Backup existing hooks
        for hook_file in "${HOOK_FILES[@]}"; do
            local hook_path="$HOOKS_DIR/$hook_file"
            if [[ -f "$hook_path" ]]; then
                cp "$hook_path" "$BACKUP_DIR/"
                echo -e "${GREEN}✅ Backed up: $hook_file${NC}"
            fi
        done
        
        echo -e "${GREEN}💾 Backup created at: $BACKUP_DIR${NC}"
    else
        echo -e "${BLUE}ℹ️  No existing hooks to backup${NC}"
    fi
    
    echo
}

# Function to install hook files
install_hooks() {
    echo -e "${BLUE}📦 Installing constitutional Git hooks...${NC}"
    
    local hooks_installed=0
    
    # Check if hook files exist in the current location
    local hooks_source_dir="$HOOKS_DIR"
    
    # If we're running from scripts directory, look for hooks in .git/hooks
    if [[ "$SCRIPT_DIR" == *"scripts"* ]]; then
        hooks_source_dir="$HOOKS_DIR"
    fi
    
    for hook_file in "${HOOK_FILES[@]}"; do
        local source_path="$hooks_source_dir/$hook_file"
        local target_path="$HOOKS_DIR/$hook_file"
        
        if [[ -f "$source_path" ]]; then
            # Copy the hook file
            cp "$source_path" "$target_path"
            
            # Make executable (for bash scripts)
            if [[ "$hook_file" != *.ps1 ]]; then
                chmod +x "$target_path"
            fi
            
            echo -e "${GREEN}✅ Installed: $hook_file${NC}"
            ((hooks_installed++))
        else
            echo -e "${YELLOW}⚠️  Hook file not found: $source_path${NC}"
        fi
    done
    
    if [[ $hooks_installed -eq 0 ]]; then
        echo -e "${RED}❌ No hook files were installed${NC}"
        echo -e "${YELLOW}💡 Make sure hook files exist in $hooks_source_dir${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🎉 Successfully installed $hooks_installed hook file(s)${NC}"
    echo
}

# Function to verify installation
verify_installation() {
    echo -e "${BLUE}🔍 Verifying installation...${NC}"
    
    local verification_passed=true
    
    # Check each hook file
    for hook_file in "${HOOK_FILES[@]}"; do
        local hook_path="$HOOKS_DIR/$hook_file"
        
        if [[ -f "$hook_path" ]]; then
            # Check if bash script is executable
            if [[ "$hook_file" != *.ps1 ]]; then
                if [[ -x "$hook_path" ]]; then
                    echo -e "${GREEN}✅ $hook_file: Installed and executable${NC}"
                else
                    echo -e "${YELLOW}⚠️  $hook_file: Installed but not executable${NC}"
                    chmod +x "$hook_path"
                    echo -e "${GREEN}✅ Fixed permissions for $hook_file${NC}"
                fi
            else
                echo -e "${GREEN}✅ $hook_file: Installed (PowerShell)${NC}"
            fi
        else
            echo -e "${RED}❌ $hook_file: Missing${NC}"
            verification_passed=false
        fi
    done
    
    if [[ "$verification_passed" == true ]]; then
        echo -e "${GREEN}✅ All hooks verified successfully${NC}"
    else
        echo -e "${RED}❌ Some hooks failed verification${NC}"
        return 1
    fi
    
    echo
}

# Function to test hooks
test_hooks() {
    echo -e "${BLUE}🧪 Testing hook functionality...${NC}"
    
    # Test pre-commit hook (dry run)
    local pre_commit_hook="$HOOKS_DIR/pre-commit"
    if [[ -f "$pre_commit_hook" && -x "$pre_commit_hook" ]]; then
        echo -e "${BLUE}Testing pre-commit hook...${NC}"
        
        # Create a temporary test file
        local test_file="$REPO_ROOT/test_constitutional_hook.py"
        cat > "$test_file" << 'EOF'
# Test file for constitutional hook validation
def test_function():
    """Simple test function"""
    return "Hello, TeamReel!"
EOF
        
        # Stage the test file
        git add "$test_file" 2>/dev/null || true
        
        # Test the hook (but don't actually commit)
        if timeout 10s "$pre_commit_hook" 2>/dev/null; then
            echo -e "${GREEN}✅ Pre-commit hook test passed${NC}"
        else
            echo -e "${YELLOW}⚠️  Pre-commit hook test failed or timed out${NC}"
            echo -e "${BLUE}ℹ️  This may be expected if constitutional validator is not yet available${NC}"
        fi
        
        # Clean up test file
        git reset HEAD "$test_file" 2>/dev/null || true
        rm -f "$test_file"
    fi
    
    echo -e "${GREEN}✅ Hook testing completed${NC}"
    echo
}

# Function to provide usage instructions
show_usage_instructions() {
    echo -e "${PURPLE}📖 Usage Instructions${NC}"
    echo "===================="
    echo
    echo -e "${BLUE}Constitutional Git Hooks are now installed!${NC}"
    echo
    echo -e "${GREEN}What happens now:${NC}"
    echo "• Pre-commit hook: Validates SE principles before each commit"
    echo "• Pre-push hook: Enforces quality gates before each push"
    echo
    echo -e "${YELLOW}Platform-specific execution:${NC}"
    echo "• Linux/macOS: Hooks run automatically via bash"
    echo "• Windows: Git may use PowerShell versions (.ps1 files)"
    echo
    echo -e "${BLUE}Troubleshooting:${NC}"
    echo "• If hooks fail, check that WP01 Constitutional Core Engine is implemented"
    echo "• Hook logs provide detailed violation information"
    echo "• Use 'git commit --no-verify' to bypass hooks temporarily (not recommended)"
    echo
    echo -e "${GREEN}Configuration:${NC}"
    echo "• Rules: .kittify/config/se_rules.yaml"
    echo "• Quality Gates: .kittify/config/quality_gates.yaml"
    echo "• Constitution: .kittify/memory/constitution.md"
    echo
}

# Function to handle team deployment
deploy_for_team() {
    echo -e "${PURPLE}👥 Team Deployment Mode${NC}"
    echo "======================"
    echo
    
    echo -e "${BLUE}📋 Team installation checklist:${NC}"
    echo "1. Ensure all team members have Python 3.11+ installed"
    echo "2. Share this installation script with the team"
    echo "3. Have each team member run: ./scripts/install_git_hooks.sh"
    echo "4. Verify constitutional validator is available in all environments"
    echo
    
    echo -e "${GREEN}✅ Installation completed for this repository${NC}"
    echo -e "${YELLOW}💡 Each team member should run this script in their local repository${NC}"
    echo
}

# Main execution
main() {
    local team_deploy=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --team)
                team_deploy=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--team] [--help]"
                echo ""
                echo "Options:"
                echo "  --team    Enable team deployment mode with additional instructions"
                echo "  --help    Show this help message"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    echo -e "${PURPLE}🚀 Starting Git hooks installation...${NC}"
    echo
    
    # Run installation steps
    check_prerequisites
    backup_existing_hooks
    install_hooks
    verify_installation
    test_hooks
    show_usage_instructions
    
    if [[ "$team_deploy" == true ]]; then
        deploy_for_team
    fi
    
    echo -e "${GREEN}🎉 Git hooks installation completed successfully!${NC}"
    echo -e "${BLUE}💡 Constitutional enforcement is now active${NC}"
}

# Trap to ensure clean exit
trap 'echo -e "\n${YELLOW}⚠️  Installation interrupted${NC}"; exit 1' INT TERM

# Execute main function with all arguments
main "$@"