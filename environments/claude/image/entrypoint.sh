#!/bin/bash
set -e

# Set up git credentials
if [ -f "$HOME/.github-credentials" ]; then
  echo "Setting up git credentials"
  # Read credentials file safely
  credentials=$(cat "$HOME/.github-credentials")
  username=$(echo "$credentials" | cut -d':' -f1)
  token=$(echo "$credentials" | cut -d':' -f2)
  email=$(echo "$credentials" | cut -d':' -f3)
  
  git config --global user.name "$username"
  git config --global user.email "$email"
  git config --global credential.helper store
  echo "https://$username:$token@github.com" > $HOME/.git-credentials
  chmod 600 $HOME/.git-credentials $HOME/.github-credentials
  echo "Git credentials configured successfully"
fi

./start_all.sh
./novnc_startup.sh

python http_server.py > /tmp/server_logs.txt 2>&1 &

STREAMLIT_SERVER_PORT=8501 python -m streamlit run computer_use_demo/streamlit.py > /tmp/streamlit_stdout.log &

echo "✨ Computer Use Demo is ready!"
echo "➡️  Open http://localhost:8080 in your browser to begin"

# Keep the container running
tail -f /dev/null
