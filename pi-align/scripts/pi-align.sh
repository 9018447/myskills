#!/usr/bin/env bash
# pi-align — align pi agent config across Tailscale hosts
# Usage: pi-align.sh peers | resolve <host> | diff <host> | push <host> | pull <host> | snapshot
set -euo pipefail

PI_DIR="$HOME/.pi/agent"
BACKUP_ROOT="${PI_ALIGN_BACKUP_ROOT:-$HOME/pi-backups}"
SNAP_ROOT="$BACKUP_ROOT/pi-align-snapshots"
REMOTE_USER="${PI_ALIGN_REMOTE_USER:-$USER}"
SSH_OPTS=(-o ConnectTimeout=6 -o StrictHostKeyChecking=accept-new -o BatchMode=yes)
# directories mirrored with --delete; never --delete single files
# scope: pi packages & config ONLY — skills/ is deliberately NOT managed (myskills symlinks, per-host)
# pi-hermes-memory contains machine-local state (sessions.db, retired/recovery files) —
# only the three user-preference md files are aligned, as plain files, never --delete
ALIGN_DIRS=(themes)
ALIGN_FILES=(settings.json auth.json models.json trust.json keybindings.json \
  pi-hermes-memory/MEMORY.md pi-hermes-memory/USER.md pi-hermes-memory/failures.md)
NPM_DIR=npm

die() { echo "[ERR] $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null || die "missing dependency: $1"; }

ts() { date +%Y%m%d-%H%M%S; }

# tailscale peer table: "IP  hostname" for online linux peers
peers() {
  need tailscale; need python3
  tailscale status --json | python3 -c '
import json,sys
d=json.load(sys.stdin)
for p in d.get("Peer",{}).values():
    if p.get("Online") and p.get("OS")=="linux":
        ips=p.get("TailscaleIPs") or []
        print(ips[0] if ips else "?", p.get("HostName","?"), p.get("DNSName","?").rstrip("."))
'
}

# resolve host (name, MagicDNS short label, DNS name, or IP) to a Tailscale IP
resolve() {
  local host="$1"
  peers | awk -v h="$(echo "$host" | tr '[:upper:]' '[:lower:]')" '
    { ip=$1; hn=tolower($2); dn=tolower($3); sub(/\..*/,"",dn) }  # dn first label = MagicDNS short name
    h==ip || h==hn || h==dn || h==tolower($3) { print ip; exit }
  '
}

ssh_run() { ssh "${SSH_OPTS[@]}" "$REMOTE_USER@$1" "$2"; }

# hash one file locally and remotely; echo "local_hash remote_hash"
hash_pair() {
  local ip="$1" rel="$2"
  local lh rh
  lh=$(sha256sum "$PI_DIR/$rel" 2>/dev/null | awk '{print $1}' || true)
  rh=$(ssh_run "$ip" "sha256sum '$HOME/.pi/agent/$rel' 2>/dev/null" 2>/dev/null | awk '{print $1}')
  echo "${lh:-MISSING} ${rh:-MISSING}"
}

# safety snapshot of the align set (local or remote); returns snapshot path
snapshot_local() {
  need tar; mkdir -p "$SNAP_ROOT"
  local out="$SNAP_ROOT/pi-align-local-pre-$(ts).tar.gz"
  tar czf "$out" -C "$PI_DIR" "${ALIGN_FILES[@]}" "${ALIGN_DIRS[@]}" "${NPM_DIR}/package.json" "${NPM_DIR}/package-lock.json" 2>/dev/null
  echo "$out"
}
snapshot_remote() {
  local ip="$1"
  local name="pi-align-remote-$(ssh_run "$ip" 'hostname')-pre-$(ts).tar.gz"
  ssh_run "$ip" "mkdir -p '$HOME/pi-backups/pi-align-snapshots' && tar czf '$HOME/pi-backups/pi-align-snapshots/$name' -C '$HOME/.pi/agent' ${ALIGN_FILES[*]} ${ALIGN_DIRS[*]} ${NPM_DIR}/package.json ${NPM_DIR}/package-lock.json 2>/dev/null && ls '$HOME/pi-backups/pi-align-snapshots/$name'"
  echo "remote:$HOME/pi-backups/pi-align-snapshots/$name"
}

cmd_diff() {
  local ip="$1"; shift
  local only=("$@") drift=0
  want() { local n="$1"; [[ ${#only[@]} == 0 ]] && return 0; local w; for w in "${only[@]}"; do [[ "$n" == "$w" || "$n" == "$w/" ]] && return 0; done; return 1; }
  echo "# diff vs $ip ($(ts))"
  for f in "${ALIGN_FILES[@]}" "$NPM_DIR/package.json" "$NPM_DIR/package-lock.json"; do
    want "$f" || continue
    read -r lh rh <<<"$(hash_pair "$ip" "$f")"
    if [[ "$lh" == "$rh" ]]; then st=SAME
    elif [[ "$lh" == MISSING || "$rh" == MISSING ]]; then st=MISSING
    else st=DRIFT; fi
    [[ $st == SAME ]] || drift=$((drift+1))
    printf '%-8s %s\n' "$st" "$f"
  done
  for d in "${ALIGN_DIRS[@]}"; do
    want "$d/" || continue
    local out
    out=$(rsync -rlpgoDnc --itemize-changes --delete \
      -e "ssh ${SSH_OPTS[*]}" --exclude='__pycache__/' --exclude='*.pyc' \
      "$PI_DIR/$d/" "$REMOTE_USER@$ip:$HOME/.pi/agent/$d/" 2>/dev/null || true)
    local n=0
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      if [[ $n == 0 ]]; then
        if [[ "$d" == pi-hermes-memory ]]; then st=DRIFT; else st=DRIFT; fi
        drift=$((drift+1))
        printf '%-8s %s/\n' "$st" "$d"
      fi
      echo "    $line"
      n=$((n+1))
    done <<< "$out"
    [[ $n == 0 ]] && printf '%-8s %s/\n' SAME "$d"
  done

  [[ $drift == 0 ]]
}

cmd_push() {
  local ip="$1"; shift
  local only=("$@")
  want() { local n="$1"; [[ ${#only[@]} == 0 ]] && return 0; local w; for w in "${only[@]}"; do [[ "$n" == "$w" || "$n" == "$w/" ]] && return 0; done; return 1; }
  local allfiles=("${ALIGN_FILES[@]}")
  local npmfiles=("$NPM_DIR/package.json" "$NPM_DIR/package-lock.json")
  need rsync; need tar
  echo "== pre-snapshots"
  local lsnap rsnap
  lsnap=$(snapshot_local) || die "local pre-snapshot failed"
  echo "local : $lsnap"
  rsnap=$(snapshot_remote "$ip") || die "remote pre-snapshot failed"
  echo "remote: $rsnap"
  RSYNC_SSH="ssh ${SSH_OPTS[*]}"
  echo "== files"
  for f in "${allfiles[@]}" "${npmfiles[@]}"; do
    want "$f" || continue
    rsync -c -e "$RSYNC_SSH" "$PI_DIR/$f" "$REMOTE_USER@$ip:$HOME/.pi/agent/$f"
  done
  echo "== dirs (mirror)"
  for d in "${ALIGN_DIRS[@]}"; do
    want "$d/" || continue
    rsync -rlpgoDc --delete -e "$RSYNC_SSH" --exclude='__pycache__/' --exclude='*.pyc' \
      "$PI_DIR/$d/" "$REMOTE_USER@$ip:$HOME/.pi/agent/$d/"
  done
  if [[ ${#only[@]} == 0 ]] || want "$NPM_DIR/package.json"; then
    echo "== remote npm install"
    ssh_run "$ip" "cd '$HOME/.pi/agent/npm' && npm install --no-audit --no-fund --legacy-peer-deps --loglevel=error" || die "remote npm install failed"
  fi
  echo "== verify"
  cmd_diff "$ip" "${only[@]}" || die "post-push diff still shows drift"
  echo "push complete: $ip (${only[*]:-full set})"
}

cmd_pull() {
  local ip="$1"; shift
  local only=("$@")
  want() { local n="$1"; [[ ${#only[@]} == 0 ]] && return 0; local w; for w in "${only[@]}"; do [[ "$n" == "$w" || "$n" == "$w/" ]] && return 0; done; return 1; }
  local npmfiles=("$NPM_DIR/package.json" "$NPM_DIR/package-lock.json")
  need rsync; need tar
  echo "== pre-snapshots"
  local lsnap rsnap
  lsnap=$(snapshot_local) || die "local pre-snapshot failed"
  echo "local : $lsnap"
  rsnap=$(snapshot_remote "$ip") || die "remote pre-snapshot failed"
  echo "remote: $rsnap"
  RSYNC_SSH="ssh ${SSH_OPTS[*]}"
  echo "== files"
  for f in "${ALIGN_FILES[@]}" "${npmfiles[@]}"; do
    want "$f" || continue
    rsync -c -e "$RSYNC_SSH" "$REMOTE_USER@$ip:$HOME/.pi/agent/$f" "$PI_DIR/$f"
  done
  echo "== dirs (mirror)"
  for d in "${ALIGN_DIRS[@]}"; do
    want "$d/" || continue
    rsync -rlpgoDc --delete -e "$RSYNC_SSH" --exclude='__pycache__/' --exclude='*.pyc' \
      "$REMOTE_USER@$ip:$HOME/.pi/agent/$d/" "$PI_DIR/$d/"
  done
  if [[ ${#only[@]} == 0 ]] || want "$NPM_DIR/package.json"; then
    echo "== local npm install"
    (cd "$PI_DIR/npm" && npm install --no-audit --no-fund --legacy-peer-deps --loglevel=error) || die "local npm install failed"
  fi
  echo "== verify"
  cmd_diff "$ip" "${only[@]}" || die "post-pull diff still shows drift"
  echo "pull complete: from $ip"
}

cmd_snapshot() {
  local PB="$HOME/.pi/agent/npm/node_modules/@jamiefutch/pi-backup/backup-pi.sh"
  [[ -x "$PB" ]] || PB="${PI_BACKUP_SCRIPT:-}"
  [[ -n "$PB" && -f "$PB" ]] || die "pi-backup backup-pi.sh not found; set PI_BACKUP_SCRIPT"
  BACKUP_ROOT="$BACKUP_ROOT" bash "$PB"
}

case "${1:-}" in
  peers)    peers ;;
  resolve)  [[ $# == 2 ]] || die "usage: $0 resolve <host>"; resolve "$2" | grep . || die "no online tailscale peer matches: $2" ;;
  diff)     [[ $# -ge 2 ]] || die "usage: $0 diff <host> [items...]"; ip=$(resolve "$2") || true; [[ -n "${ip:-}" ]] || die "cannot resolve $2 to a tailscale IP"; shift 2; cmd_diff "$ip" "$@" ;;
  push)     [[ $# -ge 2 ]] || die "usage: $0 push <host> [items...]"; ip=$(resolve "$2") || true; [[ -n "${ip:-}" ]] || die "cannot resolve $2 to a tailscale IP"; shift 2; cmd_push "$ip" "$@" ;;
  pull)     [[ $# -ge 2 ]] || die "usage: $0 pull <host> [items...]"; ip=$(resolve "$2") || true; [[ -n "${ip:-}" ]] || die "cannot resolve $2 to a tailscale IP"; shift 2; cmd_pull "$ip" "$@" ;;
  snapshot) cmd_snapshot ;;
  *)        die "usage: $0 peers|resolve <host>|diff <host>|push <host>|pull <host>|snapshot" ;;
esac
