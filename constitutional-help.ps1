#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Constitutional Help CLI for Windows/PowerShell

.DESCRIPTION
    Simple command-line interface for the constitutional help system.
    
.PARAMETER Topic
    Help topic to display (principle, topic, or quick fix)
    
.PARAMETER ListPrinciples
    List all constitutional principles
    
.PARAMETER Search
    Search help content for a query

.EXAMPLE
    .\constitutional-help.ps1
    Show general help
    
.EXAMPLE
    .\constitutional-help.ps1 srp
    Learn about Single Responsibility Principle
    
.EXAMPLE
    .\constitutional-help.ps1 -ListPrinciples
    List all constitutional principles
    
.EXAMPLE
    .\constitutional-help.ps1 -Search "test coverage"
    Search help content
#>

param(
    [string]$Topic,
    [switch]$ListPrinciples,
    [string]$Search
)

# Add src to Python path and run help system
$srcPath = Join-Path $PSScriptRoot "src"

if ($ListPrinciples) {
    python -c "import sys; sys.path.insert(0, '$srcPath'); from help_system import ConstitutionalHelpSystem; print(ConstitutionalHelpSystem().list_principles())"
}
elseif ($Search) {
    python -c "import sys; sys.path.insert(0, '$srcPath'); from help_system import ConstitutionalHelpSystem; print(ConstitutionalHelpSystem().search_help('$Search'))"
}
elseif ($Topic) {
    python -c "import sys; sys.path.insert(0, '$srcPath'); from help_system import ConstitutionalHelpSystem; print(ConstitutionalHelpSystem().show_help('$Topic'))"
}
else {
    python -c "import sys; sys.path.insert(0, '$srcPath'); from help_system import ConstitutionalHelpSystem; print(ConstitutionalHelpSystem().show_help())"
}