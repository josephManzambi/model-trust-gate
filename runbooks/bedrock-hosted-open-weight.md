# Worked runbook: a hosted open-weight model (Qwen on AWS Bedrock, first time)

*This is the most common request a platform team gets today: "we want to use an open model (Qwen, Llama) through Bedrock." It is neither of the textbook origins. The provider holds the files (so the file-level supply chain nearly vanishes, like a cloud API), but the model arrives with far thinner inherited safety testing than a frontier lab's (so your own testing carries more weight). This runbook walks that case end to end and ends in a signed [Model Trust Record](../templates/model-trust-record.bedrock-example.json). It is the operational companion to Test 5 in [VALIDATION.md](../VALIDATION.md).*

**Scenario.** A team wants a **Qwen** model served through **AWS Bedrock** to power an **internal knowledge assistant**: staff ask questions over internal documents. Read-only, cannot take actions. First time using this model and this model family.

---

## Step 0: Intake

```
Requesting team:      Internal Tools
Model:                Qwen2.5-72B-Instruct
Version / variant:    Bedrock model id qwen.qwen2-5-72b-instruct-v1:0 (pin at approval)
Origin:               hosted open-weight   (open model via a cloud provider)
Use case:             Internal knowledge assistant over internal docs
Can it take actions?  no (read-only)
What can it touch?     read-only
Data it sees:          internal (some sensitive)
Impact of output: none material (advisory, human reads the answer)
Modified by us?        no
Jurisdictions / laws:  EU AI Act: internal, not Annex III -> no regulatory floor
```

## Step 1: Triage

| Driver | Value | Level |
|---|---|---|
| Autonomy | read-only, human-initiated | R1 |
| Agency | read-only | R1 |
| Data | some internal / sensitive | R2 |
| Impact | none material | R1 |

Highest driver → **R2**. Regulatory floor: **none**. → `Rigor: R2 · Floor: none`.

## Step 2: Track

R2 + hosted open-weight + unmodified + no floor → **fast track**. One reviewer, on the order of a day or two (the first-time L3/L4 testing is the bulk of it; see effort sizing in [RUNBOOK.md](../RUNBOOK.md)).

---

## The run, layer by layer

### L0: Set the stakes → **pass (R2)**
Use is internal, advisory, read-only. Not a prohibited practice. Rigor R2 carried forward.

### L1: Provenance & supply chain → **pass**
The pivot of this whole case. Because AWS holds and runs the weights, there is **no file on your disk**, no malware scan, no format check, no checksum. That supply-chain surface is absorbed by the provider, exactly as for any cloud model.
- [x] AWS security posture on file (SOC 2, ISO 27001).
- [x] Confirm the **exact** Bedrock model id and version served, and pin it. ("Qwen on Bedrock" is not specific enough; `qwen.qwen2-5-72b-instruct-v1:0` is.)
- [x] Provider model card reviewed.

Light. The extra scrutiny a first-time open-lineage model deserves has moved to L2 and L3/L4, not L1.

### L2: Permission & governance → **conditional, then resolved to pass**
This is where a first-time, third-party, open-lineage model earns its scrutiny.
- [x] Bedrock data terms confirmed: in-region, and inputs/outputs not used to train base models.
- [x] EU AI Act role: **deployer** (we did not modify the model). Internal use, not Annex III → no floor.
- [x] ISO/IEC 42001 AI System Impact Assessment run (ref AISEC-611).
- [x] Mapped to CSA AICM: GRC-10 (impact assessment), STA-09 (supply-chain/provider risk), MDS-12 (open model risk assessment), A&A-04 (requirements compliance). See [standards-crosswalk.md](../standards-crosswalk.md).
- [ ] → **[x]** **First-time origin + data-governance sign-off.** Adopting a model of this provenance for internal (some sensitive) data is a policy decision in its own right. Raised as a **conditional** here; **resolved** once the sign-off is obtained (AISEC-611), at which point L2 is recorded **pass**.

> This is the governance pattern for the whole framework: a conditional at a governance layer is a *named fix* (a sign-off, a contract amendment, a region change). When the fix lands, the layer is recorded `pass`, with the fix captured in the record's evidence. Only L3/L4 conditionals are carried as conditionals into the final record and closed by an L5 control.

### L3: Behavior → **pass (R2)**
First time with this family, so **no prior baseline to diff against**, run the full behavior suite yourself.
- [x] `promptfoo` / `DeepEval`: refusal correctness, bias, hallucination on in-scope questions, instruction-following. Met the R2 default bars (refusal ≥ 95%, hallucination ≤ 5%; see RUNBOOK pass-bars).
- [x] Read the model card; label its safety testing **inherited (vendor's)** and note it is thinner than a frontier lab's, so weight your own "ours" evidence accordingly.

### L4: Attack resistance → **conditional (one residual finding, closed at L5)**
- [x] Automated attack battery at **R2** strength (`garak`, `promptfoo`, `PyRIT`): jailbreaks, direct + indirect prompt injection (the injection surface matters for a doc-reading assistant), instruction/data leakage. No critical survived.
- The one residual: **indirect prompt injection via document content (finding L4-F1).** No critical jailbreak survived, but a doc-reading assistant's injection surface is a real weakness, so it is carried as a **conditional** and closed by the L5 guardrail rather than left open. (This is why L4 is `conditional`, not `pass`: the honest verdict for "the model is fine, but only because a runtime control contains a specific finding.")
- [x] Honesty rule recorded: a clean R2 run is not proof of safety, only that nothing critical survived testing at this strength.

### L5: Guardrails → **pass**
- [x] Attach **Bedrock Guardrails** on input **and** output. This **closes L4-F1** (the indirect-injection finding) and deliberately adds a runtime safety layer back at the platform level, the thing you would otherwise lose relative to a frontier vendor's built-in safety.
- [x] **Verify it fires** against the paths L3/L4 exercised (not merely that it is enabled). Version it (`gr-bedrock-guardrail-io` v1) and record the re-test date.

Because L4 carried a conditional (the indirect-injection finding L4-F1) that this L5 control verifiably closes, the overall verdict is **Allow with controls**, not a bare Allow. (If L4 had been a clean `pass` with no finding, the verdict would be a bare **Allow** and this defense-in-depth guardrail would be noted separately; the total rule keys "Allow with controls" on a conditional that a control closes.)

### L6: Upkeep → recorded
- [x] Pin the served model id and version.
- [x] Re-check trigger: **the provider updates the served model version** (Bedrock can move a model under the same friendly name, pin the versioned id).
- [x] Expiry: 180 days (R2 default) → **2027-02-21**.
- [x] Incident owner + notification deadline recorded.

### Exit Gate → RTD-611, accepted
The model gate judged the model. Handed to the system review (RTD-611, accepted by the system-review owner): the **RAG/knowledge-base layer's** exposure to content poisoning (gap G1, the model gate flags it, does not test it), and the dependency on the Bedrock Guardrail staying configured.

---

## The result

**Allow with controls · R2 · hosted open-weight.** The full signed record is [`templates/model-trust-record.bedrock-example.json`](../templates/model-trust-record.bedrock-example.json) (validates against [`model-trust-record.schema.json`](../templates/model-trust-record.schema.json)); the human-readable form:

```
Model Trust Record
------------------
Model:            Qwen2.5-72B-Instruct (open-lineage, via AWS Bedrock) @ qwen.qwen2-5-72b-instruct-v1:0, pinned 2026-08-25
Origin:           hosted open-weight (open model via a cloud provider)
Modified:         no
Use case:         Internal knowledge assistant over internal docs; read-only, cannot act
Scrutiny level:   R2      Regulatory floor: none
Impact assessment: ISO 42001 AISIA AISEC-611; no FRIA (Art. 27 does not apply)
Per-layer result: L0 pass · L1 pass · L2 pass · L3 pass · L4 conditional · L5 pass
Overall:          Allow with controls
Controls added:   Bedrock Guardrails on input+output (gr-bedrock-guardrail-io v1), closes L4-F1, verified to fire
                  against the paths L3/L4 exercised.
Evidence:         L1 AWS SOC 2 / ISO 27001 (vendor's); L2 first-time origin + data-governance
                  sign-off (ours); L3 behavior scorecard (ours, T2) + model card (vendor's, inherited);
                  L4 R2 red-team, no critical (ours). Links in AISEC-611.
Re-check when:    the provider updates the served model version
Expires:          2027-02-21 (180 days)
Approved by:      A. Okafor, AI Security reviewer (independent of the requesting team)
Incident owner:   SOC on-call; notify AWS and, if reportable, the regulator within the Art. 73 deadline
Retention:        3 years (matches the knowledge-platform records policy)
Record status:    append-only; the re-check at expiry produces a new record, not an edit of this one
```

## What made this case different

Compared with the two textbook origins (`VALIDATION.md` Tests 3 and 4 for downloaded, Test 2 for a frontier cloud model):

- **vs. downloaded open-weight:** the file-level supply chain at L1 (malware scan, format, checksum, publisher verification) nearly vanishes, the provider carries it. That is the whole saving.
- **vs. a frontier cloud API:** you inherit **less** safety testing, so more of the L3/L4 evidence must be "ours," and you add a platform runtime guardrail at L5 to put a safety layer back.
- **the first-time cost:** no prior baseline to diff against, so L3/L4 is a full workup rather than a cheap delta against a known release.

Same seven layers throughout. Who holds the files and who tested the model, not who trained it, is what moves the effort.
