#!/bin/bash
echo "Building YouTube Karaoke Linux Executable..."
pyinstaller --clean youtube_karaoke.spec
echo "Build complete! The executable is in the dist folder."
