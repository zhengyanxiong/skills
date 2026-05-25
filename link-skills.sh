#!/usr/bin/env bash
# link-skills.sh - Symlink skills from a central repository to agent skill directories
#
# Usage:
#   ./link-skills.sh install            Create symlinks for all skills
#   ./link-skills.sh uninstall          Remove symlinks created by this script
#   ./link-skills.sh status             Show current link state for all agents
#   ./link-skills.sh install --dry-run  Preview changes without executing
#   ./link-skills.sh install --agents claude-code,kimi
#   ./link-skills.sh install --skills skill-authoring-guide
#
# The script detects installed agents by checking for their parent config
# directories, then creates symlinks from the central skills repo into each
# agent's skills/ directory. Only the central repo is the source of truth;
# agent directories hold symlinks pointing back to it.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_NAME="$(basename "$REPO_DIR")"

# ── Color helpers ────────────────────────────────────────────────────────

BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
RESET='\033[0m'

ok()  { echo -e "  ${GREEN}${BOLD}[OK]${RESET} $*"; }
warn(){ echo -e "  ${YELLOW}${BOLD}[!!]${RESET} $*"; }
err() { echo -e "  ${RED}${BOLD}[XX]${RESET} $*"; }
info(){ echo -e "  ${CYAN}${BOLD}[..]${RESET} $*"; }

# ── Known agent skill directories ────────────────────────────────────────

# Format: "agent_id|display_name|skill_dir_parent|skill_dir_name"
# skill_dir_parent is the base config directory. The skill dir (skills/) is
# created inside it if it doesn't exist. Omit skill_dir_name if skills live
# directly inside the parent (unusual).
AGENT_DEFS=(
  "claude-code|Claude Code|$HOME/.claude|skills"
  "codex-cli|Codex CLI|$HOME/.codex|skills"
  "openclaw|OpenClaw|$HOME/.openclaw|skills"
  "kimi|Kimi|$HOME/.kimi|skills"
  "cowork|CoWork|$HOME/.cowork|skills"
  "cursor|Cursor|$HOME/.cursor|skills"
)

# ── Parse arguments ──────────────────────────────────────────────────────

DRY_RUN=false
COMMAND=""
SELECTED_AGENTS=()
SELECTED_SKILLS=()

for arg in "$@"; do
  case "$arg" in
    install|uninstall|status)
      COMMAND="$arg"
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --agents=*)
      IFS=',' read -ra SELECTED_AGENTS <<< "${arg#--agents=}"
      ;;
    --skills=*)
      IFS=',' read -ra SELECTED_SKILLS <<< "${arg#--skills=}"
      ;;
    -h|--help)
      sed -n '2,20p' "$0"
      exit 0
      ;;
    *)
      err "Unknown argument: $arg"
      echo "Usage: $0 [install|uninstall|status] [--dry-run] [--agents=a,b] [--skills=x,y]"
      exit 1
      ;;
  esac
done

if [ -z "$COMMAND" ]; then
  err "Missing command. Use: install, uninstall, or status"
  exit 1
fi

# ── Resolve agents ───────────────────────────────────────────────────────

# Filter to selected agents (if specified) and detect which are installed
# by checking whether the parent config directory exists.
resolve_agents() {
  local result=()
  for def in "${AGENT_DEFS[@]}"; do
    IFS='|' read -r agent_id display_name parent_dir skill_dir_name <<< "$def"
    local skill_dir="${parent_dir}/${skill_dir_name}"

    # Filter by --agents if specified
    if [ ${#SELECTED_AGENTS[@]} -gt 0 ]; then
      local found=false
      for a in "${SELECTED_AGENTS[@]}"; do
        [ "$a" = "$agent_id" ] && found=true && break
      done
      [ "$found" = false ] && continue
    fi

    # Only include if the parent config directory exists (agent is installed)
    if [ -d "$parent_dir" ]; then
      result+=("${agent_id}|${display_name}|${parent_dir}|${skill_dir_name}|${skill_dir}")
    fi
  done
  printf '%s\n' "${result[@]}"
}

# ── Resolve skills ───────────────────────────────────────────────────────

# Find all SKILL.md files in the repo (one level below repo root).
resolve_skills() {
  local result=()
  for skill_md in "$REPO_DIR"/*/SKILL.md; do
    [ -f "$skill_md" ] || continue
    local skill_dir
    skill_dir="$(dirname "$skill_md")"
    local skill_name
    skill_name="$(basename "$skill_dir")"

    # Filter by --skills if specified
    if [ ${#SELECTED_SKILLS[@]} -gt 0 ]; then
      local found=false
      for s in "${SELECTED_SKILLS[@]}"; do
        [ "$s" = "$skill_name" ] && found=true && break
      done
      [ "$found" = false ] && continue
    fi

    result+=("${skill_name}|${skill_dir}")
  done
  printf '%s\n' "${result[@]}"
}

# ── Commands ──────────────────────────────────────────────────────────────

cmd_install() {
  local agents=()
  local skills=()
  local line
  while IFS= read -r line; do [ -n "$line" ] && agents+=("$line"); done < <(resolve_agents)
  while IFS= read -r line; do [ -n "$line" ] && skills+=("$line"); done < <(resolve_skills)

  if [ ${#agents[@]} -eq 0 ]; then
    warn "No installed agents detected (or none matched --agents filter)"
    echo ""
    echo "  Currently monitored agent config directories:"
    for def in "${AGENT_DEFS[@]}"; do
      IFS='|' read -r agent_id display_name parent_dir skill_dir_name <<< "$def"
      if [ -d "$parent_dir" ]; then
        echo -e "    ${GREEN}+${RESET} ${display_name} (${parent_dir})"
      else
        echo -e "    ${DIM}-${RESET} ${display_name} (${parent_dir}) -- not installed"
      fi
    done
    exit 0
  fi

  if [ ${#skills[@]} -eq 0 ]; then
    warn "No skills found in $REPO_DIR"
    exit 0
  fi

  local total_created=0
  local total_skipped=0
  local total_errors=0

  for agent_line in "${agents[@]}"; do
    IFS='|' read -r agent_id display_name parent_dir skill_dir_name skill_dir <<< "$agent_line"
    echo ""
    echo -e "${BOLD}${display_name}${RESET} ${DIM}(${skill_dir})${RESET}"

    # Create agent skill directory if needed
    if [ ! -d "$skill_dir" ]; then
      if [ "$DRY_RUN" = true ]; then
        info "mkdir -p $skill_dir"
      else
        mkdir -p "$skill_dir"
        ok "created $skill_dir"
      fi
    fi

    for skill_line in "${skills[@]}"; do
      IFS='|' read -r skill_name skill_src <<< "$skill_line"
      local link_path="${skill_dir}/${skill_name}"

      if [ -L "$link_path" ]; then
        # Already a symlink -- check if it points to us
        local current_target
        current_target="$(readlink "$link_path")"
        if [ "$current_target" = "$skill_src" ]; then
          info "${DIM}${skill_name}${RESET} ${DIM}already linked${RESET}"
          ((total_skipped++)) || true
        else
          warn "${skill_name} points to ${DIM}${current_target}${RESET}, expected ${DIM}${skill_src}${RESET}"
          if [ "$DRY_RUN" = true ]; then
            info "would update symlink"
          else
            ln -sfn "$skill_src" "$link_path"
            ok "${skill_name} ${DIM}updated${RESET}"
          fi
          ((total_created++)) || true
        fi
      elif [ -d "$link_path" ] || [ -f "$link_path" ]; then
        # Real file/directory in the way
        err "${skill_name} ${DIM}real file exists at target, skipping${RESET}"
        ((total_errors++)) || true
      else
        # No conflict -- create symlink
        if [ "$DRY_RUN" = true ]; then
          info "${skill_name} ${DIM}would symlink${RESET}"
        else
          ln -s "$skill_src" "$link_path"
          ok "${skill_name} ${DIM}linked${RESET}"
        fi
        ((total_created++)) || true
      fi
    done
  done

  echo ""
  echo -e "${BOLD}Summary:${RESET} ${GREEN}${total_created} created/updated${RESET}, ${DIM}${total_skipped} skipped${RESET}, ${RED}${total_errors} errors${RESET}"
}

cmd_uninstall() {
  local agents=()
  local skills=()
  local line
  while IFS= read -r line; do [ -n "$line" ] && agents+=("$line"); done < <(resolve_agents)
  while IFS= read -r line; do [ -n "$line" ] && skills+=("$line"); done < <(resolve_skills)

  local total_removed=0
  local total_skipped=0

  for agent_line in "${agents[@]}"; do
    IFS='|' read -r agent_id display_name parent_dir skill_dir_name skill_dir <<< "$agent_line"

    if [ ! -d "$skill_dir" ]; then
      echo -e "${BOLD}${display_name}${RESET} ${DIM}skill dir not found, skipping${RESET}"
      continue
    fi

    echo ""
    echo -e "${BOLD}${display_name}${RESET} ${DIM}(${skill_dir})${RESET}"

    for skill_line in "${skills[@]}"; do
      IFS='|' read -r skill_name skill_src <<< "$skill_line"
      local link_path="${skill_dir}/${skill_name}"

      if [ -L "$link_path" ]; then
        local current_target
        current_target="$(readlink "$link_path")"
        if [ "$current_target" = "$skill_src" ]; then
          if [ "$DRY_RUN" = true ]; then
            info "${skill_name} ${DIM}would remove${RESET}"
          else
            rm "$link_path"
            ok "${skill_name} ${DIM}removed${RESET}"
          fi
          ((total_removed++)) || true
        else
          warn "${skill_name} ${DIM}points elsewhere (${current_target}), not ours to remove${RESET}"
          ((total_skipped++)) || true
        fi
      elif [ -e "$link_path" ]; then
        warn "${skill_name} ${DIM}real file, not a symlink -- not touched${RESET}"
        ((total_skipped++)) || true
      else
        info "${DIM}${skill_name}${RESET} ${DIM}not linked${RESET}"
        ((total_skipped++)) || true
      fi
    done
  done

  echo ""
  echo -e "${BOLD}Summary:${RESET} ${GREEN}${total_removed} removed${RESET}, ${DIM}${total_skipped} skipped${RESET}"
}

cmd_status() {
  local agents=()
  local skills=()
  local line
  while IFS= read -r line; do [ -n "$line" ] && agents+=("$line"); done < <(resolve_agents)
  while IFS= read -r line; do [ -n "$line" ] && skills+=("$line"); done < <(resolve_skills)

  echo -e "${BOLD}Central repo:${RESET} ${REPO_DIR}"
  echo ""
  echo -e "${BOLD}Skills in repo:${RESET}"
  for skill_line in "${skills[@]}"; do
    IFS='|' read -r skill_name skill_src <<< "$skill_line"
    echo -e "  ${CYAN}${skill_name}${RESET}"
  done

  echo ""
  echo -e "${BOLD}Agent links:${RESET}"
  echo ""

  for agent_line in "${agents[@]}"; do
    IFS='|' read -r agent_id display_name parent_dir skill_dir_name skill_dir <<< "$agent_line"

    echo -e "${BOLD}${display_name}${RESET} ${DIM}(${skill_dir})${RESET}"

    if [ ! -d "$skill_dir" ]; then
      echo -e "  ${DIM}skill directory does not exist${RESET}"
      continue
    fi

    for skill_line in "${skills[@]}"; do
      IFS='|' read -r skill_name skill_src <<< "$skill_line"
      local link_path="${skill_dir}/${skill_name}"

      if [ -L "$link_path" ]; then
        local target
        target="$(readlink "$link_path")"
        if [ "$target" = "$skill_src" ]; then
          echo -e "  ${GREEN}${skill_name}${RESET} ${DIM}-> ${target}${RESET}"
        else
          echo -e "  ${YELLOW}${skill_name}${RESET} ${DIM}-> ${target} ${YELLOW}(stale)${RESET}"
        fi
      elif [ -e "$link_path" ]; then
        echo -e "  ${RED}${skill_name}${RESET} ${DIM}(real file, not symlink)${RESET}"
      else
        echo -e "  ${DIM}${skill_name} (not linked)${RESET}"
      fi
    done
    echo ""
  done

  # Show agents that are not installed
  local has_missing=false
  for def in "${AGENT_DEFS[@]}"; do
    IFS='|' read -r agent_id display_name parent_dir skill_dir_name <<< "$def"
    if [ ! -d "$parent_dir" ]; then
      [ "$has_missing" = false ] && has_missing=true
      echo -e "  ${DIM}${display_name} -- not installed (${parent_dir})${RESET}"
    fi
  done
  [ "$has_missing" = true ] && echo ""
}

# ── Entry point ──────────────────────────────────────────────────────────

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}${BOLD}== DRY RUN (no changes will be made) ==${RESET}"
  echo ""
fi

case "$COMMAND" in
  install)   cmd_install ;;
  uninstall) cmd_uninstall ;;
  status)    cmd_status ;;
  *)
    err "Unknown command: $COMMAND"
    exit 1
    ;;
esac
