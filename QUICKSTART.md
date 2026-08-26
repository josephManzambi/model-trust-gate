# Quickstart: from "a team brought us a model" to a signed record

*The one-afternoon path. It threads the parts you actually run and links each step to the file that carries the detail. Read [FRAMEWORK.md](FRAMEWORK.md) once for the why; you do not need it open to follow this.*

You are deciding whether to trust **one model, for one use**, and producing a signed record you can defend. Seven checks, cheapest first, fail-fast.

## 1. Intake (10 minutes)

Copy the intake block from [RUNBOOK.md](RUNBOOK.md) ("Step 0") into the ticket and fill it. The four capability rows (autonomy, agency, data, impact) are the rigor drivers you will use next. If a field cannot be answered, that is itself an L0/L2 finding.

## 2. Triage: set the Rigor Level (5 minutes)

Take the **highest** level any single driver reaches (RUNBOOK "Step 1"): R1 low, R4 highest. Add the **regulatory floor** (EU AI Act high-risk, sector rules): a floor raises rigor regardless of the drivers. Result: `Rigor: Rn, Floor: ...`.

## 3. Pick a track (1 minute)

- **Fast track** if R1/R2, cloud or hosted-open-weight, unmodified, no floor: same gate, the expensive high-rigor steps omitted.
- **Full track** otherwise (R3/R4, or downloaded, or modified, or any floor): every layer at full strength, an approver independent of the requesting team, and a human red-team at L4.

The moment a fast-track assumption breaks (a modification appears, L3/L4 reveals a higher-stakes capability), fall back to the full track.

## 4. Run the gate, layer by layer

Work the per-layer checklist in [RUNBOOK.md](RUNBOOK.md). The governance layers (L0 to L2) are cheap and come first, so an early **stop** saves the expensive testing. For the two technical layers, use the starter kit so you are running, not assembling:

- **L3 Behavior:** [`starters/promptfoo-behavior.yaml`](starters/promptfoo-behavior.yaml). Refusal correctness, over-refusal, grounding. Read against the RUNBOOK pass-bars.
- **L4 Attack resistance:** [`starters/garak-attack.sh`](starters/garak-attack.sh). Jailbreak, injection, leakage. Read the attack-success rate against the bar; add a human red-team at R3/R4.

Each layer ends in **pass**, **conditional** (allowed once a named L5 control closes a specific finding), or **stop** (a Deny that ends the run).

## 5. Guardrails and hand-off (L5, L6, Exit Gate)

For each **conditional**, add the L5 control that closes that finding and **test it drops the finding below the bar**, not merely that it fires. Set the re-check triggers and expiry at L6. Hand any system-level risk the gate flagged but did not test (knowledge base, orchestration) to the Exit Gate.

## 6. Fill and sign the record

Copy the blank [`templates/model-trust-record.template.json`](templates/model-trust-record.template.json) and fill it as you go (or the human-readable [`templates/model-trust-record.md`](templates/model-trust-record.md)). The verdict follows from the layers:

- all layers pass, no control needed: **Allow**
- every conditional closed by a verified L5 control: **Allow with controls**
- a conditional resolved only by narrowing the use: **Restrict** (record the narrower use)
- any stop, or a conditional L5 cannot close: **Deny**

Sign it, store it append-only. The [JSON schema](templates/model-trust-record.schema.json) lets a policy engine gate deployment on the record's invariants.

## Worked examples to copy from

- [runbooks/bedrock-hosted-open-weight.md](runbooks/bedrock-hosted-open-weight.md): an open model (Qwen, Llama) via a cloud provider. The common case.
- [runbooks/fine-tuned-open-weight.md](runbooks/fine-tuned-open-weight.md): an open model you fine-tuned in house.

Both go intake to signed record and end in a filled example ([bedrock](templates/model-trust-record.bedrock-example.json), [fine-tuned](templates/model-trust-record.fine-tuned-example.json)).
