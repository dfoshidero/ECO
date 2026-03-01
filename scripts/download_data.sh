#!/usr/bin/env bash
# Download training data for a specific release from GitHub Releases.
# Usage: ./scripts/download_data.sh <release_tag>
# Example: ./scripts/download_data.sh v1.0.0  -> downloads data-v1.zip to data/v1/
# Requires: gh CLI (https://cli.github.com/)
set -e

if [[ -z "${1:-}" ]]; then
    echo "Usage: ./scripts/download_data.sh <release_tag>"
    echo "Example: ./scripts/download_data.sh v1.0.0"
    exit 1
fi

RELEASE_TAG="$1"
# Extract major version (e.g. v1.0.0 -> 1, v2.1.3 -> 2)
MAJOR="${RELEASE_TAG#v}"
MAJOR="${MAJOR%%.*}"
ZIP_NAME="data-v${MAJOR}.zip"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$REPO_ROOT/data"
TARGET_DIR="$DATA_DIR/v${MAJOR}"

if ! command -v gh &>/dev/null; then
    echo "Error: gh CLI not found. Install from https://cli.github.com/"
    exit 1
fi

echo "Downloading $ZIP_NAME from release $RELEASE_TAG..."
cd "$REPO_ROOT"
gh release download "$RELEASE_TAG" --pattern "$ZIP_NAME"

if [[ ! -f "$ZIP_NAME" ]]; then
    echo "Error: $ZIP_NAME not found in release $RELEASE_TAG"
    exit 1
fi

echo "Extracting to $TARGET_DIR..."
mkdir -p "$TARGET_DIR"
unzip -o "$ZIP_NAME" -d "$DATA_DIR"
rm -f "$ZIP_NAME"

echo "Done. Data is in $TARGET_DIR (trainers/v${MAJOR}/ will use it)."
