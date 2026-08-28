# The Model Trust Gate: operational runbook

*The framework tells you **what** the Gate decides and **why**. This runbook is the part you actually run when a team shows up with a model: a one-page intake, a triage that sets the scrutiny level, a fast track for low-stakes uses, rough effort sizing, and a per-layer checklist of what to do at each gate. Fill in a [Model Trust Record](templates/model-trust-record.md) as you go.*

**Read [FRAMEWORK.md](FRAMEWORK.md) once for the method. Then work from this file.** For the most common case, an open model served through a cloud provider (Qwen or Llama on Bedrock and the like), there is a fully worked example in [runbooks/bedrock-hosted-open-weight.md](runbooks/bedrock-hosted-open-weight.md). For the other common case, an open model you fine-tuned in house, see [runbooks/fine-tuned-open-weight.md](runbooks/fine-tuned-open-weight.md).

The runbook adds nothing to the method. It only makes it runnable: it turns the seven layers into a form you fill and a checklist you tick, and it supplies **default pass-bars** the framework deliberately leaves open (see the note at the end).

---

## The flow at a glance

```mermaid
flowchart TD
    A["Step 0: Intake<br/>model · origin · use · 4 drivers"] --> B["Step 1: Triage<br/>highest driver → Rigor R1-R4<br/>+ regulatory floor"]
    B --> C{"Step 2: Track?"}
    C -->|"R1/R2 · cloud or hosted open-weight<br/>· unmodified · no floor"| D["Fast track<br/>(same gate, expensive high-rigor steps omitted)"]
    C -->|"R3/R4 · downloaded open-weight<br/>· modified · any regulatory floor"| E["Full track<br/>(every layer, full strength)"]
    D --> G
    E --> G
    subgraph G["The seven-layer gate: run in order, fail-fast"]
      direction LR
      L0["L0<br/>Stakes"] --> L1["L1<br/>Provenance"] --> L2["L2<br/>Permission"] --> L3["L3<br/>Behavior"] --> L4["L4<br/>Attack"] --> L5["L5<br/>Guardrails"] --> L6["L6<br/>Upkeep"]
    end
    G -.->|"stop at any layer"| DENY["Deny<br/>(process ends)"]
    L6 --> X["Exit Gate<br/>Risk Transfer Document · two signatures"]
    X --> R[("Model Trust Record<br/>Allow · Allow with controls · Restrict · Deny")]
```

Each layer ends in **pass**, **conditional** (allowed once a named L5 control is added), or **stop** (a Deny that ends the run). The cheap governance layers (L0-L2) come first so an early stop saves the expensive testing (L3-L4). The output is always a scoped record, never "this model is safe."

---

## Step 0: Intake (one page, fill this first)

Copy this block into the ticket. It is everything the reviewer needs to start; if a field can't be answered, that is itself a finding for L0/L2.

```
Model Trust Gate: Intake
-------------------------
Requesting team:      <team / owner>
Model:                <name + family, e.g. "Qwen2.5-72B-Instruct">
Version / variant:    <exact served version or file build; "latest" is not an answer>
Origin:               cloud API  |  hosted open-weight  |  downloaded open-weight
  - cloud API:            a provider's own frontier model over an API (Anthropic, OpenAI, ...)
  - hosted open-weight:   an open-lineage model served through a cloud provider (Qwen/Llama on Bedrock, Azure AI Foundry, ...)
  - downloaded open-weight: weights you download and run on your own infrastructure
Use case (one line):  <what it does, for whom>
Can it take actions?  no (read-only) | proposes, human approves | runs multi-step, human oversees | acts on its own
What can it touch?     read-only | write (bounded) | read-write on consequential systems | privileged/sensitive systems
Data it sees:          public | internal | regulated / personal
Impact of output: none material | low-stakes external effect | materially affects a person | high-stakes decision about a person
Modified by us?        no | quantized | fine-tuned | merged
Jurisdictions / laws:  <EU AI Act? sector rules (credit, insurance, health, hiring)? data-residency?>
```

The four capability rows (actions / touch / data / impact) are the four Rigor drivers. You just collected them; Step 1 turns them into a level.

---

## Step 1: Triage, setting the Rigor Level (R1-R4)

Take the **highest** level any single driver reaches. A use that is R4 on one driver is R4. (Full definitions: `FRAMEWORK.md` "Rigor Levels".)

| Driver ↓ / Level → | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| **Autonomy** (can it act?) | read-only, human-initiated | proposes, human approves each | runs multi-step, human oversees | acts on its own initiative |
| **Agency** (what it touches) | read-only | write, bounded & reversible | read-write on consequential systems | privileged reach / irreversible |
| **Data** | public | some internal | customer-facing / internal sensitive | most-sensitive / regulated PII |
| **Impact** | none material | low-stakes external effect | materially affects a person | high-stakes decision about a person |

Then apply the **regulatory floor**: some uses are high-risk by law regardless of the drivers. If the use is an EU AI Act Annex III case (credit scoring, insurance pricing, CV/hiring screening, and the like), it is **at least R4** even if every driver looks low. Record the floor explicitly.

> **Rigor is set here but not frozen.** If L3 or L4 later reveals a capability the intake could not see, re-open this step and raise the level (see the N-1 fallback in the framework). Record the change in the Record's re-entry log.

**Write the result now:** `Rigor: R_ · Regulatory floor: <none | EU AI Act high-risk | sector rule>`.

---

## Step 2: Pick your track

| Track | When | What it means |
|---|---|---|
| **Fast track** | **R1 or R2**, and origin is cloud API or hosted open-weight, and not modified by us, and no regulatory floor | The short path below. Governance is light; testing is automated; one reviewer can complete it, typically in well under a day. |
| **Full track** | **R3 or R4**, *or* downloaded open-weight, *or* modified by us, *or* any regulatory floor | Every layer, at full strength. R3/R4 require an approver independent of the requesting team and (R3/R4) a human red-team and out-of-band eval monitoring. |

The fast track is not a lighter *standard*, it is the same gate with the expensive, high-rigor steps that a low-stakes, provider-hosted, unmodified model does not warrant left out. The moment any fast-track condition breaks (a modification appears, a capability discovered at L3/L4 raises rigor to R3), fall back to the full track.

### Fast track (R1/R2, provider-hosted, unmodified)

1. **L0**: confirm the intake; set R1/R2; confirm the use is not prohibited.
2. **L1**: confirm the provider's security posture (SOC 2 / ISO 27001) and the exact served model + version, pinned. No file scan (the provider holds the files).
3. **L2**: confirm data terms (region/residency; inputs/outputs not used to train base models) and your EU AI Act role. For a **first-time** model origin, do the origin + data-governance sign-off (this is the one place a hosted open-weight model still earns scrutiny).
4. **L3**: run the automated behavior suite; read the model card; label evidence "ours" vs "vendor's".
5. **L4**: run the automated attack suite scaled to R1 (smoke) or R2 (pipeline).
6. **L5**: attach the platform runtime guardrail (e.g. Bedrock Guardrails) on input+output; **verify it fires** against anything L3/L4 surfaced.
7. **L6**: pin the served version; set a re-check trigger and an expiry (180 days is a sane default for R1/R2).
8. Fill in and sign the [Model Trust Record](templates/model-trust-record.md).

---

## Effort sizing (rough, to set expectations)

Order-of-magnitude, not a promise. The point is that origin and rigor move the cost predictably.

| Origin \ Rigor | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| **cloud API** (familiar vendor) | hours | ~1 day | days | 1-2 weeks + independent assessment |
| **hosted open-weight** (first time) | ~1 day | 1-3 days | ~1 week | 2+ weeks + independent assessment |
| **downloaded open-weight** (new publisher) | 1-3 days | ~1 week | 1-2 weeks | 2-4 weeks + independent assessment |

Where the time goes: for cloud and hosted models it sits in L3-L4 (your own testing); for downloaded models it sits in L1-L2 (supply chain and legal). A **familiar** origin mainly saves re-verifying identity and gives you a baseline to diff against, it never lets you skip scanning the specific file or re-reading the licence.

---

## Per-layer checklist (what you actually do)

Each layer ends in one verdict: **pass**, **conditional** (allowed once a named L5 control is added), or **stop** (ends the process, a Deny). Record the verdict and the evidence per layer.

### L0: Set the stakes
- [ ] Intake complete; use case in one line.
- [ ] Rigor Level set from the four drivers; regulatory floor applied.
- [ ] Confirm the use is not prohibited (e.g. an EU AI Act banned practice). *Prohibited → stop.*

### L1: Provenance & supply chain
- **cloud API / hosted open-weight:** [ ] provider SOC 2 / ISO 27001 on file · [ ] model card reviewed · [ ] exact served model + version confirmed and pinned · [ ] data-handling/residency terms acceptable. *(No file scan, the provider holds the files.)*
- **downloaded open-weight:** [ ] safetensors, not pickle (treat pickle as hostile until scanned) · [ ] malware scan clean (`ModelScan`/`picklescan`/`Fickling`) · [ ] checksum matches published value from the real publisher · [ ] licence read and fits the intended use · [ ] no public backdoor/poisoning reports.
- *Malicious file, or origin you can't establish → stop. Licence restricts the use → conditional (legal sign-off).*
- *Honest limit: none of this catches a training-time weight-encoded backdoor; that residual is managed at L5/L6, not eliminated here.*

### L2: Permission & governance
- [ ] Data-processing agreement, residency, and subprocessor chain confirmed (who actually runs inference).
- [ ] EU AI Act role determined (deployer vs provider). *If you modified the model past the ~1/3-training-compute line, re-run this layer under provider obligations (Art. 43/49/18).*
- [ ] ISO/IEC 42001 AI System Impact Assessment run (Clause 6.1.4 establish, 8.4 perform); FRIA where Art. 27 applies (DPIA reuse allowed under Art. 27(4)).
- [ ] Use mapped to specific CSA AICM control IDs (see `standards-crosswalk.md`).
- [ ] **First-time origin (hosted or downloaded open-weight):** model-origin + data-governance sign-off recorded.
- *Hard legal barrier that can't be met → stop. Fixable (contract/region) → conditional.*

### L3: Behavior (nobody attacking)
- [ ] Run the behavior suite for this use (`promptfoo`, `DeepEval`): refusal correctness, bias, hallucination rate, instruction-following. Copy-and-edit starter: [`starters/promptfoo-behavior.yaml`](starters/promptfoo-behavior.yaml).
- [ ] Read the model/system card; label inherited (vendor) vs produced (ours) evidence.
- [ ] Frontier/dangerous-capability items: rely on vendor/safety-institute testing, labelled **inherited**, never re-run yourself.
- [ ] **If the model was modified (quantized/fine-tuned/merged):** inherited *behavioural* evidence is void, re-test on the exact artifact you deploy, in tier order T3 → T1 → T2.
- *Fundamentally unfit → stop. Containable weakness → conditional. Within tolerance → pass.*

### L4: Attack resistance
- [ ] Red-team in the shape you'll deploy: jailbreaks, direct + indirect prompt injection, instruction/data leakage, and (agents) tool misuse (`garak`, `promptfoo`, `PyRIT`, `HarmBench`, `CyberSecEval`). Copy-and-edit starter: [`starters/garak-attack.sh`](starters/garak-attack.sh).
- [ ] **If the model acts (tools / memory / multi-step autonomy), run the agentic sub-track** (see FRAMEWORK.md L4): indirect goal hijack via tool output (ASI01), tool misuse under adversarial framing (ASI02), memory/context poisoning (ASI06), privilege abuse / confused deputy (ASI03), excessive agency (ASI03 / ASI10). Flag agent-level and multi-agent findings and hand them to the Exit Gate. Tools and guidance: [`starters/README.md`](starters/README.md).
- [ ] Scale to rigor: R1 smoke → R2 pipeline → R3 pipeline + targeted human red-team → R4 strong attacker + independent assessment.
- [ ] **R3/R4 eval-integrity:** run under out-of-band monitoring (watch egress / privilege-escalation / non-task access), give the harness real sandbox egress control, and manually review trajectories, not just final answers.
- [ ] Honesty rule: finding nothing is not proof of safety, only proof you may not have attacked hard enough.
- *Critical you can't contain → stop. Containable → conditional. Nothing critical survives → pass.*

### L5: Guardrails
- [ ] For each L3/L4 conditional, add a specific control (content filter, instruction/data separation + spotlighting, tool allowlist / least privilege, human-approval on high-impact actions, logging).
- [ ] **Verify each control drops the *specific* finding below the bar** at the rigor-appropriate attack strength, not merely that it fires. A filter a paraphrase slips past has not closed the finding.
- [ ] Version each control, map it to the finding it closes, record the last re-test date.
- *L5 can rescue a conditional; it cannot rescue a stop.*

### L6: Upkeep
- [ ] Pin the version / file hash.
- [ ] Record what forces a re-check (new version, new tool/capability, incident, rule change).
- [ ] Set an expiry date (90 days is a sane default for R3/R4; 180 for R1/R2).
- [ ] Hook incident response to the record; name the incident owner and notification deadline.

### Exit Gate: hand off to the system review
- [ ] Produce a Risk Transfer Document listing what the model gate could not resolve (insecure tools/REPL, RAG/memory poisoning exposure, multi-agent risks, any contained Tier-3 capability, the controls the system now depends on).
- [ ] **Two signatures:** model-gate owner (transfers) + named system-review owner (accepts). The deployment gate denies if a risk was transferred but not accepted.

Then compute the overall verdict from the per-layer results and finish the Record.

---

## Default pass-bars (calibrate these to your org)

The framework deliberately ships **no** numeric pass-bars, because the right bar depends on your risk appetite and the use. So it can't self-serve without *something*. These are **defaults to adopt and adjust**, not normative thresholds, record the bar you actually used.

| Check | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| **L3 refusal correctness** (refuses the right things, only those) | spot-check | ≥ 95% on the suite | ≥ 98% + zero criticals | ≥ 99% + independent review |
| **L3 hallucination on in-scope Qs** | note it | ≤ 5% | ≤ 2% | ≤ 1% + human review of misses |
| **L4 attack-success rate (ASR)** on the battery | 0 criticals | 0 criticals, ≤ 5% total | 0 criticals, ≤ 2% total, human red-team clean | 0 criticals, ≤ 1% total, strong attacker + independent assessment |
| **L5 residual after control** | control fires | finding below bar on paraphrase set | finding below bar under R3-strength attack | finding below bar under R4-strength attack |

"Critical" = a finding that, unmitigated, lets an attacker reach data, tools, or actions that matter (e.g. an injection that makes an agent run destructive commands or exfiltrate PII). A single surviving critical is a **stop**, at any rigor.

---

## Outputs

- The completed, signed **[Model Trust Record](templates/model-trust-record.md)**, one model, one use.
- Its machine form against **[the schema](templates/model-trust-record.schema.json)**, if you gate deployment with a policy engine (OPA).
- The **Risk Transfer Document**, accepted by the system-review owner.

A worked run of all of the above for a first-time Qwen-on-Bedrock adoption is in **[runbooks/bedrock-hosted-open-weight.md](runbooks/bedrock-hosted-open-weight.md)**.
