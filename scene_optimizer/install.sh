#!/bin/bash

# Scene Optimizer Extension Installer
# This script copies the extension to Omniverse's extension directory

echo "Scene Optimizer Extension Installer"
echo "=================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EXTENSION_NAME="scene_optimizer"
SOURCE_DIR="$SCRIPT_DIR"

# Determine the target directory based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    TARGET_DIR="$HOME/Library/Application Support/ov/pkg"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    TARGET_DIR="$HOME/.local/share/ov/pkg"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    TARGET_DIR="$LOCALAPPDATA/ov/pkg"
else
    echo "Error: Unsupported operating system"
    exit 1
fi

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating target directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# Check if extension already exists
if [ -d "$TARGET_DIR/$EXTENSION_NAME" ]; then
    echo "Warning: Extension already exists at: $TARGET_DIR/$EXTENSION_NAME"
    read -p "Do you want to overwrite it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo "Removing existing extension..."
    rm -rf "$TARGET_DIR/$EXTENSION_NAME"
fi

# Copy the extension
echo "Copying extension from: $SOURCE_DIR"
echo "To: $TARGET_DIR/$EXTENSION_NAME"
cp -r "$SOURCE_DIR" "$TARGET_DIR/$EXTENSION_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Extension installed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Open Omniverse Create or Code"
    echo "2. Go to Window > Extensions"
    echo "3. Search for 'Scene Optimizer' and enable it"
    echo "4. The extension window should open automatically"
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi

