# [PROJECT NAME] Development Guidelines
*Path: [templates/agent-file-template.md](templates/agent-file-template.md)*


Auto-generated from all feature plans. Last updated: [DATE]

## Active Technologies
[EXTRACTED FROM ALL PLAN.MD FILES]

### TeamReel Tech Stack (Constitutional Requirements)
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS (mandatory)
- **Backend**: Django REST Framework + Python 3.11+ (mandatory)  
- **AI Engine**: LangGraph + OpenAI APIs (mandatory)
- **Database**: PostgreSQL (production), SQLite (tests) (mandatory)
- **Storage**: AWS S3 with signed URLs (mandatory)
- **Testing**: Pytest (backend), Vitest (frontend), Playwright (E2E optional)
- **Linting**: Ruff (Python), ESLint + TypeScript (Frontend)
- **Deployment**: Railway (staging + production)

## Project Structure
```
[ACTUAL STRUCTURE FROM PLANS]
```

### Constitutional Structure (Mandatory Compliance)
```
TeamReel-core-app/
├── frontend/src/modules/{auth,dashboard,workflows,editor,templates}/  # SRP
├── backend/apps/{users,projects,media,ai_engine,workflows,billing}/   # SRP  
├── ai/{workflows,agents,tools,schemas}/                              # SRP
├── shared/{utils,common,types}/                                      # Reusability
└── tests/ (mirror source structure)                                  # Testability
```

## Commands
[ONLY COMMANDS FOR ACTIVE TECHNOLOGIES]

### Constitution Compliance Commands
- **Spec verification**: `spec-kitty verify` (mandatory before merge)
- **Test coverage**: `pytest --cov=. --cov-fail-under=80` (backend)
- **Code quality**: `ruff check .` (Python), `npm run lint` (Frontend)  
- **Complexity check**: Automated via ESLint/Ruff (max complexity: 10)
- **Security scan**: `python manage.py check --deploy` (Django)

[IF SCRIPT_TYPE=powershell]
## PowerShell Syntax
**⚠️ IMPORTANT**: You are in a PowerShell environment. See [.kittify/templates/POWERSHELL_SYNTAX.md](.kittify/templates/POWERSHELL_SYNTAX.md) for correct syntax.

Quick reminders:
- Use `-Json` not `--json`
- Use `;` not `&&` for command chaining
- Use `.\.kittify\scripts\powershell\` not `./kittify/scripts/bash/`
[ENDIF]

## Code Style
[LANGUAGE-SPECIFIC, ONLY FOR LANGUAGES IN USE]

### TeamReel Naming Conventions (Constitutional Requirements)

#### REST API Endpoints
- **Format**: kebab-case with trailing slashes
- **Examples**: `/user-profiles/`, `/video-workflows/`, `/ai-tasks/{id}/`
- **Status Codes**: 2xx success, 4xx client errors, 5xx server errors

#### Backend (Django/Python)  
- **Models/Functions**: snake_case (`user_profile`, `video_workflow`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_FILE_SIZE`, `DEFAULT_TIMEOUT`)
- **Apps**: snake_case folder names (`ai_engine`, `media_processing`)

#### Frontend (Next.js/TypeScript)
- **Variables/Functions**: camelCase (`userProfile`, `videoWorkflow`)  
- **Components**: PascalCase (`UserProfile`, `VideoWorkflow`)
- **Props/State**: camelCase (`userName`, `isLoading`)
- **Modules**: camelCase folder names (`authModule`, `dashboardModule`)

#### AI Workflows (Python)
- **Workflows**: snake_case (`content_generation`, `quality_validation`)
- **Agents**: snake_case (`content_agent`, `validation_agent`)
- **Schemas**: snake_case with descriptive names (`workflow_input`, `agent_output`)

### SE Principles Enforcement
- **SRP**: Each file/class has single responsibility (enforced via linting)
- **Complexity**: Max cyclomatic complexity = 10 (ESLint/Ruff rules)
- **DRY**: No duplicate code (enforced via code review + linting)
- **YAGNI**: Implement only what's needed (validated via spec compliance)

## Recent Changes
[LAST 3 FEATURES AND WHAT THEY ADDED]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->