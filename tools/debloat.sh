#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/debloat_common.sh"

PHASE=ALL
APPLY=0
APPROVED=0
ALLOW_REVIEWED=0
BATCH_SIZE=5
MEASURE_LABEL=""
BOOT_LABEL=""
BOOT_SECONDS=""

usage() {
  cat <<'EOF'
FarfarRemote OS Debloat 0.1 — dry-run is the default; package actions are reversible per Android user.

Usage:
  tools/debloat.sh [--phase A|B|C|D|ALL] [--dry-run]
  tools/debloat.sh --measure baseline|after-A|after-B|after-C|after-D
  tools/debloat.sh --phase A|B|C|D --apply --approve-phase PHASE [--allow-reviewed]
  tools/debloat.sh --phase C --apply --approve-phase C --batch-size 1
  tools/debloat.sh --record-boot-seconds baseline|after-A|after-B|after-C|after-D SECONDS

Apply still requires typing the exact device/phase confirmation and manually passing
regression checks. Phase D requires --allow-reviewed and is not recommended for the
first trial. No uninstall, root, /system write, flash, or reboot command is used.
EOF
}
while (($#)); do
  case "$1" in
    --phase) (($# >= 2)) || dr_die "--phase needs a value"; PHASE="$2"; shift 2 ;;
    --dry-run) APPLY=0; shift ;;
    --apply) APPLY=1; shift ;;
    --approve-phase) (($# >= 2)) || dr_die "--approve-phase needs A/B/C/D"; [[ "$2" == "$PHASE" ]] || dr_die "approval phase must match --phase"; APPROVED=1; shift 2 ;;
    --allow-reviewed) ALLOW_REVIEWED=1; shift ;;
    --batch-size) (($# >= 2)) || dr_die "--batch-size needs 1..5"; BATCH_SIZE="$2"; shift 2 ;;
    --measure) (($# >= 2)) || dr_die "--measure needs a label"; MEASURE_LABEL="$2"; shift 2 ;;
    --record-boot-seconds) (($# >= 3)) || dr_die "--record-boot-seconds needs label and seconds"; BOOT_LABEL="$2"; BOOT_SECONDS="$3"; shift 3 ;;
    -h|--help) usage; exit 0 ;;
    *) dr_die "unknown option: $1" ;;
  esac
done

dr_latest_audit
chmod 700 "$DR_STATE" "$DR_STATE/metrics"
if [[ -n "$MEASURE_LABEL" ]]; then
  [[ "$MEASURE_LABEL" =~ ^(baseline|after-[A-D])$ ]] || dr_die "measure label must be baseline or after-A/B/C/D"
  dr_device_check
  path="$(dr_metric_snapshot "$MEASURE_LABEL")"
  printf 'Snapshot saved: %s\n' "$path"
  exit 0
fi
if [[ -n "$BOOT_LABEL" ]]; then
  [[ "$BOOT_LABEL" =~ ^(baseline|after-[A-D])$ ]] || dr_die "boot label must be baseline or after-A/B/C/D"
  [[ "$BOOT_SECONDS" =~ ^[0-9]+([.][0-9]+)?$ ]] || dr_die "seconds must be a numeric stopwatch value"
  printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$BOOT_LABEL" "$BOOT_SECONDS" >> "$DR_STATE/boot_times.tsv"
  printf 'Recorded manual cold-boot time: %s = %s seconds\n' "$BOOT_LABEL" "$BOOT_SECONDS"
  exit 0
fi
[[ "$PHASE" =~ ^(A|B|C|D|ALL)$ ]] || dr_die "phase must be A, B, C, D, or ALL"
[[ "$BATCH_SIZE" =~ ^[1-5]$ ]] || dr_die "batch size is limited to 1..5 packages per regression round"

installed_in_audit() {
  awk -F'\t' -v p="$1" 'index($0,"package:") {v=substr($0,index($0,"package:")+8); sub(/\r/,"",v); sub(/^.*=/,"",v); if(v==p) found=1} END{exit !found}' "$DR_AUDIT_DIR/packages_all.txt"
}
print_plan() {
  local requested="$1" phase pkg fun risk eligible evidence recommendation n=0
  printf 'Audit: %s (serial %s; E2003)\n' "$(basename "$DR_AUDIT_DIR")" "$DR_SERIAL"
  printf 'Mode: %s\n\n' "$([[ "$APPLY" == 1 ]] && echo APPLY || echo DRY-RUN)"
  printf '| Phase | Package | Risk | Status | Function / evidence |\n|---|---|---|---|---|\n'
  while IFS=$'\t' read -r phase pkg fun risk eligible evidence recommendation; do
    [[ "$phase" == "phase" || -z "$phase" ]] && continue
    [[ "$requested" == ALL || "$requested" == "$phase" ]] || continue
    installed_in_audit "$pkg" || continue
    local status="$eligible"
    [[ "$eligible" == NEVER ]] && status="protected — never auto-disable"
    [[ "$eligible" == REVIEW ]] && status="deferred — requires --allow-reviewed"
    printf '| %s | `%s` | %s | %s | %s |\n' "$phase" "$pkg" "$risk" "$status" "$fun — $evidence"
    ((n+=1))
  done < "$DR_CANDIDATES"
  printf '\n%d package rows shown. Dry-run does not require a connected phone and makes no changes.\n' "$n"
}

if [[ "$APPLY" == 0 ]]; then
  print_plan "$PHASE"
  printf '\nFor valid OS metrics, close the regular App flavor and let the device settle idle for five minutes with the intended screen, Wi-Fi, Kodi and charger conditions.\n'
  printf 'Recommended flow: ./tools/debloat.sh --measure baseline ; record stopwatch cold boot; dry-run Phase A; then apply A only after review.\n'
  exit 0
fi

[[ "$PHASE" != ALL ]] || dr_die "ALL is dry-run only; apply exactly one phase at a time"
[[ "$APPROVED" == 1 ]] || dr_die "apply requires --approve-phase $PHASE"
if [[ "$PHASE" == D && "$ALLOW_REVIEWED" != 1 ]]; then dr_die "Phase D contains reviewed/high-risk entries; pass --allow-reviewed only after reviewing package_review.md"; fi
[[ -f "$DR_STATE/actions.tsv" ]] || : > "$DR_STATE/actions.tsv"
[[ -f "$DR_STATE/phases.tsv" ]] || : > "$DR_STATE/phases.tsv"
if [[ "$PHASE" != A ]]; then
  previous="$(printf '%s' "$PHASE" | tr 'BCD' 'ABC')"
  [[ "$(dr_latest_phase_status "$previous")" == PASS ]] || dr_die "Phase $previous must first be fully applied and all regression rounds marked PASS"
fi
dr_baseline_exists || dr_die "collect a before-change baseline first: tools/debloat.sh --measure baseline"
dr_device_check
pmhelp="$(dr_shell pm help 2>&1 || true)"
grep -q 'disable-user' <<< "$pmhelp" || dr_die "this package manager does not advertise reversible pm disable-user; no changes made"

print_plan "$PHASE"
declare -a packages=()
while IFS=$'\t' read -r phase pkg fun risk eligible evidence recommendation; do
  [[ "$phase" == "$PHASE" ]] || continue
  [[ "$eligible" == YES || ( "$eligible" == REVIEW && "$ALLOW_REVIEWED" == 1 ) ]] || continue
  [[ "$risk" != CRITICAL ]] || continue
  dr_protected_package "$pkg" && dr_die "internal protected-package block: $pkg"
  dr_package_installed "$pkg" || { printf 'Skip absent package: %s\n' "$pkg"; continue; }
  state="$(dr_latest_package_status "$PHASE" "$pkg")"
  [[ "$state" != DISABLED && "$state" != ALREADY_DISABLED ]] || continue
  packages+=("$pkg")
  ((${#packages[@]} < BATCH_SIZE)) || break
done < "$DR_CANDIDATES"
if ((${#packages[@]} == 0)); then
  if [[ "$(dr_latest_phase_status "$PHASE")" == PASS ]]; then
    printf 'Phase %s is already complete and passed all regression rounds.\n' "$PHASE"; exit 0
  fi
  dr_die "no remaining enabled candidates in phase $PHASE; inspect action log and restore/mark the phase manually"
fi

printf '\nThis round will reversibly disable these %s package(s) for Android user 0: %s\n' "${#packages[@]}" "${packages[*]}"
printf 'It will not erase APKs/data or write /system. Restore is via tools/restore.sh.\n'
printf 'Type exactly DISABLE E2003 PHASE %s to continue: ' "$PHASE"
IFS= read -r confirmation || dr_die "no confirmation received"
[[ "$confirmation" == "DISABLE E2003 PHASE $PHASE" ]] || dr_die "confirmation did not match; no package changes made"

before="$(dr_metric_snapshot "pre-$PHASE")"
printf '\nPre-change metrics: %s\n' "$before"
dr_log_phase "$PHASE" APPLYING "approved candidate list recorded in actions.tsv"
for pkg in "${packages[@]}"; do
  dr_device_check
  dr_protected_package "$pkg" && dr_die "protected package guard blocked $pkg"
  if dr_package_disabled "$pkg"; then
    dr_log_event DISABLE "$PHASE" "$pkg" ALREADY_DISABLED "pre-existing state; will not claim/restore it"
    continue
  fi
  dr_log_event DISABLE "$PHASE" "$pkg" PENDING "enabled before this tool issued pm disable-user; verify/restore if ADB drops"
  cmd_output="$(dr_shell pm disable-user --user 0 "$pkg" 2>&1)" || {
    dr_log_event DISABLE "$PHASE" "$pkg" ERROR "$cmd_output"
    dr_log_phase "$PHASE" PARTIAL "disable command failed; inspect and run restore.sh after ADB is stable"
    dr_die "disable failed at $pkg; stop here and use tools/restore.sh --group $PHASE --apply"
  }
  dr_device_check
  if ! dr_package_disabled "$pkg"; then
    dr_log_event DISABLE "$PHASE" "$pkg" ERROR "command returned but package not in disabled list: $cmd_output"
    dr_log_phase "$PHASE" PARTIAL "package state uncertain"
    dr_die "could not verify disabled state for $pkg; use restore.sh after checking the device"
  fi
  dr_log_event DISABLE "$PHASE" "$pkg" DISABLED "pm disable-user --user 0; $cmd_output"
  printf 'Disabled for user 0: %s\n' "$pkg"
done
dr_device_check
after="$(dr_metric_snapshot "post-$PHASE")"
printf '\nPost-change metrics: %s\n' "$after"
dr_log_phase "$PHASE" PENDING_TEST "complete manual regression checklist before continuing"

printf '\nRun the manual checks now. For each, enter PASS or FAIL. Bluetooth can be N/A only if not used.\n'
tests=("FarfarRemote starts as HOME, renders and accepts touch/navigation" "Kodi connects; play/pause, stop, back, home and volume work" "Wi-Fi remains connected and Settings can enter/change a network" "Touchscreen and physical buttons respond" "USB charging and power/screen wake behavior are normal" "Bluetooth pairing/control works, or is deliberately unused" "ADB stays connected and adb install -r of the current APK succeeds")
labels=(farfarremote kodi wifi input power bluetooth adb_apk)
fail=0
for i in "${!tests[@]}"; do
  while true; do
    printf '%s — [PASS/FAIL%s]: ' "${tests[$i]}" "$([[ "${labels[$i]}" == bluetooth ]] && echo '/N/A' || true)"
    IFS= read -r result || dr_die "no regression result entered"
    result="${result^^}"
    if [[ "$result" == PASS || "$result" == FAIL || ( "$result" == N/A && "${labels[$i]}" == bluetooth ) ]]; then break; fi
    printf 'Use PASS or FAIL; N/A is allowed only for Bluetooth.\n'
  done
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$PHASE" "${labels[$i]}" "$result" >> "$DR_STATE/regression.tsv"
  [[ "$result" == FAIL ]] && fail=1
done

if ((fail)); then
  printf '\nAt least one regression failed; restoring only packages disabled by this script in Phase %s.\n' "$PHASE"
  dr_restore_group "$PHASE"
  rollback="$(dr_metric_snapshot "rollback-$PHASE")"
  dr_log_phase "$PHASE" ROLLED_BACK "regression failure; re-enabled script-owned package changes"
  printf 'Rollback metrics: %s\n' "$rollback"
  exit 1
fi
dr_device_check
remaining=0
while IFS=$'\t' read -r check_phase check_pkg _ _ check_eligibility _ _; do
  [[ "$check_phase" == "$PHASE" ]] || continue
  [[ "$check_eligibility" == YES || ( "$check_eligibility" == REVIEW && "$ALLOW_REVIEWED" == 1 ) ]] || continue
  installed_in_audit "$check_pkg" || continue
  check_state="$(dr_latest_package_status "$PHASE" "$check_pkg")"
  [[ "$check_state" == DISABLED || "$check_state" == ALREADY_DISABLED ]] || ((remaining+=1))
done < "$DR_CANDIDATES"
if ((remaining == 0)); then
  dr_log_phase "$PHASE" PASS "all packages handled and all regression rounds passed"
  printf '\nPhase %s is complete: all candidates handled and all regression rounds passed. Record cold boot after manual power-off/start with:\n' "$PHASE"
  printf './tools/debloat.sh --record-boot-seconds after-%s SECONDS\n' "$PHASE"
else
  dr_log_phase "$PHASE" ROUND_PASS "$remaining candidate package(s) remain; this round passed"
  printf '\nPhase %s round passed; %s candidate package(s) remain. Run another round after reviewing the results.\n' "$PHASE" "$remaining"
fi
printf 'No reboot was initiated automatically. Review metrics with tools/analyze_debloat_metrics.py.\n'
