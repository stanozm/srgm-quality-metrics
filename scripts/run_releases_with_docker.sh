#!/bin/bash

# Script for running STRAIT from docker on a set of releases
# Releases are mined from the git repo from the project that is checked out
# The script modifies dockercompose file and batchConfig.json to add the information about the release dates and the identifier of the project to be used in docker
# The output is created in the output folder of STRAIT root dir - each batchAnalysisReport.csv is moved there with the info added to the name about the project and release (as STRAIT otherwise overwrites each output)
# Running script with sudo if privileges needed for docker
# The script uses sudo -u <username> for commands that do not need sudo privileges
# change the USERNAME variable for a user to be running those commands

# Check if repository URL is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <GitHub repo URL, e.g., https://github.com/oshi/oshi>"
  exit 1
fi

REPO_URL="$1"
REPO_NAME=$(basename -s .git "$REPO_URL")
CLONE_DIR="./$REPO_NAME-tmp"
LOG_FILE="./logs/dockerlog.out"
OUTPUT_DIR="./output/"
USERNAME="brossi"

# Clone the repository if not already cloned
if [ -d "$CLONE_DIR" ]; then
  echo "Repository already cloned at $CLONE_DIR"
else
  echo "Cloning repository..."
  sudo -u $USERNAME git clone "$REPO_URL" "$CLONE_DIR"
fi

cd "$CLONE_DIR" || exit 1

# Get the date of the first commit
FIRST_COMMIT_DATE=$(git log --reverse --format=%cs | head -n 1)T00:00:00

# Get all tags and their dates
mapfile -t RELEASES < <(git for-each-ref --sort=creatordate --format '%(refname:short) %(creatordate:iso8601)' refs/tags)

# Go back to original directory
cd - > /dev/null || exit 1

ITERATION=1

# TODO should likely escape input
# Escape characters that are special in sed replacement: \ / &
#escaped_project=$(printf '%s' "$PROJECT" | sed 's/[\\/&]/\\&/g')

# Modify batchConfig.json
sudo -u $USERNAME sed -i.bak -E 's/("location"[[:space:]]*:[[:space:]]*")[^"]*"/\1'"$REPO_URL"'"/' batchConfig.json

printf 'Number of releases found: %d\n' "${#RELEASES[@]}"
for RELEASE in "${RELEASES[@]}"; do

  TAG=$(echo "$RELEASE" | awk '{print $1}')
  TAG_DATE=$(echo "$RELEASE" | awk '{print $2}')T00:00:00

  echo "Processing $RELEASE release from $FIRST_COMMIT_DATE to $TAG_DATE..........."

  # Modify docker-compose.yml with date ranges
  sudo -u $USERNAME sed -i.bak -E 's/-ft", "[0-9T:-]+", "[0-9T:-]+"/-ft", "'"$FIRST_COMMIT_DATE"'", "'"$TAG_DATE"'"/' docker-compose.yml

  # Run docker compose
  echo "Running docker compose..."
  docker compose up --abort-on-container-exit --exit-code-from java-app >> "$LOG_FILE" 2>&1

  # Copy the output CSV
  VERSION_CSV="batchAnalysisReport-$(printf "%02d" $ITERATION)-$TAG.csv"
  sudo -u $USERNAME mv batchAnalysisReport.csv "${OUTPUT_DIR}${VERSION_CSV}"

  ((ITERATION++))

  echo "Waiting 30 seconds before starting STRAIT container again..."
  sleep 30

done

# Cleanup
#rm -rf "$CLONE_DIR"
