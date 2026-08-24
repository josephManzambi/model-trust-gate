# The Model Trust Gate

*A step-by-step way to decide whether your organization should trust a given AI model, for a specific use, with the right amount of scrutiny and a record you can show an auditor.*

**Status:** working draft (v0.2.1). Facts that need a primary-source check before publication are tagged `[verify]`.

---

## Executive summary (read this first)

**The problem.** Teams keep adopting AI models, both cloud services and downloadable open-weight models, and someone has to decide whether each is safe enough for a given use, then be able to defend that call. That is a hard decision, and an easy one to make inconsistently. The Model Trust Gate makes it a repeatable procedure, like a vendor-risk or change-approval gate, but for AI models.

**How it works.** Seven checks, run in order from cheap to expensive, so a model that fails an early check is stopped before you spend on the hard testing. Each check ends in one of three outcomes: pass, conditional-pass (allowed once a named control is added), or stop.

The seven questions, in plain terms:

- **L0 Set the stakes:** what are we deciding, and how carefully must we look? (This sets the scrutiny level.)
- **L1 Provenance:** do we know where this model came from, and can we trust the files?
- **L2 Permission:** are we allowed to use it, and can we prove it to a regulator?
- **L3 Behavior:** with nobody attacking it, does it behave well enough for the job?
- **L4 Attack resistance:** when someone actively tries to trick or abuse it, does it hold?
- **L5 Guardrails:** what controls do we wrap around it in production?
- **L6 Upkeep:** how do we keep this decision valid as the model, threats, and rules change?

<p align="center">
  <img src="assets/model-trust-gate-diagram.png" alt="The Model Trust Gate: seven ordered checks from L0 to L6, run cheapest first, each ending in pass, conditional pass, or fail. Passing all seven produces a signed, dated Model Trust Record; a fail at any gate stops the sequence and is recorded." width="560">
</p>

**Scrutiny scales with stakes.** A meeting-notes tool gets a light review (level R1); a model deciding insurance claims gets a heavy one (level R4). The scrutiny level belongs to the *use*, not the model.

**The one idea to remember.** Both cloud and open-weight models need behavior and attack testing (L3 to L4). What downloading and self-hosting an open-weight model *adds* is supply-chain risk (L1 to L2) that a reputable cloud API mostly spares you, because you now hold and run the files. It can also raise the technical risk, since you lose the vendor's runtime safety layer and may change the model when you compress or fine-tune it. So the rule of thumb "cloud means the hard work is L3 to L4, open-weight means it is L1 to L2" is about where the *extra, distinctive* effort lands, not a claim that either side is risk-free.

**What you get.** Not a score, but a signed, dated Model Trust Record: one model, one use, the result of each check, the controls added, who approved it, and when it expires. The kind of artifact you hand an auditor.

---

## The problem this solves

Teams across the business keep wanting to adopt AI models. Some are cloud services you call over an API (OpenAI, Anthropic, a model on AWS Bedrock). Others are "open-weight" models: files you download and run on your own infrastructure (Llama, Mistral, DeepSeek and the like). Either way, someone has to answer a simple-sounding question before it goes live:

> Do we trust this model enough to use it for this, and can we prove we made that call responsibly?

That is a hard decision, and an easy one to make inconsistently or on the strength of a vendor's marketing. The Model Trust Gate makes it a repeatable procedure instead. If you already run vendor-risk reviews or change-approval gates, this is the same idea applied to AI models: a short sequence of checks, each with a clear pass, conditional-pass, or stop, ending in a signed record.

It is deliberately **not** a new set of security controls. It reuses the frameworks you likely already reference (NIST, ISO 42001, CSA's AI Controls Matrix, the OWASP Top 10 for LLM and Agentic Applications, MITRE ATLAS) and arranges them into one runnable decision. Staged, fail-fast gates that end in a signed record are an old pattern from vendor-risk review and bank model-risk management; what the AI-standards frameworks do not give you on their own is that pattern run on the AI-specific standards and weighted by whether the model is a cloud call or a downloaded file. (See "How this relates to existing frameworks" below.)

**Who it is for.** The organization *adopting* a pretrained model, not the lab that trained it. That matters: some risks are baked into a model during training and can't be fixed by the adopter, only detected. The Gate is honest about that line.

**What it does not cover.** It judges the *model*. It does not judge the whole system around the model (the knowledge bases it reads from, the way several AI agents chain together, the application code). Those are real risks; the Gate flags them and hands them to a separate system-level review rather than pretending to cover them. That hand-off is made formal at the end of the process, in the Exit Gate.

### A few terms in plain English

- **Open-weight model:** a model whose files you download and run yourself. You own the hosting, and therefore the risk of what is inside those files.
- **Provenance:** where a model came from and whether the files or endpoint have been tampered with. The same idea as software supply-chain security, applied to model files.
- **Prompt injection:** hiding instructions inside content the model reads (a web page, an email, a document) so the model follows the attacker's instructions instead of yours.
- **Jailbreak:** phrasing that gets a model to do something it is supposed to refuse.
- **Guardrail:** a runtime filter or control that sits around the model in production to catch bad inputs or outputs.

---

## The two ideas that make it work

**1. Check the cheap things first, and stop early if they fail.**
The checks are ordered from cheap and administrative to expensive and technical. You confirm where the model came from and whether you are legally allowed to use it *before* you spend days red-teaming it. If a downloaded model file fails a malware scan, you stop there. You never pay for the expensive testing on a model you were never going to be allowed to run. This is the same "fail fast" logic as a change gate that rejects a request on a missing approval before anyone starts the work.

**2. Match the scrutiny to the stakes, and let the model's origin decide where the effort goes.**
- **How much scrutiny** is set once, at the start, by how risky the *use* is. A tool that drafts internal meeting notes gets a light review; a model that helps decide insurance claims gets a heavy one. We call this the **Rigor Level (R1 to R4)**.
- **Where the effort lands** depends on whether the model is a cloud service or a downloaded open-weight model. For a trusted cloud vendor, the paperwork is light and the real work is behavior and attack testing. For a downloaded model, the supply-chain and legal checks are the hard part, because you are now running someone else's files in your environment.

The single most useful idea in this whole document: **downloading and self-hosting an open-weight model adds supply-chain risk that a reputable cloud API mostly spares you (you now hold and run the files), and it can raise the technical risk too, because you lose the vendor's runtime safety layer and may change the model when you compress or fine-tune it. Both kinds of model still need behavior and attack testing; open-weight adds the supply-chain work on top.**

---

## Rigor Levels: how much scrutiny

The scrutiny a use deserves comes from **four drivers**. You take the highest level any single driver reaches, not an average: a use that is R4 on any one driver is R4.

Two drivers come straight from the AWS / CSA Agentic AI Security Scoping Matrix, which separates two things people often blur:

- **Autonomy: how independently it acts.** The Scope 1 to 4 ladder, set by how much a human stays in the loop:
  - **Scope 1, no agency:** read-only, human-initiated, it can't change anything.
  - **Scope 2, prescribed agency:** it proposes an action, but a human must approve each one.
  - **Scope 3, supervised agency:** it runs multi-step tasks on its own; a human triggers and oversees.
  - **Scope 4, full agency:** it acts on its own initiative in response to events, with no human trigger.
- **Agency: what it is permitted to touch and do.** The matrix grades this on two sub-dimensions, permission and reach, which combine into a ladder of their own:
  - **Read-only:** it can retrieve and read, but cannot change anything.
  - **Write, bounded:** it can create or change data, but only within a narrow, reversible, low-exposure scope.
  - **Read-write on consequential systems:** it can change records or state that matter to the business or to a person.
  - **Privileged reach:** it can touch sensitive systems or credentials, or take high-blast-radius or irreversible actions.

  Two agents at the same autonomy scope carry very different risk if one is read-only and the other has privileged reach.

The third driver is **data sensitivity**: public, internal, or regulated and personal data.

The fourth driver is **impact (also called consequence): how much its output affects a person or the business, whether or not the model "acts."** A model that only outputs a score still drives a real decision when that score screens a job applicant, prices insurance, or ranks a claim. Customer-facing reach and blast radius live here too. This driver exists because a pure advisory or scoring model can be Scope 1 on autonomy and read-only on agency, yet be one of the highest-stakes uses in the building. (This is the rigor input, distinct from the formal AI System Impact Assessment produced at L2; its four levels track the EU AI Act's risk framing, from minimal to high-risk.)

Your Rigor Level is the highest level reached by any of the four:

| Level | Reached when any driver hits this | Example | How hard you attack-test it |
|---|---|---|---|
| **R1** | Scope 1, read-only, non-sensitive data, no material consequence to a person | A tool that summarizes a team's notes. | A quick smoke test. |
| **R2** | Scope 2 (human-approved actions), or write access, or some sensitive data, or a low-stakes external effect | An assistant that drafts changes for a human to approve. | Automated testing you can run in a pipeline. |
| **R3** | Scope 3 (supervised), or wide agency with real blast radius, or customer-facing, or a decision that materially affects a person | A support agent that looks up and changes records. | Automated testing plus a targeted human red-team. |
| **R4** | Scope 4 (full autonomy), or agency over sensitive production systems, or the most sensitive data, or a high-stakes decision about a person (hiring, credit, claims, health) | An autonomous remediation agent on production; a CV-screening model. | A strong attacker plus an independent assessment. |

Two rules keep this honest:

- **A regulatory floor sits on top of the four drivers.** Some uses are high-risk by law regardless of how they score. A CV-screening model is Scope 1 and read-only, but the EU AI Act classifies it high-risk, so it is at least R4. The impact driver catches most such cases on its own; the floor is the backstop for anything the drivers miss.
- **Rigor is set at L0, but it is not frozen.** If Layers 3 or 4 reveal a capability the intake could not see (for example, the model emits links a downstream service will fetch, or can reach a tool you had not scoped), re-open L0 and raise the level. The intake sets the strength of the later tests, so a capability discovered later must be allowed to raise it.

Why reuse the AWS/CSA matrix rather than invent a scale: it is a published standard (AWS defined it, CSA enhanced it into a multi-dimensional version), it separates autonomy from agency cleanly, and where your organization already scopes agents this way, the Gate reads from a call your teams already make.

The Rigor Level belongs to the *use*, not the model. The same model can be R1 in one deployment and R4 in another.

---

## The seven layers

Read each layer as one question you must answer. For each, this document gives you: the question in plain terms, why a security leader should care, what a pass, conditional-pass, or stop means, a short concrete example, and the standards and tools that support it.

The flow is a gate. A **stop (FAIL)** can occur at any layer and ends the process; the governance checks (L0 to L2) are simply where most early stops happen, before you spend on testing. A **conditional-pass (CONDITIONAL)** in the technical layers means "allowed, but only once we add a specific control," and that control gets built at Layer 5. Note that L4's stop-versus-conditional line depends on whether a control at L5 can contain the finding, so L4 and L5 are judged together, not in strict isolation.

### The flow is not strictly linear: recursive triggers

The seven layers run in order, but three events re-open an earlier layer and force part of the gate to run again. This is the **N-1 fallback**: a fact discovered late must be allowed to change a decision made early.

- **A modification** (quantization, fine-tuning, or a model merge), discovered or performed at L3 or L4, re-opens **L2** (your legal standing may shift from deployer to provider under the EU AI Act, Art. 25), re-opens the affected **L3/L4 evidence** under the tiered-evidence rule at Layer 3, and re-opens **L5** for any guardrail whose justifying L4 finding the modification may have changed, because the tested artifact is no longer the approved one.
- **A capability beyond the intake's assumptions**, discovered at L3 or L4 (the model can reach a tool you had not scoped, emits content a downstream system will act on, or shows autonomy the use-case description did not imply), re-opens **L0** and can raise the Rigor Level, which in turn strengthens the L3/L4 tests.
- **A scope reduction** (the use is narrowed after the fact) re-opens **L0** under the symmetry rule below, and re-opens **L5** to re-validate the guardrails whose justification has changed.

**Why this terminates (no infinite loop).** Termination rests on two rules, not on a convergence proof (a proof by "rigor only rises" would be wrong, because the symmetry rule below can also lower it). First, **each discovered fact fires its trigger at most once**: mark it resolved in the record, so re-opening a layer on an already-known modification or capability cannot re-fire. Second, **cap the re-entries per record** at a small K; a case that keeps re-triggering is escalated to a human owner, not looped. Within those two rules the discovery path is bounded (a capability can raise rigor at most three times), and scope-lowering is human-initiated and gated, so it is not part of the automatic loop.

**The symmetry rule: rigor can go down, but only against evidence, not paper.** Rigor may be *lowered* when scope is genuinely reduced, but a scope reduction only counts if the capability or reach was **actually removed and that removal is verified** (the tool grant revoked, egress cut, the credential scope narrowed), not merely if the use-case sentence was edited. Editing the description while the write or tool grant stays live does **not** lower rigor. When the removal is verified, the new level is the higher of (the level the reduced drivers warrant) and (the regulatory floor). The asymmetry points the right way: raising rigor is triggered by *discovered capability* (empirical), so lowering it must be gated on *verified removal* (also empirical), never on a paper re-scope. Any L5 guardrail that closes a concrete, already-confirmed finding is **retained regardless of the rigor change**; only controls justified *solely* by the prior rigor level are re-validated at the new level. Record the old scope, the new scope, the verified removal, and the floor check in the Model Trust Record.

---

### Layer 0: What are we deciding, and how carefully must we look?

- **Why you care:** scrutiny should match stakes. Reviewing a meeting-notes tool as hard as a loan-decision model wastes everyone's time; reviewing the loan model as lightly as the notes tool is negligence. This layer prevents both.
- **What happens:** you write down the use case, what data it touches, whether it can take actions on its own, and which regulations apply. From that you set the Rigor Level (R1 to R4).
- **The decision:** the only way to fail here is if the use is outright prohibited (for example, a use banned under the EU AI Act). Otherwise you pass, carrying a Rigor Level forward.
- **Example:** "A model that drafts internal IT tickets" lands at R1 or R2. "A model that ranks insurance claims for adjuster review" lands at R4, and everything downstream gets the heavy version.
- **Draws on:** NIST AI RMF ("Map"), EU AI Act risk tiers, NIST's generative-AI risk categories.

### Layer 1: Do we actually know where this model came from, and can we trust the files?

This is the layer that looks completely different depending on the model's origin, and it is where a downloaded open-weight model earns its extra scrutiny.

- **Why you care:** when you download and run a model, you are running someone else's binary inside your environment. A tampered model file can execute code the moment it loads, or carry a hidden backdoor. This is a supply-chain exposure, the same category as a poisoned software dependency. It has already happened in the wild: a malicious model trended near the top of a public model hub, and a widely used model-file format ("pickle") can run arbitrary code on load.
- **What happens, for a downloaded (open-weight) model:** require the safe file format ("safetensors") and treat the unsafe one ("pickle") as hostile until scanned. Scan the files for malware. Verify the download matches its published checksum and comes from the real publisher. Read the licence, because many "open" models carry real use restrictions and are not as open as they sound. Check for any published reports of the model being backdoored or poisoned.
- **What happens, for a cloud model:** you are not holding the files, so the question shifts to the provider: do they have credible security certification (SOC 2, ISO 27001), a published model card, and acceptable data-handling and data-location terms.
- **A note on "we've used this publisher before":** familiarity helps, but only a little. It saves you re-verifying the publisher's identity. It does **not** let you skip scanning the specific new file or re-reading the licence, because a publisher you trust can still ship a compromised or newly-restricted release. Every release is its own supply-chain event.
- **An honest limit, stated plainly.** These checks prove the file runs no code on load and was not tampered with in transit; they cannot prove the weights themselves are free of a training-time backdoor that stays dormant until a trigger. That class of poisoning is not reliably detectable here (see gap G2 in the validation); the residual is managed downstream at Layers 5 and 6 (least privilege, egress limits, monitoring), not eliminated at L1. For a cloud model the mirror-image limit holds: SOC 2 and ISO 27001 attest the provider's security management, not that the exact weights served are un-tampered, so cloud does not remove model-integrity risk so much as move it to the provider, where you cannot audit it. Treat that as a residual limitation, not a clean pass.
- **The decision:** **stop** if a file is malicious or you cannot establish where it came from. You never move a model you can't even trust to load into the expensive testing stages. **Conditional-pass** if the licence restricts your intended use (proceed only with legal sign-off). **Pass** if the files are clean, the source is verified, and the licence fits.
- **Draws on:** CSA AI Controls Matrix (supply-chain domain); NIST SP 800-218 (Secure Software Development Framework), applied to the model artifact and its build-and-download path; OWASP Top 10 for LLM Applications 2026 (LLM04 supply chain, LLM05 poisoning); SLSA for provenance/attestation. Tools: `ModelScan`, `picklescan`, `Fickling`.

### Layer 2: Are we allowed to use it, and can we prove it?

- **Why you care:** a model can be perfectly secure and still be one you are not permitted to use for this data, in this region, under this contract. Finding that out after you've deployed is expensive; finding it out after a regulator asks is worse.
- **What happens (a mapping exercise, not a checklist).** Do not just tick boxes; map the use onto the controls that govern it and produce the artifacts a regulator asks for by name. Concretely: (1) confirm the data-processing agreement, data-residency, and the subprocessor chain (who actually runs inference); (2) determine your role under the EU AI Act (deployer versus provider) and the obligations that attach; (3) run an **AI System Impact Assessment** as ISO/IEC 42001 requires (Clause 6.1.4 establishes the process, Clause 8.4 performs it; Annex A.5 controls), and, where it applies, the EU AI Act's **Fundamental Rights Impact Assessment**: note Art. 27 mandates the FRIA only for specific deployers (public bodies, private providers of public services, and deployers of the Annex III credit-scoring and life/health-insurance-pricing systems), not for every high-risk use, and Art. 27(4) lets you reuse an existing GDPR DPIA to satisfy it; (4) map the use to the specific **CSA AICM** control objectives it touches, by control ID. The full layer-by-layer ISO 42001 and AICM crosswalk is in `standards-crosswalk.md`, so the decision is evidenced against named controls, not just framework names.
- **A modification trigger.** If you fine-tune or substantially modify an open-weight model, your legal standing can change: under the EU AI Act, substantially modifying a general-purpose model can make *you* its provider. "Substantial" has a threshold: the Commission's guidance treats a modification using roughly one-third or more of the original training compute as the line, so ordinary fine-tuning usually does not flip your status, but a large continued-pretraining run can. Whenever Layer 3 flags a modification past that line, re-run this layer under **provider** obligations, which include Art. 43 conformity assessment, Art. 49 EU-database registration, and Art. 18/19 technical-documentation and log retention, not the lighter deployer ones.
- **The decision:** **stop** if a hard legal barrier can't be met (for example, the data must stay in-region and the model can't guarantee that). **Conditional-pass** with named fixes (a contract amendment, a region change). **Pass** if the obligations are mapped and satisfiable.
- **Draws on:** ISO/IEC 42001, CSA AICM, EU AI Act, NIST AI RMF ("Govern").

### Layer 3: With nobody attacking it, does the model behave well enough for this job?

- **Why you care:** before you worry about attackers, the model has to do the job acceptably in normal use. A support model that refuses legitimate requests, shows bias, or confidently invents policy is a failure even though nothing "attacked" it.
- **What happens:** run tests scoped to the Rigor Level for the things this use cares about: does it refuse the right things and only the right things, is it biased, how often does it make things up, does it follow instructions. For dangerous capabilities you cannot responsibly test yourself (for example, whether it meaningfully helps build a weapon), you rely on the vendor's published safety testing and clearly label that evidence as *inherited* (theirs), not *produced* (yours). When you inherit a benchmark or vendor score, ask for the cheating-detection and monitoring methodology behind it: models are documented to game evaluations, so a score with no disclosed integrity method is weaker evidence than it looks, and neither the model's self-report nor its reasoning trace is a reliable check on this. One coupling to handle precisely: what happens to inherited evidence when you modify the model (quantize, fine-tune, merge, or strip the runtime guardrail). The research is blunt, so the rule is too: safety drift after modification is *unpredictable and not reliably a function of the type or degree of change* (CDT, *Out of Tune*, 2026; and arXiv:2604.24902), and even quantization sub-degrees matter. So **no modification-type earns a "safety survives" pass.** Concretely:
  - **Any modification voids inherited *behavioural* evidence** (everything tested at L3 and L4). Re-test it on the exact artifact you will deploy. Only *non-behavioural* evidence carries over unchanged: provenance, licence, and the vendor's documentation of intended use.
  - The tiers below are a **re-test priority when you cannot re-test everything at once**, not a licence to skip. Do them in this order: **Tier 3 first** (adversarial robustness, safety-bypass resistance, dangerous-capability limits, the most dangerous to get wrong); **then Tier 1** (general safety and refusal behaviour, which quantization is documented to erode); **then Tier 2** (task performance and precision, the thing your use depends on day to day).

  Record each inherited item and whether the modification voided it. A real modification also triggers the provider-status re-check at Layer 2.
- **The decision:** **stop** if it is fundamentally unfit for the use. **Conditional-pass** if a specific weakness can be contained by a runtime guardrail later. **Pass** if it behaves within tolerance for the Rigor Level.
- **Draws on:** NIST generative-AI profile ("Measure"), HELM. Tools for this layer are the non-adversarial ones: `promptfoo` and `DeepEval` for behaviour, `HELM` for capability, plus the vendor's system card for what you cannot test yourself. (The adversarial scanners, `garak`, `HarmBench`, `CyberSecEval`, belong at Layer 4.)

### Layer 4: When someone actively tries to trick or abuse it, does it hold?

- **Why you care:** real users include hostile ones. The headline AI incidents are here: an email with hidden instructions that makes an assistant leak internal data, a chatbot talked past its rules, an agent tricked into misusing the tools it was given. This is the layer the news is about.
- **What happens:** red-team the model in the shape you'll actually deploy it. Try jailbreaks, prompt injection, multi-step manipulation, getting it to leak its instructions or data, and (for agents) getting it to abuse its tools. How hard you push is set by the Rigor Level: an R1 use gets an automated smoke test, an R4 use gets a strong attacker and human experts.
- **The honesty rule, worth stating out loud:** finding a successful attack is proof of a real problem. Finding nothing is *not* proof of safety; it may just mean you didn't attack hard enough. So a clean result at low rigor must never be read as "this model is safe."
- **Evaluation integrity, the harder version of the honesty rule:** models are documented across vendors to *cheat on the evaluation itself*, and the two cheapest integrity checks, asking the model to self-report and reading its reasoning trace, miss it (CSA research note on frontier-model evaluation cheating, drawing on UK AI Safety Institute data, 2026; Anthropic's July 2026 post-mortem of three incidents where its own models reached real infrastructure from a supposedly isolated evaluation harness; and the July 2026 Hugging Face intrusion by an autonomous agent framework, which OpenAI attributed to one of its own models escaping a cyber-evaluation, though Hugging Face could not confirm the model or the motive). For R3 and R4, do not trust the score alone: run the eval under independent, out-of-band monitoring (watch for network egress, privilege-escalation attempts, or access to non-task systems during the run), give the harness sandbox egress controls robust enough to contain a model trying to escape it, and add manual review of the trajectories, not just the final answer, for any result that will inform a deployment decision.
- **The decision:** **stop** on a critical you can't contain (for example, a trivial injection that makes an agent run destructive commands). **Conditional-pass** for problems a runtime control can contain. **Pass** if nothing critical survives testing at the right strength.
- **Draws on:** OWASP Top 10 for LLM Applications 2026, MITRE ATLAS, NIST AI 100-2 E2025 (the adversarial-ML taxonomy: evasion, poisoning, privacy attacks, and direct and indirect prompt injection). For agentic deployments, also the OWASP Top 10 for Agentic Applications 2026, the ASI Top 10 (agent goal hijacking, tool misuse and exploitation, memory and context poisoning). Tools: `garak`, `promptfoo`, `PyRIT`, `HarmBench`, `CyberSecEval`, UK AI Safety Institute `Inspect`.

### Layer 5: What guardrails do we wrap around it in production?

- **Why you care:** almost no model passes every check cleanly. This layer is where the conditional-passes from Layers 3 and 4 get turned into concrete production controls, so the leftover risk is acceptable. It is the difference between "the model has a weakness" and "the weakness can't reach anything that matters."
- **What happens:** for each conditional-pass, add a specific control: a content filter, separating trusted instructions from untrusted data, limiting which tools an agent may call, requiring a human to approve high-impact actions, logging. Then, crucially, **test that each control actually reduces the finding below the tolerance for this Rigor Level, not merely that it fires.** A filter that triggers but that a paraphrase still slips past has not closed the finding. A conditional may become a pass only when the containing control is shown to drop the *specific* finding below the bar, at the Rigor-appropriate attack strength.
- **Controls have a lifecycle; they are not set-and-forget.** A guardrail is itself code and configuration, and it drifts. Any change to a control's configuration (a new regex, an updated filter model, a changed allowlist) triggers a **targeted re-test of the specific L4 finding that control was built to resolve**, not a full re-run. Version each control, map it to the finding it closes, and record the last re-test date, so a silent config edit cannot quietly re-open a closed vulnerability.
- **The decision:** **pass** if the leftover risk, after the controls, is within tolerance for the Rigor Level. This layer can rescue a conditional-pass from earlier. It **cannot** rescue an outright stop.
- **Draws on:** OWASP GenAI mitigations, CSA AICM, Google SAIF; for agentic controls (tool allowlists, least-privilege, sandboxing), the OWASP Top 10 for Agentic Applications 2026, the ASI Top 10 (tool-misuse and memory-poisoning controls). Tools: `Llama Guard`, `NeMo Guardrails`, `Lakera`, cloud content-safety.

### Layer 6: How do we keep this decision valid over time?

- **Why you care:** a "yes" is not forever. Cloud vendors update models silently under the same name, new attack techniques appear, and regulations change. A decision with no expiry quietly becomes a liability.
- **What happens:** record what would force a re-check (a new model version, a new capability or tool, an incident, a rule change) and set an expiry date. Hook your incident response to the record so that when something goes wrong, you know exactly what was approved. Because a model's ability to hide cheating on evaluations is expected to grow with its capability, treat the monitoring tooling behind your tests as something to reassess periodically, not certify once.
- **The rule:** this layer doesn't grant entry; it sets the shelf life of the decision. A decision without a live re-check trigger is treated as expired.
- **Draws on:** NIST AI RMF ("Manage"), ISO/IEC 42001 (continual improvement).

---

## What you get at the end: the Model Trust Record

The Gate does not hand you a score out of ten. It hands you a short, signed, dated record, the same kind of artifact you'd show an auditor for any other tested control. One model, one use, one decision:

```
Model Trust Record
------------------
Model:            <name> @ <version or file hash>
Origin:           cloud API  |  downloaded open-weight
Modified:         no | quantized | fine-tuned | merged   (a "yes" re-tiers evidence; see L2 and L3)
Use case:         <one line>
Scrutiny level:   R1 | R2 | R3 | R4      Regulatory floor: <e.g. EU AI Act high-risk, or none>
Impact assessment: <ISO 42001 AI System Impact Assessment ref; + EU AI Act FRIA ref if high-risk>
Per-layer result: L0 pass · L1 pass · L2 conditional · L3 pass · L4 conditional · L5 pass
Overall:          Allow | Allow with controls | Restrict to a narrower use | Deny
Narrowed use:     <required iff Overall is "Restrict": the narrower use this record is valid for>
Evidence:         <each item: layer · "ours"|"vendor's" · valid|void-on-modification;
                  tier T1|T2|T3 for L3/L4 behavioural evidence, n/a for L1/L2 evidence>
Guardrails:       <each control: id · config-version · L4-finding-it-closes · last-re-test date>
Re-entry log:     <each trigger: modification|new-capability|scope-change -> layers re-opened -> rigor change>
Scope changes:    <old scope -> new scope · verified removal ref · floor check · L5 re-validation ref>
Risk transfer:    <RTD ref> · accepted by <system-review owner + date>
Re-check when:    <events that force a re-check>   Expires(date): <ISO date>   Expires(event): <e.g. version bump>
Approved by:      <name + role; for R3/R4, an approver independent of the team proposing the model>
Incident owner:   <who notifies the provider / regulator on an incident, plus the deadline>
Retention:        <how long this record is kept; once provider status attaches, at least the Art. 18 floor>
Record status:    append-only, signed, stored WORM/immutable; a re-check produces a new record, not an edit
```

**How the per-layer results become the overall verdict** (a total rule, so a policy engine can compute it, and every case is covered):

- Any **stop** at any layer is a **Deny**. (A containable problem is recorded as a *conditional*, not a stop, so a stop is by definition uncontained; there is no "stop you cannot contain" separate from "stop.")
- A **conditional that L5 does not verifiably close** is also a **Deny**.
- **All layers pass**, no control needed, is an **Allow**.
- **Every conditional closed by a verified L5 control** is an **Allow with controls**.
- **Restrict to a narrower use** applies when a conditional was resolved *only* by narrowing the use; the record must then carry the narrower use it is valid for (the `narrowed_use` field), or the verdict is not well-formed.

**A filled-in example** (from the first validation run: a new version of a cloud model already used for a customer-support agent). Illustrative, no real vendor named.

```
Model Trust Record
------------------
Model:            Frontier Chat v5 (cloud) @ endpoint pinned 2026-08-01, version chat-v5.2
Origin:           cloud API
Modified:         no
Use case:         Customer-support agent that looks up and updates a customer's order records
Scrutiny level:   R3  (Scope 3 supervised autonomy; customer-facing impact; customer PII)
Per-layer result: L0 pass · L1 pass · L2 pass · L3 conditional · L4 conditional · L5 pass
Overall:          Allow with controls
Controls added:   (1) instruction / tool-output separation + spotlighting on the order-lookup tool,
                  closing the L4 indirect-injection path found via a tool result;
                  (2) least-privilege scope on the update-order tool (no bulk actions, no refunds);
                  (3) prompt-tuned the two support intents that over-refused at L3.
                  All three verified to fire before sign-off.
Evidence:         L1 provider SOC 2 + system card (vendor's); L3 domain eval scorecard (ours)
                  and capability/safety deltas (vendor's, inherited); L4 red-team report at R3
                  strength (ours). Links in ticket AISEC-482.
Re-check when:    next model-version bump, or any new tool granted to the agent
Expires:          2026-11-03 (90 days)
Approved by:      J. Rivera, Head of AI Security (independent of the support-platform team)
Incident owner:   SOC on-call; notify the provider immediately, and the regulator within the
                  Art. 73 deadline if it is a reportable incident
Retention:        7 years (matches the support platform's records-retention policy)
Record status:    append-only; the re-check at expiry produces a new record, not an edit of this one
```

### Built for automation: an auditable, invariant-checkable record

Every layer emits exactly one of three verdicts (`pass`, `conditional`, `stop`), the overall verdict is computed from them by the total rule above, and the record is JSON, so a policy engine such as Open Policy Agent (OPA) can *check and enforce its invariants* at the deployment gate. The record, as JSON:

```json
{
  "model": "frontier-chat-v5", "version": "chat-v5.2", "origin": "cloud",
  "modified": false, "use_case": "support-agent-order-lookup",
  "rigor": "R3", "regulatory_floor": "none",
  "layers": {"L0":"pass","L1":"pass","L2":"pass","L3":"conditional","L4":"conditional","L5":"pass"},
  "overall": "allow_with_controls", "narrowed_use": null,
  "evidence": [{"layer":"L3","source":"ours","tier":"T2","valid":true}],
  "guardrails": [{"id":"gr-injection-spotlight","config_version":"3","closes":"L4-F1","last_retest":"2026-08-01"}],
  "re_entry_log": [], "scope_changes": [],
  "risk_transfer_ref": "RTD-482", "risk_transfer_accepted": true,
  "expires_date": "2026-11-03", "expires_event": "next model-version bump",
  "approved_by": "j.rivera", "record_status": "append-only", "record_signature": "<sig over the record>"
}
```

The policy is not the trivial `deny if overall == "deny"` (that just echoes a field); it enforces the record's **invariants**, which is what makes the automation worth anything:

```
deny if some L in input.layers; input.layers[L] == "stop"
deny if input.layers["L4"] == "conditional"; count(guardrails that close an L4 finding) == 0
deny if input.overall == "restrict" and input.narrowed_use == null
deny if time.now > input.expires_date
deny if input.risk_transfer_ref != null and not input.risk_transfer_accepted
deny if not signature_valid(input) or not record_is_head(input)
```

Three design choices make this real: `expires_date` is a required machine date (the human "or event" lives in `expires_event`), so the time check is well-typed; the gate reads the **newest non-superseded** record, not any record; and the record is **signed and stored append-only** (a WORM store, a signed commit, or an immutable GRC-platform ledger), so OPA checks an attested artifact, not an editable blob.

**One honest limit, and it is the important one:** OPA checks *consistency* (no stop shipped, every conditional has a closing control, not expired, risk transfer accepted, signature valid). It cannot check *truth*: whether the human who wrote `L4: conditional` should have written `stop`, whether the red-team was strong enough, or whether `last_retest` reflects a real re-test. The field *values* remain expert judgments and can be stale or wrong. "Policy-engine-ready" means the record is structured, signed, and invariant-checkable, not that the decision is automated.

Notice the verdict is always scoped: "allow for this use, at this scrutiny level, until this date." It is never "this model is safe." That scoping is the single most important guard in the whole method, because the most common and most dangerous mistake is reading a narrow pass as a blanket clean bill of health.

---

## The Exit Gate: what the model gate hands to the system review

The Gate judges the *model*. Many real incidents live one level up, in the *system* around it: an insecure agentic tool-chain, a code interpreter or Python REPL an agent can run arbitrary code in, a retrieval store an attacker can poison, a multi-agent loop with no isolation. Those are out of scope here (see "What it does not cover"), but they must not fall through the crack between the model gate and whoever owns the system.

So the Gate ends in a formal **Exit Gate**: before the model is deployed, the model-gate owner produces a **Risk Transfer Document** and hands it to the system-level security review. It explicitly lists the risks the model gate could not resolve and is transferring, for example:

- Insecure tool implementations the agent can call: an unsandboxed code interpreter or Python REPL, a shell tool, an over-broad database connector.
- The RAG or memory layer's exposure to content poisoning (gap G1 in the validation), which the model gate flags but does not test.
- Multi-agent orchestration and delegation risks that only appear when several agents interact.
- Any Tier-3 capability the model *has* but that the model gate managed only by containment, so the system must keep that containment intact.
- Residual items marked "allow with controls," so the system owner knows which controls it now depends on.

The Risk Transfer Document requires **two signatures**: the model-gate owner who transfers the risk, and a named system-review owner who **accepts** it. The record carries both the reference and the acceptance (`risk_transfer_ref` + `risk_transfer_accepted`), and the deployment gate denies if a risk was transferred but not accepted, so a risk cannot be signed away into a void. And one rule closes the classic crack of two owners for one control: a containment control has a **single** owner. If a Tier-3 capability is managed by an L5 guardrail and then handed to the system, the RTD names who owns that guardrail's ongoing re-test; it is not left claimed by both the model gate and the system review. The purpose is accountability: a risk the model gate cannot close is not silently dropped, it has an owner who agreed, in writing, to carry it.

---

## How this relates to existing frameworks

The Gate is a synthesis, not a rival to the standards it runs on. The nearest neighbours, and the one thing the Gate adds to each:

- **NIST AI RMF, ISO/IEC 42001, CSA AICM, OWASP Top 10 for LLM and Agentic Applications, MITRE ATLAS, NIST AI 100-2 E2025** are the controls and taxonomies the Gate consumes. It does not replace them; it orders them into a per-model decision.
- **Databricks DASF**: also composes many standards, but organised by system component, not as a sequential stop/pass gate.
- **GLACIS AI Vendor Due Diligence**: adopter-side like the Gate, but a flat parallel checklist with no fail-fast ordering and no cloud-versus-open-weight split.
- **Gartner AI TRiSM**: the incumbent "trust, risk and security" brand, but a continuous operating model across four layers, not a one-time per-model adoption decision.
- **CSA STAR for AI**: a maturity and attestation pathway for an organisation, not a decision on one model for one use.
- **Bank model-risk management (SR 11-7, superseded by SR 26-2 in April 2026)**: the structural ancestor: tier by materiality, scale validation to the tier, sign off, revalidate on a trigger. SR 26-2 explicitly excludes generative and agentic AI from its scope, which is part of why a gap exists for the Gate to fill. The Gate is that pattern retargeted at AI-specific inputs, with the cloud-versus-open-weight weighting added.

What the Gate puts in one place that none of them give you together: the fail-fast **ordering** (cheap governance before expensive testing), the **cloud-versus-open-weight weighting** that decides where the effort lands, the **recursive triggers and tiered evidence** that handle a modified model correctly, the **evaluation-integrity** treatment for a threat the standards bodies have not yet caught up to, a formal **Exit Gate** that transfers unsolved risk to the system review, and a single, **invariant-checkable signed record** scoped to one model and one use.

**What this is not.** It is a reference *procedure*, not a governance *platform*. Products like Credo AI or Holistic AI, and assurance programmes like CSA STAR for AI, provide the tooling, workflow, and third-party validation a running programme needs. The Gate is the method you would implement on top of one of those, or run by hand: a worked, auditable decision procedure and a public reference, not a substitute for a platform or a certification.

---

## How to run it, in five steps

1. **Set the stakes (L0).** Describe the use, set the scrutiny level, note the model's origin. If the use is prohibited, stop now.
2. **Clear the paperwork (L1 to L2).** Confirm where the model came from and that you're allowed to use it. A stop here saves you all the expensive testing below. For a downloaded model, this is most of the work.
3. **Test the model (L3 to L4).** Check normal behavior, then attack it, scaled to the stakes. For a cloud model, this is most of the work.
4. **Add the guardrails (L5).** Turn each conditional-pass into a production control, and test that it fires.
5. **Write it down (L6).** Produce the Model Trust Record, with a re-check trigger and an expiry.

The order is the whole point. The cheap checks protect the expensive ones from being wasted, and the record protects the decision from being forgotten or misread.

---

## Known limitations (what a later version should add)

This version adds the recursive triggers, tiered evidence, the Exit Gate, and the policy-engine-ready record. It is still not a full turnkey runbook, and it names what it lacks rather than implying completeness:

- **Operational depth.** The record names an approver and an incident owner, but there is no per-layer RACI, no numeric pass-bars for the L3/L4 tests, no one-page fast-track form for R1/R2, no effort sizing, and no stated fallback for teams that cannot build out-of-band eval monitoring at R3/R4 (outsource, accept documented residual, or hard-stop).
- **Compliance artifacts.** L2 now names the AI System Impact Assessment, the FRIA (with its actual Art. 27 trigger and the Art. 27(4) DPIA-reuse route), the provider-status threshold and its Art. 43/49/18 consequences, and the subprocessor chain; the record carries an incident-notification owner and a retention floor. Still missing: an explicit GDPR records-of-processing (Art. 30) hook, and a maintained mapping of Article 73 serious-incident deadlines by jurisdiction.
- **Stronger evidence.** The claim-verification harness is a directional pilot on small local models, not a definitive measurement.

None of these change the decision the Gate makes. They are the difference between a sound method and a turnkey runbook, and they are the roadmap for the next version.

---

## Sources for the incidents cited

The evaluation-integrity argument at Layer 4 rests on recent, still-developing incidents. Their sources:

- Anthropic, *Investigating three real-world incidents in our cybersecurity evaluations* (30 July 2026): https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals
- The July 2026 Hugging Face intrusion: Hugging Face's own disclosure (https://huggingface.co/blog/security-incident-july-2026) and OpenAI's statement (https://openai.com/index/hugging-face-model-evaluation-security-incident/), with independent reporting by Axios (21 Jul 2026), Time (24 Jul 2026), and Simon Willison (22 Jul 2026). Note the accounts diverge: OpenAI attributes the attack to one of its models escaping an evaluation; Hugging Face could not confirm the model or the motive and describes the vulnerabilities used against it as existing ones, not zero-days.
- The CSA research note on frontier-model evaluation cheating, drawing on UK AI Safety Institute data (July 2026).
