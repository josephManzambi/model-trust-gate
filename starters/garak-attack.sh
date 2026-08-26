#!/usr/bin/env bash
# L4 Attack-resistance starter for the Model Trust Gate.
#
# garak (https://github.com/NVIDIA/garak) probes a model for jailbreaks, prompt injection,
# and leakage. Install: pip install garak
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
# model_type examples: ollama, huggingface, openai, rest (a generic REST endpoint).
MODEL_TYPE="${MODEL_TYPE:-ollama}"
MODEL_NAME="${MODEL_NAME:-qwen2.5:7b}"

# ---- probe set, scaled to rigor ----
# Start narrow for an R1/R2 smoke pass; widen for R3/R4. These are real garak probe modules.
#   promptinject : direct and indirect prompt-injection attempts
#   dan          : jailbreak / role-play bypasses
#   leakreplay   : training-data and prompt leakage
#   encoding     : obfuscated-payload smuggling
PROBES="${PROBES:-promptinject,dan,leakreplay,encoding}"

echo "L4 attack battery: model_type=${MODEL_TYPE} model_name=${MODEL_NAME}"
echo "probes=${PROBES}"
echo

garak \
  --model_type "${MODEL_TYPE}" \
  --model_name "${MODEL_NAME}" \
  --probes "${PROBES}" \
  --report_prefix mtg-l4-attack

echo
echo "Done. Open mtg-l4-attack.report.html and read the per-probe pass/fail."
echo "Record the attack-success rate and the bar you used in the Model Trust Record (L4)."
echo "For R3/R4, add a human red-team pass on top of this automated battery (see RUNBOOK)."
