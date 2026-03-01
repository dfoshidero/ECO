#!/usr/bin/env bash
# ECO deployment build script
# Version is ALWAYS set by this script (never set version.json manually).
# Usage: ./build.sh test | ./build.sh release <patch|minor|major>
set -e

# Find a working Python (test run, not just existence - Windows Store alias can fool command -v)
for cand in python3 python "py -3" py; do
    if $cand -c "import json" 2>/dev/null; then
        PYTHON=$cand
        break
    fi
done
if [[ -z "${PYTHON:-}" ]]; then
    echo "Error: Python not found. Install Python or ensure 'python', 'python3', or 'py' is in PATH."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEV_WORKING="$REPO_ROOT/deployment/dev/working"

# Docker Hub image for push (username/repo)
DOCKER_PUSH_IMAGE="${DOCKER_PUSH_IMAGE:-dfoshidero/eco-embodied-carbon-api}"
DEV_MODELS="$REPO_ROOT/deployment/dev/models"
PROD_RELEASES="$REPO_ROOT/deployment/prod/releases"
PROD_DOCKERFILE="$SCRIPT_DIR/Dockerfile"
DATA_DIR="$REPO_ROOT/data"

# Bootstrap version.json only when missing; thereafter only release bump changes it.
ensure_version_json() {
    if [[ ! -f "$DEV_WORKING/version.json" ]]; then
        echo '{"version": "1.0.0", "major": 1}' > "$DEV_WORKING/version.json"
        echo "Created $DEV_WORKING/version.json (bootstrap 1.0.0). Use 'build.sh release <patch|minor|major>' to set version; never edit by hand."
    fi
}

read_version() {
    (cd "$DEV_WORKING" && $PYTHON -c "import json; print(json.load(open('version.json'))['version'])")
}

read_major() {
    (cd "$DEV_WORKING" && $PYTHON -c "import json; print(json.load(open('version.json'))['major'])")
}

parse_version() {
    local v="$1"
    v="${v#v}"
    local major="${v%%.*}"
    v="${v#$major.}"
    local minor="${v%%.*}"
    local patch="${v#$minor.}"
    echo "$major $minor $patch"
}

bump_version() {
    local bump_type="$1"
    local major minor patch
    read major minor patch < <(parse_version "$(read_version)")
    case "$bump_type" in
        patch) patch=$((patch + 1)) ;;
        minor) minor=$((minor + 1)); patch=0 ;;
        major) major=$((major + 1)); minor=0; patch=0 ;;
        *) echo "Invalid bump type: $bump_type"; exit 1 ;;
    esac
    echo "v${major}.${minor}.${patch}"
}

validate_manifest() {
    local major="$1"
    local model_dir="$DEV_MODELS/v$major"
    local manifest="$model_dir/manifest.json"
    if [[ ! -f "$manifest" ]]; then
        echo "Error: manifest.json not found at $manifest"
        exit 1
    fi
    local files
    files=$(cd "$model_dir" && $PYTHON -c "import json; m=json.load(open('manifest.json')); print(' '.join(m.get('files',[])))")
    for f in $files; do
        if [[ ! -f "$model_dir/$f" ]]; then
            echo "Error: Required model file missing: $model_dir/$f"
            exit 1
        fi
    done
}

build_image() {
    local build_dir="$1"
    local tag="$2"
    cd "$build_dir"
    docker build -t "$tag" -f Dockerfile .
    echo "Built: $tag"
    docker images "$tag" --format "Size: {{.Size}}"
}

# --- Test mode (uses current version from version.json; no bump) ---
cmd_test() {
    local version
    version=$(read_version)
    echo "Test build using version from version.json: $version"
    local major
    major=$(read_major)
    validate_manifest "$major"
    local tmp_build
    tmp_build=$(mktemp -d)
    trap "rm -rf $tmp_build" EXIT
    cp -r "$DEV_WORKING/app" "$tmp_build/"
    cp "$DEV_WORKING/requirements.txt" "$tmp_build/"
    cp "$DEV_WORKING/version.json" "$tmp_build/"
    mkdir -p "$tmp_build/model"
    for f in "$DEV_MODELS/v$major"/*.pkl; do
        [[ -f "$f" ]] && cp "$f" "$tmp_build/model/"
    done
    cp "$PROD_DOCKERFILE" "$tmp_build/Dockerfile"
    build_image "$tmp_build" "eco-model:test"
    docker tag "eco-model:test" "$DOCKER_PUSH_IMAGE:dev-$version"
    echo "Tagged for push: $DOCKER_PUSH_IMAGE:dev-$version"
}

# --- Release mode ---
cmd_release() {
    local bump_type="$1"
    [[ -z "$bump_type" ]] && { echo "Usage: ./build.sh release <patch|minor|major>"; exit 1; }
    local new_version
    new_version=$(bump_version "$bump_type")
    local major
    major="${new_version#v}"
    major="${major%%.*}"
    validate_manifest "$major"
    local release_dir="$PROD_RELEASES/$new_version"
    if [[ -d "$release_dir" ]]; then
        echo "Error: Release $new_version already exists at $release_dir"
        exit 1
    fi
    mkdir -p "$release_dir"
    cp -r "$DEV_WORKING/app" "$release_dir/"
    cp "$DEV_WORKING/requirements.txt" "$release_dir/"
    [[ -f "$DEV_WORKING/README.md" ]] && cp "$DEV_WORKING/README.md" "$release_dir/"
    mkdir -p "$release_dir/model"
    for f in "$DEV_MODELS/v$major"/*.pkl; do
        [[ -f "$f" ]] && cp "$f" "$release_dir/model/"
    done
    echo "{\"version\": \"$new_version\", \"major\": $major}" > "$release_dir/version.json"
    cp "$PROD_DOCKERFILE" "$release_dir/Dockerfile"
    build_image "$release_dir" "eco-model:$new_version"
    docker tag "eco-model:$new_version" "$DOCKER_PUSH_IMAGE:release-$new_version"
    docker tag "eco-model:$new_version" "$DOCKER_PUSH_IMAGE:latest"
    echo "Tagged for push: $DOCKER_PUSH_IMAGE:release-$new_version, $DOCKER_PUSH_IMAGE:latest"
    $PYTHON -c "
import json
p='$DEV_WORKING/version.json'
d=json.load(open(p))
d['version']='$new_version'
d['major']=$major
json.dump(d,open(p,'w'),indent=2)
"
    echo "Updated $DEV_WORKING/version.json to $new_version (version is always set by build.sh)"
    if [[ "$bump_type" == "major" ]]; then
        if command -v gh &>/dev/null && [[ -d "$DATA_DIR/v$major" ]]; then
            local zip_name="data-v$major.zip"
            (cd "$DATA_DIR" && zip -r "$zip_name" "v$major")
            if gh release view "$new_version" &>/dev/null; then
                gh release upload "$new_version" "$DATA_DIR/$zip_name" --clobber
            else
                gh release create "$new_version" "$DATA_DIR/$zip_name" --title "$new_version"
            fi
            rm -f "$DATA_DIR/$zip_name"
            echo "Attached $zip_name to GitHub Release $new_version"
        else
            echo "Note: Skipped data upload (gh CLI not found or data/v$major missing)"
        fi
    fi
    echo "Release $new_version ready at $release_dir"
}

# --- Main ---
ensure_version_json
case "${1:-}" in
    test) cmd_test ;;
    release) cmd_release "${2:-}" ;;
    *) echo "Usage: ./build.sh test | ./build.sh release <patch|minor|major>"; exit 1 ;;
esac
