# Model Trust Record (fillable template)

*Copy this file per adoption. One model, one use, one decision. Fill every field; a field you cannot answer is itself a finding. The machine-readable form is [`model-trust-record.schema.json`](model-trust-record.schema.json); a completed example is [`model-trust-record.bedrock-example.json`](model-trust-record.bedrock-example.json).*

> Delete this note and the parenthetical hints once filled. Keep the record **append-only and signed**: a re-check produces a *new* record, never an edit of this one.

```
Model Trust Record
------------------
Model:            <name> @ <version or file hash>
Origin:           cloud API | hosted open-weight (open model via a cloud provider) | downloaded open-weight
Modified:         no | quantized | fine-tuned | merged      (a "yes" re-tiers evidence; see FRAMEWORK L2 and L3)
Use case:         <one line>
Scrutiny level:   R1 | R2 | R3 | R4      Regulatory floor: <e.g. EU AI Act high-risk, or none>
Impact assessment: <ISO 42001 AI System Impact Assessment ref; + EU AI Act FRIA ref if it applies>
Per-layer result: L0 <r> · L1 <r> · L2 <r> · L3 <r> · L4 <r> · L5 <r>   (each: pass | conditional | stop)
Overall:          Allow | Allow with controls | Restrict to a narrower use | Deny
Narrowed use:     <required iff Overall is "Restrict": the narrower use this record is valid for; else n/a>
Evidence:         <each item: layer · "ours" | "vendor's" · valid | void-on-modification;
                  tier T1|T2|T3 for L3/L4 behavioural evidence, n/a for L1/L2 evidence>
Guardrails:       <each control: id · config-version · L4-finding-it-closes · last-re-test date>
Re-entry log:     <each trigger: modification | new-capability | scope-change -> layers re-opened -> rigor change>
Scope changes:    <old scope -> new scope · verified-removal ref · floor check · L5 re-validation ref; else none>
Risk transfer:    <RTD ref> · accepted by <system-review owner + date>
Re-check when:    <events that force a re-check>
Expires (date):   <ISO date>        Expires (event): <e.g. next model-version bump>
Approved by:      <name + role; for R3/R4, an approver independent of the team proposing the model>
Incident owner:   <who notifies the provider / regulator on an incident, plus the deadline>
Retention:        <how long this record is kept; once provider status attaches, at least the EU AI Act Art. 18 floor>
Record status:    append-only, signed, stored WORM/immutable; a re-check produces a new record, not an edit
```

## How the per-layer results become the overall verdict

A total rule, so it is unambiguous and a policy engine can compute it:

- Any **stop** at any layer → **Deny**.
- A **conditional that L5 does not verifiably close** → **Deny**.
- **All layers pass**, no control needed → **Allow**.
- **Every conditional closed by a verified L5 control** → **Allow with controls**.
- A conditional resolved **only** by narrowing the use → **Restrict to a narrower use** (fill `Narrowed use`, or the verdict is malformed).

The verdict is always scoped: "allow *for this use*, at *this level*, until *this date*." It is never "this model is safe."
