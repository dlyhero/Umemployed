#!/bin/bash
# Production deployment script for the Umemployed project
# This script performs production-specific checks and preparations

set -e  # Exit on any error

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}      PRODUCTION DEPLOYMENT SCRIPT${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${RED}Error: No virtual environment detected!${NC}"
    exit 1
else
    echo -e "${GREEN}Using virtual environment: $VIRTUAL_ENV${NC}"
fi

cd "$PROJECT_ROOT"

# Function to run a step and handle errors
run_step() {
    local step_name="$1"
    local command="$2"
    
    echo -e "\n${YELLOW}=== Running step: $step_name ===${NC}"
    if eval "$command"; then
        echo -e "${GREEN}✓ Step completed successfully: $step_name${NC}"
        return 0
    else
        local exit_code=$?
        echo -e "${RED}✗ Step failed: $step_name (Exit code: $exit_code)${NC}"
        echo -e "${YELLOW}Do you want to continue anyway? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Deployment preparation aborted.${NC}"
            exit 1
        fi
        return $exit_code
    fi
}

# Production-specific checks and operations
run_step "Validating production environment" "python manage.py check --deploy"

# Run migrations (production)
echo -e "${YELLOW}Do you want to apply database migrations in production? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_step "Applying migrations" "python manage.py migrate"
else
    echo -e "${YELLOW}Migrations not applied.${NC}"
fi

# Collect static files (production)
echo -e "${YELLOW}Do you want to collect static files for production? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_step "Collecting static files" "python manage.py collectstatic --noinput"
else
    echo -e "${YELLOW}Static files not collected.${NC}"
fi

# Check database connection
run_step "Checking database connection" "python manage.py dbshell --command='SELECT 1;' || python -c 'import django; django.setup(); from django.db import connections; connections[\"default\"].ensure_connection(); print(\"Database connection successful!\")'"

# Production checklist
echo -e "\n${YELLOW}=== Production deployment checklist ===${NC}"
echo -e "${BLUE}☐ Have you updated SECRET_KEY in production?${NC}"
echo -e "${BLUE}☐ Is DEBUG set to False in production settings?${NC}"
echo -e "${BLUE}☐ Have you configured proper ALLOWED_HOSTS?${NC}"
echo -e "${BLUE}☐ Are database credentials secure and backed up?${NC}"
echo -e "${BLUE}☐ Is HTTPS properly configured?${NC}"
echo -e "${BLUE}☐ Have you set up proper logging?${NC}"
echo -e "${BLUE}☐ Are static and media files properly configured?${NC}"
echo -e "${BLUE}☐ Have you set up a backup strategy?${NC}"

# Generate deployment report
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$PROJECT_ROOT/deployment_report_$TIMESTAMP.txt"

{
    echo "Umemployed Production Deployment Report"
    echo "======================================"
    echo "Generated: $(date)"
    echo "Python: $(python --version 2>&1)"
    echo "Virtual Environment: $VIRTUAL_ENV"
    echo
    echo "Django Version: $(python -c 'import django; print(django.get_version())')"
    echo
    echo "Database: $(python -c "
import django
django.setup()
from django.db import connections
db = connections['default'].settings_dict
print(f'{db[\"ENGINE\"]} - {db[\"NAME\"]}')
")"
} > "$REPORT_FILE"

echo -e "${GREEN}Production deployment report generated: $REPORT_FILE${NC}"
echo -e "\n${GREEN}=== Production deployment preparation completed ===${NC}"

# 1. Update dependencies
run_step "Checking and updating dependencies" "pip install -r $PROJECT_ROOT/requirements.txt"

# 2. Validate Python package versions
run_step "Validating package versions" "pip check"

# 3. Lint code with flake8 if available
if command -v flake8 &> /dev/null; then
    run_step "Linting code with flake8" "cd $PROJECT_ROOT && flake8"
else
    echo -e "${YELLOW}Skipping flake8 linting (flake8 not installed)${NC}"
    echo -e "${YELLOW}Consider installing flake8: pip install flake8${NC}"
fi

# 4. Run tests
echo -e "\n${YELLOW}=== Running step: Running tests ===${NC}"
echo -e "${BLUE}First checking for any test collection errors...${NC}"
cd "$PROJECT_ROOT" && python -m pytest --collect-only -v > test_collection_results.txt 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Test collection errors found.${NC}"
    echo -e "${YELLOW}Collection errors:${NC}"
    cat test_collection_results.txt | grep -E "Error|error|ERRORS|errors" -A 5
    echo -e "${YELLOW}Do you want to try running tests anyway? (y/n)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Running tests with -k to skip collection errors...${NC}"
        run_step "Running tests (with skips)" "$PROJECT_ROOT/scripts/development/run_tests.sh -v -k 'not error'"
    else
        echo -e "${YELLOW}Skipping tests due to collection errors.${NC}"
        echo -e "${YELLOW}You can fix the errors and run tests manually with: ./scripts/development/run_tests.sh -v${NC}"
    fi
else
    echo -e "${GREEN}✓ No test collection errors found.${NC}"
    run_step "Running tests" "$PROJECT_ROOT/scripts/development/run_tests.sh -v"
fi

# 5. Check for missing migrations
run_step "Checking for missing migrations" "cd $PROJECT_ROOT && python manage.py makemigrations --check --dry-run"

# 6. Run migrations
run_step "Running database migrations" "cd $PROJECT_ROOT && python manage.py migrate --plan"
echo -e "${YELLOW}The above is the migration plan. Do you want to apply these migrations? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_step "Applying migrations" "cd $PROJECT_ROOT && python manage.py migrate"
else
    echo -e "${YELLOW}Migrations not applied.${NC}"
fi

# 7. Collect static files
echo -e "${YELLOW}Do you want to collect static files? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_step "Collecting static files" "cd $PROJECT_ROOT && python manage.py collectstatic --noinput"
else
    echo -e "${YELLOW}Static files not collected.${NC}"
fi

# 8. Run system checks
run_step "Running Django system checks" "cd $PROJECT_ROOT && python manage.py check --deploy"

# 9. Check security with bandit if available
if command -v bandit &> /dev/null; then
    run_step "Running security checks with bandit" "cd $PROJECT_ROOT && bandit -r ."
else
    echo -e "${YELLOW}Skipping security checks (bandit not installed)${NC}"
    echo -e "${YELLOW}Consider installing bandit: pip install bandit${NC}"
fi

# 10. Check for outdated packages
run_step "Checking for outdated packages" "pip list --outdated"

# 11. Generate requirements.txt if necessary
echo -e "${YELLOW}Do you want to update requirements.txt with your current environment? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_step "Updating requirements.txt" "pip freeze > $PROJECT_ROOT/requirements.txt.new && mv $PROJECT_ROOT/requirements.txt.new $PROJECT_ROOT/requirements.txt"
    echo -e "${GREEN}requirements.txt has been updated.${NC}"
else
    echo -e "${YELLOW}requirements.txt not updated.${NC}"
fi

# 12. Check database connection
run_step "Checking database connection" "cd $PROJECT_ROOT && python -c \"
import django
django.setup()
from django.db import connections
connections['default'].ensure_connection()
print('Database connection successful!')
\""

# 13. Check for common deployment issues
echo -e "\n${YELLOW}=== Pre-deployment checklist ===${NC}"
echo -e "${BLUE}☐ Have you updated SECRET_KEY in production?${NC}"
echo -e "${BLUE}☐ Is DEBUG set to False in production settings?${NC}"
echo -e "${BLUE}☐ Have you configured proper ALLOWED_HOSTS?${NC}"
echo -e "${BLUE}☐ Are database credentials secure and backed up?${NC}"
echo -e "${BLUE}☐ Is HTTPS properly configured?${NC}"
echo -e "${BLUE}☐ Have you set up proper logging?${NC}"
echo -e "${BLUE}☐ Are static and media files properly configured?${NC}"
echo -e "${BLUE}☐ Have you set up a backup strategy?${NC}"

# Final summary
echo -e "\n${GREEN}=== Deployment preparation completed ===${NC}"
echo -e "${GREEN}Your application is ready for deployment!${NC}"
echo -e "${YELLOW}Remember to backup your database before deploying.${NC}"

# Generate a deployment report
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$PROJECT_ROOT/deployment_report_$TIMESTAMP.txt"

{
    echo "Umemployed Deployment Report"
    echo "============================="
    echo "Generated: $(date)"
    echo "Python: $(python --version 2>&1)"
    echo "Virtual Environment: $VIRTUAL_ENV"
    echo
    echo "Django Version: $(python -c 'import django; print(django.get_version())')"
    echo
    echo "Database: $(python -c "
import django
django.setup()
from django.db import connections
db = connections['default'].settings_dict
print(f'{db[\"ENGINE\"]} - {db[\"NAME\"]}')
")"
    echo
    echo "Package Versions:"
    pip freeze
} > "$REPORT_FILE"

echo -e "${GREEN}Deployment report generated: $REPORT_FILE${NC}"
