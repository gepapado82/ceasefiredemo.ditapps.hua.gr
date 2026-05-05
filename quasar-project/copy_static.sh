#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Source and destination directories
SRC_DIR="../api/static"
DEST_DIR="./public"

# Check if source directory exists
if [ ! -d "$SRC_DIR" ]; then
    echo -e "${RED}Error: Source directory $SRC_DIR does not exist${NC}"
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Copy all files and directories
echo -e "${GREEN}Copying files from $SRC_DIR to $DEST_DIR${NC}"
cp -r "$SRC_DIR"/* "$DEST_DIR"

# Check if copy was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Files copied successfully${NC}"
else
    echo -e "${RED}Error copying files${NC}"
    exit 1
fi