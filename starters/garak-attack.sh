#!/usr/bin/env bash
# L4 Attack-resistance starter for the Model Trust Gate.
#
# garak (https://github.com/NVIDIA/garak) probes a model for jailbreaks, prompt injection,
# and leakage. Tested with garak 0.17.0, which needs Python 3.11+:
#   python3 -m pip install -U "garak>=0.17"
#
# EDIT the target below for the origin you are reviewing, then run: ./garak-attack.sh
# Read the reported failure rate (the attack-success rate, ASR) against the RUNBOOK pass-bars,
# and record it in the Model Trust Record (L4 evidence). Calibrate the bar to your org.
#
# A clean run means "nothing critical survived at this strength", NOT "the model is safe".
# Any surviving critical is an L4 stop, or a conditional you must close with an L5 guardrail
# (then re-test that the guardrail drops that finding below the bar, not merely that it fires).

set -euo pipefail

# ---- pick ONE target (edit) ----
# target_type examples: ollama, huggingface, openai, rest (a generic REST endpoint).
TARGET_TYPE="${TARGET_TYPE:-ollama}"
TARGET_NAME="${TARGET_NAME:-qwen2.5:7b}"

# ---- probe set, scaled to rigor ----
# Start narrow for an R1/R2 smoke pass; widen for R3/R4. These are real garak probe modules.
#   promptinject    : direct prompt injection (goal hijacking)
#   latentinjection : indirect prompt injection hidden in content the model is asked to process
#   dan             : jailbreak / role-play bypasses
#   leakreplay      : replay of memorised training data
#   encoding        : obfuscated-payload smuggling
SPEC="${SPEC:-probes.promptinject,probes.latentinjection,probes.dan,probes.leakreplay,probes.encoding}"

echo "L4 attack battery: target_type=${TARGET_TYPE} target_name=${TARGET_NAME}"
echo "spec=${SPEC}"
echo

# An absolute prefix makes garak write the reports here instead of its own data directory.
garak \
  --target_type "${TARGET_TYPE}" \
  --target_name "${TARGET_NAME}" \
  --spec "${SPEC}" \
  --report_prefix "${PWD}/mtg-l4-attack"

echo
echo "Done. Open ./mtg-l4-attack.report.html and read the per-probe pass/fail."
echo "Record the attack-success rate and the bar you used in the Model Trust Record (L4)."
echo "For R3/R4, add a human red-team pass on top of this automated battery (see RUNBOOK)."
