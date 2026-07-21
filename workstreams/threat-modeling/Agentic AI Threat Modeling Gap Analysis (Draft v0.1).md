---
Working Group: Security & Privacy (AAIF)
Deliverable: 2 of 5, Agentic AI Threat Modeling - Gap Analysis and Framework Design
Status: Draft v0.1, for WG review
Lead: Fernando Lucktemberg
Co-lead: Alon Mazor
---

# Agentic AI Threat Modeling: Gap Analysis and Framework Design

*A Report of the AAIF Security & Privacy Working Group*

**The WG's deliverable set, for reference:**
- **D1: Taxonomy of Terms**, shared vocabulary for agentic-AI-specific threats.
- **D2: Threat Modeling Gap Analysis** (this report), whether existing frameworks adequately cover agentic-specific threats.
- **D3: Design Patterns Catalog**, architectural patterns for the gaps this report flags as build-new.
- **D4: Best Practices Guide**, operational guidance built on this report's classification baseline.
- **D5: Cross-WG Security and Privacy Review Checklist**, handoff and review checklist for findings that belong to another WG.

## 1. Executive Summary

The WG's mandate for this deliverable is sequential by design: before producing original threat-modeling guidance, the WG must first determine whether existing frameworks (OWASP, MITRE ATLAS, CSA MAESTRO, NIST AI RMF, and adjacent standards) already address agentic-AI-specific threats adequately. The WG's deliverable text named four areas where that adequacy was in doubt: multi-agent persuasion, tool invocation risk, delegated authorization boundaries, and supply chain integrity. Those four are not the full set of agentic-specific threats this WG needs to account for, only the ones the deliverable text named explicitly, so this report extends the analysis to eight areas in total, adding memory and context poisoning, agent sabotage/derailment/rogue agents, excessive agency and blast radius containment, and commerce and payment-agent risk. All eight are evaluated against the same adequacy test.

**Finding.** Across all eight areas, the major frameworks jointly provide adequate vulnerability classification, adversary-technique coding, and architectural layering in most cases. The WG does not need to build a competing taxonomy. But the analysis surfaces real, evidenced voids of three different shapes: five areas where a concrete technical or methodological gap warrants new WG-led work; two areas where the gap is real but the architectural fix belongs to a different AAIF working group, and this WG's contribution should be the governance framing plus a handoff; and one area that is not primarily a missing-control problem at all, but an unresolved jurisdictional question between this WG and the Accuracy and Reliability WG.

**Recommendation.** Adopt the existing frameworks as the WG's baseline classification system for all subsequent deliverables, and direct new WG effort at the specific voids identified in Section 6, rather than re-deriving classification work already done well elsewhere.

## 2. Background and Mission Alignment

The WG's mission statement is still in draft, with multiple candidate formulations under discussion and none yet adopted. The candidates converge on three elements: open frameworks, a shared taxonomy, and practical guidance. This report is written against those three elements.

The WG's own deliverables list states the mandate and rationale for this report directly:

> **Agentic AI Threat Modeling: Gap Analysis and Framework Design**: An evaluation of existing AI threat model frameworks (e.g., CSA Maestro, OWASP, NIST AI RMF) to determine whether any adequately address agentic-AI-specific threats, such as multi-agent persuasion, tool invocation risks, delegated authorization boundaries, and supply chain integrity (system prompt integrity, model provenance, tools manifest verification). Format: Gap analysis and guidance document. Rationale: Before the group can produce threat modeling guidance, it needs to establish whether a sufficient model already exists or whether the agentic-specific gaps are large enough to warrant new work.

That rationale is the test this report applies throughout: does a sufficient model already exist for each gap area, or is the gap large enough to warrant new work? The four areas named in that mandate are not the complete set this report evaluates.

The WG's running notes record a wider set of agentic-specific threats already in discussion, including agent derailment, agent sabotage, rogue agents, and a commerce and payments theme present since the group's earliest sessions, and this report evaluates them together rather than deferring them.

The answer is also a precondition for the Design Patterns Catalog (Deliverable 3) and the Best Practices Guide (Deliverable 4): each gap area's classification here determines whether those documents reference existing framework material or author new WG content.

## 3. Methodology

Threat modeling for agentic systems is not well served by a single framework, because no single framework answers all three questions a security program needs answered: what can break (a developer-facing classification), how attackers actually execute against it (a SOC-facing technique taxonomy), and where in the architecture the threat originates (an architect-facing layer model). This report evaluates frameworks in combination rather than independently, because a threat that surfaces in only one of the three lenses is an incomplete risk characterization, not a non-issue.

**OWASP (developer controls).** Two lists apply: the OWASP Top 10 for LLM Applications (vulnerabilities affecting any language-model system) and the OWASP Top 10 for Agentic Applications 2026, "ASI01-ASI10" (December 2025 release; the ten risk categories that emerge specifically from autonomy and tool access).
Output: control requirements a development team can build against.

**MITRE ATLAS (SOC detection).** A structured adversarial-technique taxonomy (`AML.T####` codes) mapped to a six-stage attack lifecycle (reconnaissance through defense evasion). Version baseline for this report: v4.6.0 (October 2025, the Zenity Labs collaboration that added 14 agentic-specific techniques), with v5.3.0/v5.4.0 (Jan/Feb 2026) refinements noted where they sharpen precision.
Output: SIEM detection rules and red-team technique specifications. ATLAS is built to describe adversarial technique, which matters directly for Section 4.3 below: it has no native vocabulary for non-adversarial failure.

**CSA MAESTRO (architectural hardening).** A seven-layer reference model spanning L1 (Foundation Models) through L7 (Agent Ecosystem). L6 (Security and Compliance) is a vertical layer that spans the other six rather than sitting in the stack sequence.
Output: which architectural layer to invest hardening budget in for a given threat.

**Supplementary governance frameworks**, evaluated specifically because the WG named NIST AI RMF as a comparison target:
- NIST AI RMF 1.0: Govern-Map-Measure-Manage cycle. No agentic-specific technical content, but it provides the accountability/governance scaffold OWASP/ATLAS/MAESTRO lack.
- NIST IR 8596 Cyber AI Profile: preliminary draft (December 2025), Secure/Defend/Thwart focus areas, not yet finalized.
- ISO/IEC 42001:2023: AI management system certification standard.
- CSA AI Controls Matrix v1.0: 243 controls across 18 domains, the broadest cross-framework mapping available, including crosswalks to ISO 42001, ISO 27001, and NIST AI RMF.

**The structural premise underlying most of the eight gap areas.** Agentic systems share a single architectural root cause: language models process instructions and untrusted data through the same token pipeline, with no architectural separation equivalent to parameterized queries in SQL.

This becomes exploitable when three conditions converge: access to private data, exposure to untrusted content, and external communication capability (Willison's "Lethal Trifecta"). Every agent with meaningful business capability has all three, and none of the three elements alone is dangerous.

This is why agentic-specific threats cannot be fully reduced to existing LLM-only or traditional-application threat models: the trifecta is a property of useful agent deployments, not a misconfiguration. One exception exists: agent derailment (Section 4.3) has no adversary and does not depend on the trifecta at all, which is itself part of that finding.

## 4. Findings

### 4.1 Memory and context poisoning

Persistent memory and RAG-based retrieval extend an agent's useful life across sessions, but they also extend the lifetime of a successful compromise.

OWASP classifies this under ASI06 (Memory and Context Poisoning), escalating into ASI10 (Rogue Agents) once a poisoned memory state begins acting without further attacker involvement. ATLAS's AML.T0080.000 (AI Agent Context Poisoning: Memory) gives SOC teams a specific technique code, distinct from the session-scoped AML.T0080.001 (Thread) variant relevant to Section 4.2. MAESTRO assigns this to L2 (Data Operations).

**Gap:** classification and technique coding are adequate, but no framework specifies how to resolve the tension between persistent memory (the feature that makes an agent useful across sessions) and the data-protection requirement to erase or correct memory contents once poisoning is found or once a data subject exercises an erasure right.

Provenance-tagging on memory writes (writer, timestamp, source, content hash) is a candidate way to distinguish a poisoned memory update from a legitimate one, but it has no equivalent ratified standard for agent memory stores specifically.

Crypto-shredding, encrypting per-subject data with a unique key and destroying the key on an erasure request, is a candidate architecture for the same problem, but it is not WG output, and it carries a regulatory caveat: the EDPB's 2025 guidelines on blockchain technologies hold that encrypted personal data remains personal data after key destruction, so the technique is not a certified compliance path.

Context-Based Access Control, the emerging pattern for scoping what an agent's memory can retrieve at query time, exists as engineering practice, not as a specification, in either the WG's record or the standards literature.

**Severity:** High. This is a clear build-new finding and should be sequenced alongside the supply-chain runtime-manifest work in Deliverable 3 (Section 4.7), since both are infrastructure-pattern gaps the WG is positioned to fill directly.

### 4.2 Multi-agent persuasion

OWASP's ASI07/ASI08/ASI10 correctly classify the vulnerability category (insecure inter-agent trust, cascading failures, rogue agents), and ATLAS's AML.T0080 gives SOC teams a technique code for delegation-propagated context poisoning. Neither, however, was built from an empirical failure taxonomy of *how* multi-agent persuasion actually happens in production.

That taxonomy exists, but not from a standards body: Cemri et al.'s MAST framework (arXiv:2503.13657, 2025), built from 1,600+ annotated multi-agent execution traces, identifies three failure categories (specification/design gaps, inter-agent misalignment, task verification gaps) and six cascade patterns.

The closest formal articulation of persuasion-style compromise is "conformity bias amplification": a single agent's confident, plausible-but-wrong output shifts the swarm's collective behavior because no protocol exists for adjudicating disagreement between peer agents that all carry equal nominal trust.

**Gap:** no standards-body framework names this failure mode directly or specifies a structural countermeasure (consensus protocols, diversity requirements in voting pools, delegation-boundary content inspection). MAST is academic, not normative, and has no certification or compliance standing.

**Severity:** Moderate-high. The classification exists; the countermeasure architecture does not, in any framework the WG could cite as authoritative.

### 4.3 Agent sabotage, derailment, and rogue agents

The WG's own draft taxonomy already distinguishes three related but separable terms: agent derailment (unintended deviation without malicious external cause), agent sabotage (deliberate external manipulation), and rogue agent (an agent operating outside authorized boundaries for any reason, including compromise, misconfiguration, or emergent behavior).

OWASP's ASI10 maps cleanly to rogue agent and to sabotage as its caused-by-attack variant. Agent derailment is the harder case: by definition it has no external adversary, which puts it outside what an adversarial-technique taxonomy like ATLAS is built to describe, and outside what a developer-facing vulnerability list like OWASP is built to classify, since both assume an exploitable weakness an attacker triggers. MAESTRO's L1 (Foundation Models) captures the layer where goal representation drifts, but MAESTRO does not distinguish adversarial from non-adversarial causes at any layer.

**Gap:** this is not primarily a missing-control gap, it is a scope-boundary gap, and the WG's own running notes already flag it as such: derailment was raised explicitly as "distinct from adversarial attacks" during the WG's March 3 session, and the WG's own out-of-scope list defers "Recovery from Model Poisoning" to the Accuracy and Reliability WG, marked "pending WG mission."

Non-adversarial misbehavior sits between this WG's security mandate and the Accuracy and Reliability WG's reliability mandate. No external framework will resolve that overlap, it is on the two WGs to agree how to divide the work.

**Severity:** Moderate. The detection methods overlap heavily with the behavioral baselining this WG already recommends elsewhere for its Best Practices Guide, so the unresolved piece is not technical, it is which WG owns the resulting guidance. Recommend the WG resolve this directly with the Accuracy and Reliability WG; no external framework will resolve this for them.

### 4.4 Tool invocation risk

ASI02 classifies tool misuse as a developer-facing risk category, and ATLAS's AML.T0051.001 + AML.T0053 give precise SOC detection codes for indirect injection delivered through a tool response and for tool-invocation abuse generally. MAESTRO assigns this to L3 (Agent Frameworks).

This is the best-covered of the eight gap areas in classification terms.

**Gap:** the protocol itself, Model Context Protocol, now governed by AAIF under the Linux Foundation as of December 9, 2025, has two structural trust-model defects no framework closes: OAuth 2.1 authentication is marked *optional* in the specification, and stdio transport (the most common deployment mode) is explicitly *exempt* from the OAuth framework entirely. First-party and third-party servers are indistinguishable at the protocol level.

The OWASP Secure MCP Development Guide (published February 16, 2026) codifies best practice for these defects, but it is guidance layered on top of the protocol, not a change to the protocol's mandatory security baseline.

**Severity:** High, and unusually actionable for this WG specifically: because AAIF now governs MCP, this WG has standing to recommend protocol-level baseline requirements that no other body can mandate.

Mandatory OAuth regardless of transport is not a simple specification change: MCP has no global authorization-server concept, so a bare mandate would just push every server implementer, including stdio-transport servers that today rely on local process trust rather than any network boundary, to solve authorization-server federation on their own.

Candidate resolutions that avoid that trap, as illustrative examples rather than a settled recommendation:
- **Host-as-issuer:** the client mints short-lived, scoped tokens for each server it spawns, instead of every server running its own authorization server.
- **Transport-appropriate local tokens for stdio:** a lightweight, host-issued token at spawn time, instead of forcing a network-auth flow onto a local pipe.
- **Provenance and signing for the first-party-vs-third-party problem:** supply-chain-level package signing instead of session-level authorization.
- **Reference auth library:** AAIF ships or endorses a minimal drop-in auth sidecar so implementers are not building an authorization server from scratch.

This is still the strongest case in this report for the WG doing more than evaluating; see Section 6.

### 4.5 Excessive agency and blast radius containment

OWASP names this directly: Excessive Agency (LLM06 in the original LLM Top 10, absorbed into ASI09's Human-Agent Trust Exploitation framing in the Agentic Top 10) and the accompanying Least Agency design principle. Most deployed agents are already over-privileged relative to what any single task requires.

This is distinct from Section 4.6's delegated authorization boundaries finding: an agent can be over-permissioned without ever delegating to another agent at all, simply by being provisioned once with broad standing access.

ATLAS has no single technique code for this, since over-permissioning is a precondition that enables many different downstream techniques rather than a technique in itself. MAESTRO treats it as a vertical concern under L6 (Security and Compliance).

**Gap:** OWASP names the principle, but no framework specifies a pre-deployment measurement methodology for quantifying how much agency an agent actually needs versus how much it has been granted. Without a measurement standard, "excessive" has no operational definition an auditor or procurement reviewer can apply consistently across vendors.

**Severity:** High. This is an unusually tractable build-new finding: it requires a measurement methodology, not a new architecture, and the WG's own gap-analysis-and-guidance format is the right vehicle to propose one directly.

### 4.6 Delegated authorization boundaries

This is the most explicitly documented gap of the eight, because the frameworks say so themselves. ASI03 and ASI09 (Human-Agent Trust Exploitation, the category that absorbed the original Excessive Agency vulnerability, see Section 4.5) classify the risk; AML.T0083 and AML.T0106 give detection codes for credential extraction from agent configuration.

NIST SP 800-207 makes a real accommodation, its "subject" definition explicitly includes non-human entities, but four of its seven Zero Trust tenets translate cleanly to agentic contexts and three (resource classification, dynamic authn/authz enforcement, telemetry scope) require material extension that the standard does not itself provide.

A 2025 CSA/MIT/AWS research collaboration (Huang, Narajala et al., arXiv:2505.19301) found that OAuth, OIDC, and SAML break down across several structural dimensions when applied to multi-agent delegation chains, including static and coarse scope, no native delegation-chain concept, context-blindness at runtime, secret sprawl, no peer-to-peer trust negotiation, and slow revocation.

**Gap, stated as plainly as the source material states it:** no current framework, not CISA ZTMM v2.0, not NIST AI RMF 1.0, not OWASP's Agentic Top 10, defines a governance model for accountability across a full delegation chain. Each "describes pieces of the problem": identity pillars, risk functions, threat categories. None specifies who is accountable when a sub-agent three hops downstream from the human initiator takes a destructive action under credentials traced back to a provisioning decision made weeks earlier.

Protocol-level primitives exist to narrow this gap technically (RFC 8693 token exchange with `act`/`may_act` claims; SPIFFE/SPIRE workload attestation; UCAN v1 capability tokens, specification-complete July 2025), but no IETF working group has ratified an agent-identity standard, and the median IETF timeline from draft to RFC (two to four years) makes near-term ratification unlikely.

**Severity:** High. This is a build-new finding, with one caveat: per the WG's own scope division, the architectural specification work for agent identity and delegated authorization belongs to the Identity and Trust WG, not this WG. This WG's contribution should be the governance/accountability framing above, handed off via the Cross-WG Security and Privacy Review Checklist (Deliverable 5), not a competing identity architecture.

### 4.7 Supply chain integrity

ASI04 classifies agentic supply chain vulnerabilities; AML.T0010, AML.T0011.002, and AML.T0104 give technique codes for compromise, poisoned-tool execution, and adversary-side publication of malicious components; MAESTRO assigns this to L7 (Agent Ecosystem).

**Gap:** traditional supply-chain security rests on the Software Bill of Materials model, a declarative, fixed-at-deployment-time inventory. Agentic systems invalidate that premise structurally: an agent composes its own tool access at runtime, fetching MCP servers, plugins, and sub-agent delegations in response to task context, not in response to a deployment pipeline. No framework offers a standardized equivalent of a "runtime manifest" for this.

The tooling that exists (Cisco Skill Scanner, Snyk Agent Scan, Syft/Grype for traditional SBOM) is vendor- or community-driven and useful, but it is not a ratified standard, and no two tools share a manifest format.

**Severity:** High. This is a build-new finding, and one the WG is well positioned to address without waiting on a standards body, since the deliverable format the WG already committed to (a gap-analysis-and-guidance document, followed by a pattern catalog) is the right shape for filling exactly this kind of void.

### 4.8 Commerce and payment-agent risk

This area is named explicitly in the WG's own scope document, under Cross-WG Collaboration, as a handoff to the Agentic Commerce WG (fund draining, account leaks, payment agent scope limits) and under the WG's earliest Theme H brainstorm (commerce and payments, DeFi and blockchain integration, enforcing security guardrails on commerce).

No OWASP category, ATLAS technique code, or MAESTRO layer addresses payment-agent risk as a distinct category today. The closest existing material is illustrative rather than normative: an Excessive Agency example, such as an agent with $100 refund authority approving every fraudulent refund that fits its parameters, explains a general principle, not commerce risk specifically.

**Gap:** this is the largest blank space identified in this analysis. No standards body has yet produced a payment-agent-specific threat classification, which means there is no OWASP code to adopt, no ATLAS technique to detect against, and no MAESTRO layer assignment to default to.

**Severity:** High as a gap, but explicitly out of this WG's lane per its own scope division. The appropriate action mirrors Section 4.6: document the gap and hand it off rather than building a competing classification inside this WG. Recommend routing through the Cross-WG Security and Privacy Review Checklist (Deliverable 5) once the Agentic Commerce WG has a charter mature enough to receive it.

## 5. Cross-Framework Coverage Matrix

| Gap Area | OWASP Coverage | ATLAS Coverage | MAESTRO Layer | Governance Overlay |
|---|---|---|---|---|
| Memory and context poisoning | ASI06 (Memory and Context Poisoning), ASI10 (Rogue Agents) | AML.T0080.000 (Context Poisoning: Memory) | L2 (Data Operations) | None: no erasure/retention standard for agent memory |
| Multi-agent persuasion | ASI07 (Insecure Inter-Agent Communication), ASI08 (Cascading Failures), ASI10 (Rogue Agents) | AML.T0080 (Context Poisoning, propagated via delegation) | L3 (Agent Frameworks) + L7 (Agent Ecosystem), cross-layer | None: no governance framework names this failure mode |
| Agent sabotage, derailment, rogue agents | ASI10 (Rogue Agents) covers sabotage and rogue-agent variants; no category for non-adversarial derailment | None for non-adversarial causes (ATLAS assumes an adversary) | L1 (Foundation Models) | Unresolved jurisdiction: WG's own notes flag this as Accuracy and Reliability WG-adjacent |
| Tool invocation risk | ASI02 (Tool Misuse) | AML.T0051.001 (indirect injection via retrieved content) + AML.T0053 (AI Agent Tool Invocation) | L3 (Agent Frameworks) | OWASP Secure MCP Development Guide (Feb 2026): guidance, not enforceable |
| Excessive agency and blast radius containment | LLM06 (Excessive Agency) / ASI09 (Human-Agent Trust Exploitation, absorbed Excessive Agency), Least Agency principle | None (precondition, not a technique) | L6 (Security and Compliance), vertical | None: no measurement methodology exists |
| Delegated authorization boundaries | ASI03 (Identity and Privilege Abuse), ASI09 (Human-Agent Trust Exploitation) | AML.T0083 (Credentials from AI Agent Configuration), AML.T0106 (Exploitation for Credential Access) | L3 (Agent Frameworks) | NIST SP 800-207/800-207A (Zero Trust tenets, partial fit), CISA ZTMM v2.0, NIST AI RMF: each "describes pieces of the problem" |
| Supply chain integrity | ASI04 (Agentic Supply Chain Vulnerabilities) | AML.T0010 (ML Supply Chain Compromise), AML.T0011.002 (User Execution: Poisoned AI Agent Tool), AML.T0104 (Publish Poisoned AI Agent Tool) | L7 (Agent Ecosystem) | None: SBOM model assumes fixed-at-deployment inventory |
| Commerce and payment-agent risk | None | None | None | None: largest blank space in this analysis; explicitly Agentic Commerce WG's lane |

Read across the rows: most gap areas have a named OWASP category, at least one ATLAS technique code, and an assigned MAESTRO layer. Classification coverage is strong for six of the eight. Read down the right column: governance/accountability coverage is thin or absent for nearly all of them, and two rows (agent derailment, commerce) have no classification coverage at all from any of the three frameworks. That asymmetry, and those two genuinely uncovered rows, are the central findings of this report.

**Synthesis.** Adequate, adopt as-is: vulnerability classification (OWASP's two lists), SOC-facing technique coding (ATLAS), and architectural layer assignment (MAESTRO) for the six areas that have them, memory/context poisoning, multi-agent persuasion, tool invocation risk, excessive agency, delegated authorization, and supply chain integrity. The WG should not produce a competing taxonomy for these; where the WG produces its own Taxonomy of Terms (Deliverable 1), terms should be cross-walked to these codes, not defined independently of them.

Adequate with a named gap, monitor: NIST IR 8596 (preliminary draft, finalization expected 2026), ISO 42001 (governance certification layer, already achieved by major cloud AI providers, useful as the standard most likely to be cited by EU AI Act Article 9 regulators), CSA AI Controls Matrix v1.0 (the broadest cross-mapping reference; recommended as the WG's default control-rationalization tool rather than building a new crosswalk).

Not adequate, detailed in Section 6: five concrete technical or methodological voids, two cross-WG handoffs, and one jurisdictional question with no framework-based answer at all.

## 6. Recommendations

**Primary recommendation: adopt and extend, do not build from scratch.** Use OWASP/ATLAS/MAESTRO as the WG's baseline classification system for all subsequent deliverables (the Taxonomy, the Pattern Catalog, the Best Practices Guide). Direct new WG effort at the specific voids below, grouped by what kind of action each one needs.

**Build new, this WG leads directly (five findings):**

1. **No enforceable protocol-level security baseline for tool/MCP invocation** (Section 4.4). Highest leverage: AAIF governs MCP directly, so the WG can recommend a protocol-level change rather than publishing guidance that sits beside an unchanged spec. **Action:** draft a technical recommendation to the AAIF MCP governance body for a mandatory authentication baseline across all transports, including stdio, and a minimum audit-logging baseline. Because MCP has no global authorization-server concept, evaluate candidate resolution paths, such as a host-as-issuer token model, transport-appropriate local tokens for stdio, supply-chain provenance and signing controls, and a reference auth library, rather than mandating OAuth outright (see Section 4.4).
2. **No standardized runtime-composition manifest for agent supply chains** (Section 4.7). **Action:** open Deliverable 3 with this gap as its stated rationale and specify a runtime-manifest pattern as one of its catalog entries.
3. **No erasure/retention architecture for poisoned or stale agent memory** (Section 4.1). **Action:** pair this with Deliverable 3's runtime-manifest work, since both are infrastructure-pattern gaps with no existing standard to adopt.
4. **No measurement methodology for excessive agency** (Section 4.5). **Action:** propose a pre-deployment agency-measurement checklist as part of the Pattern Catalog or the Best Practices Guide, since OWASP names the principle but provides no audit method.
5. **No countermeasure architecture for multi-agent persuasion** (Section 4.2), moderate severity. **Action:** address inside the Design Patterns Catalog rather than as a standalone initiative; the classification gap is smaller than the others in this group.

**Cross-WG handoff, this WG documents and routes (two findings):**

6. **No accountability model for multi-hop delegation chains** (Section 4.6). **Action:** circulate this report to the Identity and Trust WG liaison and finalize the handoff language before Deliverable 5 (Cross-WG Checklist) is drafted.
7. **No payment-agent-specific threat classification** (Section 4.8). **Action:** hold this finding until the Agentic Commerce WG has a charter mature enough to receive it, then route through Deliverable 5.

**Jurisdictional question, resolve directly with another WG (one finding):**

8. **Agent derailment has no clear home between this WG and the Accuracy and Reliability WG** (Section 4.3). **Action:** raise this explicitly with the Accuracy and Reliability WG; no external framework will resolve this, since it is a question of how two AAIF working groups divide their own work, not a technical gap. The WG's own out-of-scope notes already mark the adjacent "Recovery from Model Poisoning" question as pending for the same reason.

## 7. Conclusion

The WG asked a narrow question: does a sufficient threat-modeling framework already exist for agentic AI, or are the gaps large enough to warrant new work? The answer is not uniform across the eight areas this report evaluated, four named directly in the WG's deliverable text and four more surfaced by extending the same test to terms and themes already active in the WG's own running notes.

For classification and detection purposes, the existing frameworks, OWASP, ATLAS, MAESTRO, supplemented by NIST AI RMF, ISO 42001, and the CSA AI Controls Matrix, are adequate for six of the eight areas, and the WG's effort is better spent adopting and cross-referencing them than competing with them.

For governance and protocol-baseline purposes, five specific technical voids are real, evidenced, and within this WG's mandate to act on directly. Two further areas are real gaps but belong architecturally to other AAIF working groups, and one is not a framework gap at all but an open question about which WG owns it.

That distinction is what keeps this report aligned with the WG's broader mission: contributing open frameworks and practical guidance where none exist, routing work to the right WG where one does, and naming jurisdictional questions plainly rather than letting them default to whichever WG happens to write about them first.

The next deliverables in the WG's sequence (the Taxonomy, the Pattern Catalog, and the Best Practices Guide) could build on this report's findings rather than re-litigate them.

## Appendix A: Source Ledger

| Source                                                                                                                            | Type                            | Application                                                                                                                                                                                                                 |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OWASP Top 10 for LLM Applications 2025; OWASP Top 10 for Agentic Applications 2026 (Dec 9, 2025)                                  | Standards Body                  | ASI01-ASI10 and LLM01-LLM10 classification used throughout                                                                                                                                                                  |
| MITRE ATLAS v4.6.0 (Oct 2025, Zenity Labs collaboration); v5.3.0/v5.4.0 (Jan/Feb 2026)                                            | Standards Body                  | Technique codes; two codes (AML.T0083, AML.T0062) carry a verification flag pending confirmation at atlas.mitre.org                                                                                                         |
| CSA MAESTRO 7-Layer Architecture (Feb 2025); CSA Agentic Trust Framework supplement (Feb 2026)                                    | Standards Body                  | Layer assignment throughout                                                                                                                                                                                                 |
| CSA AI Controls Matrix v1.0 (Jul 2025)                                                                                            | Standards Body                  | 243 controls, 18 domains; broadest cross-framework mapping                                                                                                                                                                  |
| NIST AI RMF 1.0 (Jan 2023); NIST IR 8596 Cyber AI Profile (preliminary draft, Dec 2025)                                           | Standards Body                  | Governance overlay comparison; IR 8596 not yet finalized                                                                                                                                                                    |
| NIST SP 800-207 (Aug 2020); NIST SP 800-207A (2023)                                                                               | Standards Body                  | Zero Trust tenet-by-tenet fit assessment, Section 4.6                                                                                                                                                                       |
| ISO/IEC 42001:2023                                                                                                                | Standards Body                  | AI management system certification; EU AI Act Article 9 relevance                                                                                                                                                           |
| IETF RFC 8693 (Jan 2020); UCAN v1 (Jul 2025); SPIFFE/SPIRE (CNCF Graduated)                                                       | Standards Body                  | Delegation-chain and capability-token primitives referenced in Section 4.6                                                                                                                                                  |
| OWASP Secure MCP Development Guide (Feb 16, 2026)                                                                                 | Standards Body                  | Section 4.4                                                                                                                                                                                                                 |
| EDPB Guidelines 02/2025 on Blockchain Technologies, Section 6.3; Thoughtworks Technology Radar, "Crypto-shredding" (Trial status) | Standards Body / Analyst Report | Regulatory caveat on crypto-shredding as a candidate, non-WG, non-ratified architecture, Section 4.1                                                                                                                        |
| Cemri et al., "Why Do Multi-Agent LLM Systems Fail?", arXiv:2503.13657 (2025)                                                     | Peer-Reviewed Research          | MAST taxonomy, Section 4.2                                                                                                                                                                                                  |
| Huang, Narajala et al. (CSA/MIT/AWS), arXiv:2505.19301 (2025)                                                                     | Peer-Reviewed Research          | OAuth/OIDC/SAML structural failure modes, Section 4.6                                                                                                                                                                       |
| AAIF Security & Privacy WG Running Notes (2026-02-17 through 2026-03-17)                                                          | Internal WG Record              | Deliverable mandate text (Section 2); taxonomy terms for agent derailment, sabotage, and rogue agents (Section 4.3); Theme H and Cross-WG Collaboration scope for commerce risk (Section 4.8); mission statement candidates |
