#!/usr/bin/env bash
# Open MongoDB Compass connected to the Employee Management System database.
#
# Usage:
#   ./scripts/compass.sh          # Open Compass with connection URI
#   ./scripts/compass.sh --import # Show how to import saved connections
#   ./scripts/compass.sh --install # Install Compass via Homebrew (macOS)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONNECTIONS_FILE="$ROOT_DIR/config/compass/ems-local.connections.json"
DATABASE_NAME="${DATABASE_NAME:-employee_management}"
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
COMPASS_URI="mongodb://${MONGO_HOST}:${MONGO_PORT}/${DATABASE_NAME}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}▸${NC} $*"; }
warn()  { echo -e "${YELLOW}▸${NC} $*"; }
error() { echo -e "${RED}▸${NC} $*" >&2; }

check_mongodb() {
  if command -v mongosh >/dev/null 2>&1; then
    if mongosh --quiet --eval "db.runCommand({ ping: 1 })" >/dev/null 2>&1; then
      info "MongoDB is running at ${MONGO_HOST}:${MONGO_PORT}"
      return 0
    fi
  fi
  error "MongoDB is not reachable at ${MONGO_HOST}:${MONGO_PORT}"
  echo ""
  echo "Start MongoDB using one of these:"
  echo "  brew services start mongodb-community   # Homebrew install"
  echo "  docker compose up mongodb -d            # Docker (from project root)"
  return 1
}

install_compass() {
  if [[ "$(uname)" != "Darwin" ]]; then
    warn "Homebrew cask install is macOS only."
    echo "Download Compass: https://www.mongodb.com/try/download/compass"
    exit 1
  fi
  if ! command -v brew >/dev/null 2>&1; then
    error "Homebrew is not installed. Install from https://brew.sh"
    exit 1
  fi
  info "Installing MongoDB Compass via Homebrew..."
  brew install --cask mongodb-compass
  info "MongoDB Compass installed."
}

show_import_instructions() {
  echo ""
  info "Import saved connections into MongoDB Compass:"
  echo ""
  echo "  1. Open MongoDB Compass"
  echo "  2. Click  CONNECT  →  Import saved connections"
  echo "  3. Select file:"
  echo "     ${CONNECTIONS_FILE}"
  echo ""
  info "Or paste this connection string manually:"
  echo ""
  echo "  ${COMPASS_URI}"
  echo ""
  info "Collections in this project:"
  echo "  • users       — registered users and roles"
  echo "  • employees   — employee records"
  echo "  • audit_logs  — login/logout and CRUD audit trail"
}

open_compass() {
  local compass_app=""

  if [[ "$(uname)" == "Darwin" ]]; then
    if [[ -d "/Applications/MongoDB Compass.app" ]]; then
      compass_app="/Applications/MongoDB Compass.app"
    fi
  elif [[ "$(uname)" == "Linux" ]]; then
    if command -v mongodb-compass >/dev/null 2>&1; then
      compass_app="mongodb-compass"
    fi
  fi

  if [[ -n "$compass_app" ]]; then
    info "Opening MongoDB Compass → ${COMPASS_URI}"
    if [[ "$(uname)" == "Darwin" ]]; then
      open -a "MongoDB Compass" --args "$COMPASS_URI"
    else
      mongodb-compass "$COMPASS_URI" &
    fi
  else
    warn "MongoDB Compass is not installed."
    echo ""
    echo "Install options:"
    echo "  macOS:   brew install --cask mongodb-compass"
    echo "  Windows: https://www.mongodb.com/try/download/compass"
    echo "  Linux:   https://www.mongodb.com/try/download/compass"
    echo ""
    echo "Or run:  ./scripts/compass.sh --install"
    echo ""
    show_import_instructions
    exit 1
  fi
}

show_status() {
  if command -v mongosh >/dev/null 2>&1; then
    info "Database summary:"
    mongosh "$DATABASE_NAME" --quiet --eval "
      print('  Database:     ${DATABASE_NAME}');
      print('  users:        ' + db.users.countDocuments({}));
      print('  employees:    ' + db.employees.countDocuments({}));
      print('  audit_logs:   ' + db.audit_logs.countDocuments({}));
    " 2>/dev/null || warn "Could not query ${DATABASE_NAME}"
  fi
}

case "${1:-}" in
  --install)
    install_compass
    ;;
  --import)
    show_import_instructions
    ;;
  --help|-h)
    echo "Usage: ./scripts/compass.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  (none)      Check MongoDB, then open Compass"
    echo "  --install   Install Compass via Homebrew (macOS)"
    echo "  --import    Show import instructions and connection string"
    echo "  --help      Show this help"
    ;;
  *)
    check_mongodb
    show_status
    open_compass
    ;;
esac
