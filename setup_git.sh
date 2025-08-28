#!/bin/bash

echo "🚀 Setting up Git repository for CSV to Kotlin Converter"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    echo "   macOS: brew install git"
    echo "   Windows: https://git-scm.com/download/win"
    echo "   Linux: sudo apt-get install git"
    exit 1
fi

# Check if this is already a git repository
if [ -d ".git" ]; then
    echo "⚠️  This directory is already a Git repository."
    echo "   If you want to start fresh, remove the .git folder first."
    exit 1
fi

# Initialize git repository
echo "📁 Initializing Git repository..."
git init

# Add all files
echo "📝 Adding files to Git..."
git add .

# Initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: CSV to Kotlin converter with web interface"

echo ""
echo "✅ Git repository initialized successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to GitHub.com and create a new repository"
echo "2. Copy the repository URL"
echo "3. Run these commands:"
echo "   git remote add origin YOUR_REPOSITORY_URL"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "🔗 Your repository URL will look like:"
echo "   https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo ""
echo "💡 Tip: You can also run this script again after creating the GitHub repo to complete the setup."
