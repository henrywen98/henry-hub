#!/usr/bin/env bash
# Common functions and variables for PRD scripts

# Get repository root
get_repo_root() {
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        git rev-parse --show-toplevel
    else
        # Fall back to script location for non-git repos
        local script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        (cd "$script_dir/../../.." && pwd)
    fi
}

# Get current spec directory (based on environment variable or latest)
get_current_spec() {
    # First check if PRD_SPEC environment variable is set
    if [[ -n "${PRD_SPEC:-}" ]]; then
        echo "$PRD_SPEC"
        return
    fi

    # For non-git repos, try to find the latest spec directory
    local repo_root=$(get_repo_root)
    local specs_dir="$repo_root/specs"

    if [[ -d "$specs_dir" ]]; then
        local latest_spec=""
        local highest=0

        for dir in "$specs_dir"/*; do
            if [[ -d "$dir" ]]; then
                local dirname=$(basename "$dir")
                if [[ "$dirname" =~ ^([0-9]{3})- ]]; then
                    local number=${BASH_REMATCH[1]}
                    number=$((10#$number))
                    if [[ "$number" -gt "$highest" ]]; then
                        highest=$number
                        latest_spec=$dirname
                    fi
                fi
            fi
        done

        if [[ -n "$latest_spec" ]]; then
            echo "$latest_spec"
            return
        fi
    fi

    echo ""  # No spec found
}

get_spec_dir() { echo "$1/specs/$2"; }

# Find spec directory by numeric prefix
find_spec_dir_by_prefix() {
    local repo_root="$1"
    local spec_name="$2"
    local specs_dir="$repo_root/specs"

    # Extract numeric prefix (e.g., "004" from "004-whatever")
    if [[ ! "$spec_name" =~ ^([0-9]{3})- ]]; then
        # If spec doesn't have numeric prefix, fall back to exact match
        echo "$specs_dir/$spec_name"
        return
    fi

    local prefix="${BASH_REMATCH[1]}"

    # Search for directories in specs/ that start with this prefix
    local matches=()
    if [[ -d "$specs_dir" ]]; then
        for dir in "$specs_dir"/"$prefix"-*; do
            if [[ -d "$dir" ]]; then
                matches+=("$(basename "$dir")")
            fi
        done
    fi

    # Handle results
    if [[ ${#matches[@]} -eq 0 ]]; then
        # No match found
        echo "$specs_dir/$spec_name"
    elif [[ ${#matches[@]} -eq 1 ]]; then
        # Exactly one match
        echo "$specs_dir/${matches[0]}"
    else
        # Multiple matches
        echo "ERROR: Multiple spec directories found with prefix '$prefix': ${matches[*]}" >&2
        echo "$specs_dir/$spec_name"
    fi
}

get_spec_paths() {
    local repo_root=$(get_repo_root)
    local current_spec=$(get_current_spec)

    # Use prefix-based lookup
    local spec_dir=$(find_spec_dir_by_prefix "$repo_root" "$current_spec")

    cat <<EOF
REPO_ROOT='$repo_root'
CURRENT_SPEC='$current_spec'
SPEC_DIR='$spec_dir'
SPEC_FILE='$spec_dir/spec.md'
EOF
}

check_file() { [[ -f "$1" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
check_dir() { [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
