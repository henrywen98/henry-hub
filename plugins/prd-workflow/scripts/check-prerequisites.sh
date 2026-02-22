#!/usr/bin/env bash

# Simplified prerequisite checking script for PRD workflow
#
# Usage: ./check-prerequisites.sh [OPTIONS]
#
# OPTIONS:
#   --json              Output in JSON format
#   --paths-only        Only output path variables (no validation)
#   --help, -h          Show help message

set -e

# Parse command line arguments
JSON_MODE=false
PATHS_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --paths-only)
            PATHS_ONLY=true
            ;;
        --help|-h)
            cat << 'EOF'
Usage: check-prerequisites.sh [OPTIONS]

Simplified prerequisite checking for PRD workflow.

OPTIONS:
  --json              Output in JSON format
  --paths-only        Only output path variables (no prerequisite validation)
  --help, -h          Show this help message

EXAMPLES:
  # Get spec paths only (no validation)
  ./check-prerequisites.sh --paths-only

  # Get spec paths in JSON format
  ./check-prerequisites.sh --json --paths-only

EOF
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option '$arg'. Use --help for usage information." >&2
            exit 1
            ;;
    esac
done

# Source common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Get spec paths
eval $(get_spec_paths)

# If paths-only mode, output paths and exit
if $PATHS_ONLY; then
    if $JSON_MODE; then
        printf '{"REPO_ROOT":"%s","SPEC_DIR":"%s","SPEC_FILE":"%s"}\n' \
            "$REPO_ROOT" "$SPEC_DIR" "$SPEC_FILE"
    else
        echo "REPO_ROOT: $REPO_ROOT"
        echo "SPEC_DIR: $SPEC_DIR"
        echo "SPEC_FILE: $SPEC_FILE"
    fi
    exit 0
fi

# Validate required directories and files
if [[ ! -d "$SPEC_DIR" ]]; then
    echo "ERROR: Spec directory not found: $SPEC_DIR" >&2
    echo "Run /prd.create first to create the spec structure." >&2
    exit 1
fi

if [[ ! -f "$SPEC_FILE" ]]; then
    echo "ERROR: spec.md not found in $SPEC_DIR" >&2
    echo "Run /prd.create first to create the spec file." >&2
    exit 1
fi

# Output results
if $JSON_MODE; then
    printf '{"SPEC_DIR":"%s","SPEC_FILE":"%s"}\n' "$SPEC_DIR" "$SPEC_FILE"
else
    echo "SPEC_DIR: $SPEC_DIR"
    echo "SPEC_FILE: $SPEC_FILE"
    check_file "$SPEC_FILE" "spec.md"
fi
