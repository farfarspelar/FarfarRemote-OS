#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/debloat_common.sh"

GROUP=ALL
APPLY=0
APPROVED=0
usage() {
  cat <<'EOF'
Restore only packages previously disabled by tools/debloat.sh for this audited E2003.

Usage:
  tools/restore.sh [--group A|B|C|D|ALL]          # dry-run
  tools/restore.sh --group A|B|C|D|ALL --apply --approve

Restoration uses `pm enable --user 0`; no package is installed or removed.
EOF
}
while (($#)); do
  case "$1" in
    --group) (($# >= 2)) || dr_die "--group needs A/B/C/D/ALL"; GROUP="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    --approve) APPROVED=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) dr_die "unknown option: $1" ;;
  esac
done
[[ "$GROUP" =~ ^(A|B|C|D|ALL)$ ]] || dr_die "group must be A, B, C, D, or ALL"
dr_latest_audit
chmod 700 "$DR_STATE" "$DR_STATE/metrics"
actions="$DR_STATE/actions.tsv"
if [[ ! -s "$actions" ]]; then printf 'No debloat actions recorded for audited E2003 %s.\n' "$DR_SERIAL"; exit 0; fi

declare -a entries=()
if [[ "$GROUP" == ALL ]]; then
  mapfile -t entries < <(awk -F'\t' '$2=="DISABLE" && ($5=="DISABLED" || $5=="PENDING") {print $3 "\t" $4}' "$actions" | tac)
else
  mapfile -t entries < <(awk -F'\t' -v g="$GROUP" '$2=="DISABLE" && $3==g && ($5=="DISABLED" || $5=="PENDING") {print $3 "\t" $4}' "$actions" | tac)
fi
declare -A seen=()
declare -a pending=()
for entry in "${entries[@]}"; do
  IFS=$'\t' read -r g pkg <<< "$entry"
  [[ -n "$pkg" && -z "${seen[$g:$pkg]:-}" ]] || continue
  seen[$g:$pkg]=1
  status="$(dr_latest_package_status "$g" "$pkg")"
  if [[ "$status" == DISABLED || "$status" == PENDING ]]; then
    printf -v row '%s\t%s\t%s' "$g" "$pkg" "$status"
    pending+=("$row")
  fi
done
if ((${#pending[@]} == 0)); then printf 'Nothing to restore for group %s.\n' "$GROUP"; exit 0; fi

printf 'Audited device: %s / E2003\nMode: %s\n' "$DR_SERIAL" "$([[ "$APPLY" == 1 ]] && echo APPLY || echo DRY-RUN)"
printf '| Phase | Package | Current action-log state |\n|---|---|---|\n'
for entry in "${pending[@]}"; do
  IFS=$'\t' read -r g pkg status <<< "$entry"
  printf '| %s | `%s` | %s by this tool |\n' "$g" "$pkg" "$status"
done
if [[ "$APPLY" == 0 ]]; then printf '\nNo package state changed. Use --apply --approve to re-enable only this list.\n'; exit 0; fi
[[ "$APPROVED" == 1 ]] || dr_die "restore requires --approve"
dr_device_check
printf 'Type exactly RESTORE E2003 GROUP %s: ' "$GROUP"
IFS= read -r confirmation || dr_die "no confirmation received"
[[ "$confirmation" == "RESTORE E2003 GROUP $GROUP" ]] || dr_die "confirmation did not match; no changes made"
before="$(dr_metric_snapshot "pre-restore-$GROUP")"
printf 'Pre-restore metrics: %s\n' "$before"
for entry in "${pending[@]}"; do
  IFS=$'\t' read -r g pkg status <<< "$entry"
  dr_device_check
  if dr_package_disabled "$pkg"; then
    output="$(dr_shell pm enable --user 0 "$pkg" 2>&1)"
    dr_device_check
    if dr_package_disabled "$pkg"; then
      dr_log_event RESTORE "$g" "$pkg" ERROR "still disabled; $output"
      dr_die "restore verification failed for $pkg; leave USB connected and inspect package state"
    fi
    dr_log_event RESTORE "$g" "$pkg" RESTORED "pm enable --user 0; $output"
    printf 'Re-enabled: %s\n' "$pkg"
  else
    dr_log_event RESTORE "$g" "$pkg" ALREADY_ENABLED "no device change"
  fi
done
dr_device_check
after="$(dr_metric_snapshot "post-restore-$GROUP")"
printf 'Post-restore metrics: %s\n' "$after"
for entry in "${pending[@]}"; do IFS=$'\t' read -r g _ <<< "$entry"; dr_log_phase "$g" RESTORED "package(s) re-enabled by restore.sh"; done
printf 'Restore complete. Run the regression checklist in reports/debloat/README.md.\n'
