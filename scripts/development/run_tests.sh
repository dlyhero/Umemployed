#!/bin/bash
# Enhanced script to run tests properly with better error handling

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Check if we're in the main directory or a subdirectory
if [[ -f "$SCRIPT_DIR/manage.py" ]]; then
    # We're in the main directory
    PROJECT_ROOT="$SCRIPT_DIR"
else
    # We're in a subdirectory (like scripts/)
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}Using Python: $(which python)${NC}"

# If a virtual environment is active, show it
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo -e "${GREEN}Using active virtual environment: $VIRTUAL_ENV${NC}"
fi

# Function to verify pytest and dependencies are installed
verify_deps() {
    if ! python -m pip show pytest > /dev/null 2>&1; then
        echo -e "${RED}pytest is not installed. Please install it: pip install pytest${NC}"
        return 1
    fi
    return 0
}

# Check for test collection errors first
check_collection() {
    echo -e "${BLUE}Checking for test collection errors...${NC}"
    python -m pytest --collect-only -q
    if [ $? -ne 0 ]; then
        echo -e "${RED}Test collection errors detected.${NC}"
        echo -e "${YELLOW}Would you like to see more details? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python -m pytest --collect-only -v
        fi
        
        echo -e "${YELLOW}Would you like to run the test diagnosis script? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ -f "$PROJECT_ROOT/scripts/diagnose_tests.sh" ]; then
                bash "$PROJECT_ROOT/scripts/diagnose_tests.sh"
            else
                echo -e "${RED}Test diagnosis script not found.${NC}"
            fi
            return 1
        fi
        
        echo -e "${YELLOW}Would you like to continue running tests anyway? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    else
        echo -e "${GREEN}Test collection successful.${NC}"
    fi
    return 0
}

# Verify dependencies first
verify_deps || { echo -e "${RED}Missing required dependencies${NC}"; exit 1; }

# Check for test collection errors if not skipped
if [[ "$*" != *"--skip-collection-check"* ]]; then
    check_collection || exit 1
fi

# Remove our custom --skip-collection-check flag if present
ARGS=$(echo "$@" | sed 's/--skip-collection-check//')

# Check for Django-specific options
if python -m pip show pytest-django > /dev/null 2>&1; then
    # If pytest-django is installed, we can use the Django-specific options
    if python -m pip show django > /dev/null 2>&1; then
        DJANGO_OPTS="--reuse-db"
    else
        DJANGO_OPTS=""
    fi
    
    # Check if we're in a CI environment
    if [ "$CI" = "true" ]; then
        # In CI, we don't want to reuse the database
        DJANGO_OPTS=""
    fi
    
    echo -e "${BLUE}Running tests with Django options: $DJANGO_OPTS${NC}"
    cd "$PROJECT_ROOT" && python -m pytest $DJANGO_OPTS $ARGS
    TEST_EXIT_CODE=$?
else
    # Otherwise, just run pytest normally
    echo -e "${BLUE}Running tests without Django options${NC}"
    cd "$PROJECT_ROOT" && python -m pytest $ARGS
    TEST_EXIT_CODE=$?
fi

# Show helpful messages based on the result
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed (exit code: $TEST_EXIT_CODE).${NC}"
    echo -e "${YELLOW}To diagnose test failures, run: scripts/diagnose_tests.sh${NC}"
fi

echo -e "${BLUE}Tests completed with exit code: $TEST_EXIT_CODE${NC}"
exit $TEST_EXIT_CODE
