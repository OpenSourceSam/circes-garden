#!/usr/bin/env bash
# Publish Circe's Garden to GitHub: push main, make it the default branch, rename the repo to
# circes-garden, make it public, turn on GitHub Pages from main /docs, create the v0.1.0 release.
# Safe to re-run: every step checks its own state first. Needs: gh logged in as the repo owner.
set -u
cd "$(dirname "$0")/.."
OWNER="OpenSourceSam"
OLD_NAME="circes_garden_v3"
NEW_NAME="circes-garden"
step() { printf '\n==> %s\n' "$*"; }

step "GitHub login"
gh api user --jq .login >/dev/null 2>&1 || { echo "gh is not logged in; run: gh auth login"; exit 1; }
gh api user --jq .login

step "Push main"
git push -u origin main || exit 1

step "Default branch -> main, drop the old master"
REPO="$OWNER/$OLD_NAME"
gh repo view "$OWNER/$NEW_NAME" >/dev/null 2>&1 && REPO="$OWNER/$NEW_NAME"
gh repo edit "$REPO" --default-branch main || exit 1
git push origin --delete master 2>/dev/null || echo "(remote master already gone)"

step "Rename to $NEW_NAME"
if [ "$REPO" = "$OWNER/$OLD_NAME" ]; then
  if gh repo rename "$NEW_NAME" --repo "$OWNER/$OLD_NAME" --yes; then
    REPO="$OWNER/$NEW_NAME"
    git remote set-url origin "https://github.com/$REPO.git"
  else
    echo "rename failed; keeping $OLD_NAME"
  fi
fi
NAME="${REPO#*/}"
PAGES_URL="https://$(echo "$OWNER" | tr '[:upper:]' '[:lower:]').github.io/$NAME/"

step "Public, description, topics, homepage"
gh repo edit "$REPO" --visibility public --accept-visibility-change-consequences || exit 1
gh repo edit "$REPO" \
  --description "A 20-minute narrative farming game about Circe, built in Godot 4.5 with open pixel art composed by code and an AI-assisted, test-driven pipeline" \
  --homepage "$PAGES_URL" \
  --add-topic godot --add-topic gdscript --add-topic game --add-topic pixel-art \
  --add-topic claude-code --add-topic ai-assisted-development --add-topic portfolio >/dev/null || echo "(topics/description step reported an error; continuing)"

step "GitHub Pages from main /docs"
if gh api "repos/$REPO/pages" >/dev/null 2>&1; then
  gh api -X PUT "repos/$REPO/pages" -f "source[branch]=main" -f "source[path]=/docs" >/dev/null && echo "pages source updated"
else
  gh api -X POST "repos/$REPO/pages" -f "source[branch]=main" -f "source[path]=/docs" >/dev/null && echo "pages enabled"
fi

step "Release v0.1.0"
if gh release view v0.1.0 --repo "$REPO" >/dev/null 2>&1; then
  echo "release exists"
else
  gh release create v0.1.0 \
    "build/CircesGarden-windows-x86_64.zip#Windows (x86_64) - unzip and run CircesGarden.exe" \
    "build/android/CircesGarden.apk#Android (arm64, debug-signed) - sideload on a phone or handheld" \
    --repo "$REPO" --title "Circe's Garden v0.1.0" --notes-file build/release_notes.md || exit 1
fi

step "Done"
echo "Repository: https://github.com/$REPO"
echo "Pages:      $PAGES_URL  (first build takes up to 10 minutes)"
echo "Release:    https://github.com/$REPO/releases/tag/v0.1.0"
gh api "repos/$REPO/pages" --jq '"Pages status: " + (.status // "pending")' 2>/dev/null || true
