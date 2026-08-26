# Worked runbook: a fine-tuned open-weight model (Qwen, fine-tuned in house, first time)

*The other common request, and the one teams most often get wrong: "we took an open model (Qwen, Llama), fine-tuned it on our own data, and now we want to ship it." The mistake is treating it as a small edit to a trusted model. It is not. Fine-tuning **forks the trust object**: the result is a new model that has never been tested by anyone but you, and the base model's reputation, safety testing, and any prior Model Trust Record describe a different artifact. This runbook walks that case end to end and ends in a signed Model Trust Record. It is the counterpart to [bedrock-hosted-open-weight.md](bedrock-hosted-open-weight.md): that case pushes effort off your plate (the provider holds and tests the model); this one puts the most effort on your plate (you hold the weights **and** you performed the last training step).*

**The one idea to carry through.** A fine-tuned model is the **creation of a new, untrusted model**, not the modification of a trusted one. So the Gate does not start over, but it splits cleanly: you **reuse** the evidence for the layers fine-tuning cannot touch (the base model's file provenance, the stakes of the use) and you **redo, from scratch,** the layers fine-tuning silently breaks (behavior and attack resistance). Fine-tuning is one of the most reliable ways to strip a model's safety alignment, and it does so quietly, even when the training data is entirely benign. That is why "modified by us" forces the **full track** on its own, regardless of rigor level.

**Scenario.** A support team downloads **Qwen2.5-7B-Instruct** and fine-tunes it (LoRA SFT) on roughly 50k of their own historical support conversations, to build an assistant that **drafts replies to customer support tickets**. A human agent reads and approves every draft before it is sent. The team runs the fine-tuned weights on their own infrastructure. First time fine-tuning this family, first time shipping a fine-tuned model at all.

---

## Step 0: Intake

```
Requesting team:      Customer Support Platform
Model:                Qwen2.5-7B-Instruct, fine-tuned (LoRA SFT) on internal support data
Version / variant:    base qwen2.5-7b-instruct @ <base weights sha256>; adapter build ft-support-2026-08 @ <adapter sha256>
Origin:               downloaded open-weight   (weights on our own infra)
Modified by us?        fine-tuned  (LoRA SFT, ~50k internal support conversations)
Use case:             Drafts replies to customer support tickets; a human agent approves each before send
Can it take actions?  proposes, human approves each  (drafts only, never sends)
What can it touch?     write, bounded (a draft field; the agent sends)
Data it sees:          customer-facing / internal sensitive  (tickets contain customer PII)
Impact of output: low-stakes external effect  (a customer-facing reply, human-reviewed before it leaves)
Jurisdictions / laws:  GDPR (personal data in both training set and inputs). Not EU AI Act Annex III.
```

## Step 1: Triage

| Driver | Value | Level |
|---|---|---|
| Autonomy | proposes, human approves each | R2 |
| Agency | write, bounded (draft field) | R2 |
| Data | customer PII, in training set and at inference | R3 |
| Impact | low-stakes external effect, human-reviewed | R2 |

Highest driver → **R3** (the data). Regulatory floor: **GDPR** (personal data; not an EU AI Act high-risk floor). → `Rigor: R3 · Floor: GDPR`.

Note how fine-tuning moved the data driver. Base Qwen never saw your customers; **your fine-tuned Qwen has customer PII baked into its weights**, which raises the data driver and brings a right-to-erasure problem the base model did not have (see L2).

## Step 2: Track

Two independent reasons this is **full track**: rigor is **R3**, and the model is **modified by us**. Either alone is enough; `FRAMEWORK.md` and the RUNBOOK flowchart send any modified model to the full track. That means an approver independent of the requesting team, a human red-team pass at L4, and out-of-band eval monitoring at L3/L4. Budget days, not hours: the base model buys you nothing at L3/L4.

---

## The run, layer by layer

### L0: Set the stakes → **pass (R3)**
Customer-facing (via a human), read of customer PII, drafts only. Not a prohibited practice. Rigor R3 carried forward. Nothing about fine-tuning changes the stakes here; the stakes come from the use, and this is the one place base and fine-tuned agree.

### L1: Provenance & supply chain → **pass, but now two chains**
Base Qwen's file provenance is reusable evidence; **your training pipeline is a brand-new supply chain**, and it is the larger risk.
- [x] **Base model (reuse):** publisher verified, base weights `sha256` pinned, license retrieved, format/malware scan on the downloaded base. This is the same downloaded-open-weight L1 as an unmodified model; you already have it.
- [x] **Training data provenance (new, and the crux):** where the 50k conversations came from, that they are licensed for this use, and that the set was reviewed for poisoning and for content that must not be learned. Fine-tuning on unvetted data is a data-poisoning vector as direct as a bad dependency: a handful of crafted examples can plant a backdoor trigger. Recorded against STA-15 (supply-chain data security) and MDS-04 (model documentation requirements).
- [x] **Pipeline integrity (new):** the fine-tuning code, the base image, and the training environment are themselves supply chain. Pin them.
- [x] **Output artifact (new):** hash the resulting adapter/checkpoint (`ft-support-2026-08`) and record base-hash → dataset-id → adapter-hash as one lineage. This triplet **is** the identity of the thing you are trusting.

### L2: Permission & governance → **conditional, then resolved to pass**
- [x] **License permits fine-tuning and this commercial use.** Confirm the Qwen license covers fine-tuning, hosting, and your use, and record who owns the resulting weights.
- [x] **EU AI Act role: provider.** By fine-tuning you are no longer a mere deployer; you have modified the model, which changes your obligations. Use is not Annex III, so no high-risk floor, but the role change is recorded.
- [x] **GDPR on the training set (the fine-tune-specific issue).** Customer PII is now in the weights. Two consequences an unmodified model never raises: a lawful basis for training on that data, and the **right-to-erasure gap**, you cannot delete one customer's data from trained weights the way you delete a row. Record the mitigation you actually chose (train on de-identified data, documented retention, and a re-train-to-forget commitment), or stop here if you have none.
- [x] Mapped to CSA AICM: GRC-10 (impact assessment), STA-09 and STA-15 (supply-chain and supply-chain data), MDS-12 (open model risk), MDS-04 (model documentation), A&A-04 (requirements compliance). See [standards-crosswalk.md](../standards-crosswalk.md).
- [ ] → **[x]** **Data-protection and model-ownership sign-off** raised as a **conditional**, **resolved** once obtained (ref AISEC-742), at which point L2 is recorded **pass**.

### L3: Behavior → **conditional (one residual finding, closed at L5), and this is a full re-test**
The base model's behavior evidence **does not transfer**; you changed the behavior on purpose. Fine-tuning also causes capability regression and catastrophic forgetting, so you test the fine-tuned artifact as if it were unknown, because it is.
- [x] Full behavior suite (`promptfoo`, `DeepEval`) on the fine-tuned artifact at R3 bars: refusal correctness ≥ 98% with zero criticals, hallucination on in-scope questions ≤ 2% (see RUNBOOK pass-bars).
- [x] **Measure the delta, do not assume it.** Run the same suite on the base model and diff. You are looking for two failure modes fine-tuning specifically causes: capability lost on things the base could do (forgetting), and, more important, safety behavior lost (see L4). Recording the base-vs-fine-tuned delta is the same discipline the pilot uses for model transforms in [VALIDATION.md](../VALIDATION.md).
- [x] **Training-data memorization check:** probe whether the model regurgitates verbatim customer data from the training set (extraction attacks). This check exists only because you fine-tuned. The residual (the model can surface training-set PII into a draft) is carried as **finding L3-F1**, a conditional closed by the output PII filter at L5 rather than left open. (This is why L3 is `conditional`, not `pass`: it meets the R3 bars but carries one specific residual a control contains.)

### L4: Attack resistance → **conditional (one residual finding, closed at L5), human red-team included (R3)**
The headline layer. Fine-tuning is empirically one of the most reliable ways to **erode safety alignment**, and even benign task fine-tuning degrades refusal behavior. A clean base model tells you nothing about the fine-tuned one here.
- [x] Automated attack battery at **R3** strength (`garak`, `promptfoo`, `PyRIT`): jailbreaks, direct and indirect prompt injection (a ticket is attacker-controlled text, so injection is in-scope), instruction/data leakage, and training-data extraction. No critical survives. The residual is **indirect prompt injection via the ticket body (finding L4-F1)**, carried as a conditional and closed by the input guardrail at L5.
- [x] **Alignment-erosion diff:** run the jailbreak/refusal set against **base and fine-tuned** and compare attack-success rates. A rise from base to fine-tuned is the signal to catch; treat a material rise as a stop, not a note.
- [x] **Human red-team pass** (required at R3): a person tries to make the drafting assistant produce a harmful or data-leaking reply through a crafted ticket.
- [x] Honesty rule recorded: a clean R3 run means nothing critical survived at this strength, not that the model is safe.

### L5: Guardrails → **pass**
The model's output distribution changed, so guardrails tuned for the base model may no longer fit.
- [x] Input/output guardrails on the drafting path (block PII exfiltration in drafts, block prompt-injection payloads from the ticket body). This **closes L3-F1 and L4-F1.** Version it (`gr-support-io` v1).
- [x] **Verify it fires** against the exact L3/L4 paths, especially the training-data extraction and injection paths, not merely that it is enabled. Record the re-test date.

Because L3 and L4 each carried a conditional (the PII-in-draft finding L3-F1 and the ticket-body injection finding L4-F1) that this L5 control verifiably closes, the verdict is **Allow with controls**.

### L6: Upkeep → recorded
Fine-tuning changes the maintenance story more than any other modification: **you own a fork with no upstream patches.**
- [x] Pin the base-hash / dataset-id / adapter-hash triplet.
- [x] Re-check triggers: (1) **the base model ships a safety fix**, you do not get it for free; you must re-fine-tune and re-run L3/L4 to inherit it. (2) You retrain on new data (a new artifact, a new record). (3) Drift in the ticket distribution.
- [x] Track base-model advisories against your fork explicitly.
- [x] Expiry: 90 days (R3 default) → **2026-11-24**.
- [x] Incident owner + notification deadline recorded.

### Exit Gate → RTD-742, two signatures
The model gate judged the model. Handed to the system review (RTD-742): the **agent-console** that inserts drafts (does an approved draft always require a human click before send?), the retention of the training set, and the right-to-erasure commitment. The gate flags the erasure gap; closing it is a system-and-policy decision, not a model test.

---

## The result

**Allow with controls · R3 · downloaded open-weight, fine-tuned.** The full signed record is [`templates/model-trust-record.fine-tuned-example.json`](../templates/model-trust-record.fine-tuned-example.json) (same shape as [`model-trust-record.schema.json`](../templates/model-trust-record.schema.json)); the human-readable form:

```
Model Trust Record
------------------
Model:            Qwen2.5-7B-Instruct, fine-tuned in house (LoRA SFT)
Identity:         base qwen2.5-7b-instruct @ <base sha256>
                  + adapter ft-support-2026-08 @ <adapter sha256>
                  + dataset support-hist-2026-07 @ <dataset id>   (this triplet is the trusted artifact)
Origin:           downloaded open-weight     Modified: fine-tuned (LoRA SFT, ~50k internal support convos)
Use case:         Drafts customer support replies; a human agent approves each before send
Scrutiny level:   R3      Regulatory floor: GDPR (personal data)      Track: full
Role (EU AI Act): provider (we modified the model)
Impact assessment: ISO 42001 AISIA AISEC-742; GDPR lawful-basis + right-to-erasure mitigation recorded
Per-layer result: L0 pass · L1 pass · L2 pass · L3 conditional · L4 conditional · L5 pass
Overall:          Allow with controls
Controls added:   Input/output guardrails on the drafting path (gr-support-io v1): PII-in-draft block,
                  ticket-body injection block. Verified to fire against the L3/L4 extraction and
                  injection paths.
Evidence:         L1 base provenance (reused) + training-data provenance, pipeline integrity, artifact
                  hash (all ours, new); L2 data-protection + model-ownership sign-off (ours);
                  L3 behavior scorecard on the fine-tuned artifact + base-vs-fine-tuned delta +
                  memorization probe (ours, full re-test); L4 R3 red-team incl. human pass +
                  alignment-erosion diff, no critical (ours). Links in AISEC-742.
Re-check when:    base model ships a safety fix · we retrain · ticket distribution drifts
Expires:          2026-11-24 (90 days, R3 default)
Approved by:      A. Okafor, AI Security reviewer (independent of the requesting team)
Incident owner:   SOC on-call; GDPR breach path if customer data leaks (notify within the Art. 33 deadline)
Retention:        3 years; training set retained under the recorded data-protection basis
Record status:    append-only; a re-fine-tune produces a new record, not an edit of this one
```

## What made this case different

Compared with the unmodified origins:

- **vs. base (unmodified) open-weight:** L0 stakes and L1 **base** provenance carry over, nothing else does. Fine-tuning adds a second, larger supply chain (training data, pipeline, output artifact) at L1, changes your EU AI Act role to **provider** and opens a GDPR right-to-erasure gap at L2, and forces a **full re-test** at L3 and L4 because the model's behavior and, critically, its safety alignment have changed.
- **vs. hosted open-weight (the Bedrock runbook):** that case pushes effort **off** your plate, the provider holds and tests the model, so L1 nearly vanishes. This case pushes effort **onto** your plate: you hold the weights and you did the last training step, so no external party has ever tested this exact artifact and every behavior/safety claim must be "ours."
- **the fork you now own:** no upstream patches. A base-model safety fix is not yours until you re-fine-tune and re-run the gate.

Same seven layers throughout. The rule that carries the whole case: **fine-tuning creates a new model.** Reuse the stakes and the base file provenance; redo behavior and attack resistance from zero.
