# --- CONFIGURATION ---
TARGET_ALIAS="runmyapp"
PROJECT_DIR="$HOME/workspace/myproject"
SCRIPT_PATH="$PROJECT_DIR/start_app.sh"
# ---------------------

# 1. Ensure the directory exists to avoid errors
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Directory $PROJECT_DIR does not exist."
else
    # 2. Check if alias already exists in .bashrc
    if grep -q "alias $TARGET_ALIAS=" ~/.bashrc; then
        echo "⚠️  Alias '$TARGET_ALIAS' already exists in .bashrc. Skipping."
    else
        # 3. Append the alias command to .bashrc
        echo "" >> ~/.bashrc
        echo "# Shortcut for Term-AI" >> ~/.bashrc
        echo "alias $TARGET_ALIAS='$SCRIPT_PATH'" >> ~/.bashrc
        echo "✅ Alias '$TARGET_ALIAS' added successfully."
    fi

    # 4. Make the script executable (just in case)
    if [ -f "$SCRIPT_PATH" ]; then
        chmod +x "$SCRIPT_PATH"
        echo "✅ Made start_app.sh executable."
    fi

    # 5. Reload the shell to apply changes immediately
    echo "🔄 Reloading shell configuration..."
    exec bash
fi