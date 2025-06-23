# DevContainer Migration: Rye to UV

This document outlines the changes made to the devcontainer configuration when migrating from `rye` to `uv`.

## Changes Made

### 1. Updated Devcontainer Feature

**Before (Rye):**
```json
// Custom rye feature
"./rye": {}
```

**After (UV):**
```json
// Community UV feature
"ghcr.io/jsburckhardt/devcontainer-features/uv:1": {}
```


### 2. Updated Post-Create Script

**Before (`scripts/post-create.sh`):**
```bash
echo "rye sync .."
rye sync
```

**After:**
```bash
echo "Setting up uv project..."
# Create virtual environment and install dependencies
uv sync
echo "Setup complete!"
```

### 3. Removed Files

- **Deleted:** `.devcontainer/rye/` directory (custom rye feature)
- **Cleaned up:** Commented rye configuration lines

## 🚀 How to Use

### 1. Rebuild Container
1. Open VS Code
2. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
3. Type: `Dev Containers: Rebuild Container`
4. Wait for rebuild to complete

### 2. Verify Installation
After rebuild, test these commands:
```bash
# Check uv is installed
uv --version

# Check virtual environment
which python
python --version

# Test poe tasks
uv run poe --help
uv run poe test
```

## 📋 What the Container Includes

- ✅ **Python 3.10**
- ✅ **UV package manager** 
- ✅ **Virtual environment** (`.venv`)
- ✅ **All project dependencies** via `uv sync`
- ✅ **Development tools** (ruff, mypy, pytest)
- ✅ **VS Code extensions** for Python development

## Benefits

- **Faster dependency resolution** (uv is much faster than rye)
- **Consistent environment** with local development
- **Official community support** for UV devcontainer feature
- **All existing poe tasks work** without changes

## Troubleshooting

### Container Won't Build - "mv: cannot stat '/root/.cargo/bin/uv'"

If you see this error during container build:
```
mv: cannot stat '/root/.cargo/bin/uv': No such file or directory
ERROR: failed to solve: process "/bin/sh -c curl -LsSf https://astral.sh/uv/install.sh | sh && mv /root/.cargo/bin/uv /usr/local/bin/uv" did not complete successfully: exit code: 1
```

**Cause**: You're using the official `ghcr.io/astral-sh/devcontainer-features/uv` feature which has a path bug where it expects uv to install to `/root/.cargo/bin` but it actually installs to `/root/.local/bin`.

**Solution**: Use the community-maintained feature instead (which we already use):
```json
"features": {
  "ghcr.io/jsburckhardt/devcontainer-features/uv:1": {}
}
```

### Python Interpreter Not Found
- Check VS Code is using the correct interpreter: `.venv/bin/python`
- Press `Ctrl+Shift+P` → `Python: Select Interpreter`

### Commands Not Working
- Ensure you're in the container terminal
- Run `uv run poe --help` to see available tasks
- Try rebuilding the container: `Dev Containers: Rebuild Container`

## 📝 Summary

The migration replaced the custom rye devcontainer feature with a  UV feature and modified the setup script to use UV commands. All functionality remains the same - only the underlying package manager changed. 