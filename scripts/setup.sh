#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is required but was not found on PATH." >&2
  echo "This repo tracks implementation work via GitHub issues, so gh is required." >&2
  echo "Install it from https://cli.github.com/ and re-run this script." >&2
  exit 1
fi

echo "gh is installed: $(gh --version | head -n 1)"
