---
Working Group: Security & Privacy (AAIF)
Deliverable: 4 of 5 - Agentic AI Security Best Practices Guide
Status: Draft v0.1, for WG review
Leads: Fernando Lucktemberg, Matthew Khouzam
---

# Agentic AI Security Best Practices Guide

## 1. Purpose and Scope

This guide consolidates practical, implementable guidance for builders deploying agentic AI systems, organized around five areas: secrets management, secure tool invocation, guardrails, eval frameworks, and post-incident forensics. It closes with a curated reference section pointing to recommended external frameworks, standards, and tooling.

**Explicitly out of scope:** agent identity and delegated authorization architecture (SPIFFE/SVID workload attestation, RFC 8693 delegation-chain encoding, UCAN capability tokens, and the broader agent-to-agent trust model). That work is contributed to the Identity and Trust WG and surfaced to this WG's audience through the Cross-WG Security and Privacy Review Checklist (Deliverable 5), not duplicated here. Where secrets-management patterns below touch credential exchange mechanics, they are scoped narrowly to credential elimination, not to the identity/authorization layer built on top of it.

Each section follows the same structure: the failure pattern in production, the architectural control, and a decision framework for selecting among options. Treat the reference section (Section 7) as the entry point for tool selection; treat Sections 2–6 as the entry point for understanding why a given control exists before procuring a tool that claims to implement it.

## 2. Secrets Management

**The failure pattern.** Static, long-lived credentials, API keys, shared service-account passwords, environment-variable-injected secrets, are structurally incompatible with agentic deployment. Every credential an agent carries is a durable attack surface: loggable, serializable, leakable to version control, and extractable through prompt injection without requiring a zero-day. Obsidian Security's 2025 AI Agent Security Report found 90% of deployed agents hold roughly ten times more privilege than any single task requires. The blast radius of a compromised static credential is not bounded by its intended scope; it is bounded only by an attacker's lateral-movement capability. CVE-2025-68664 ("LangGrinch," CVSS 9.3) demonstrated the mechanism directly: a crafted prompt triggers unsafe deserialization of an agent framework's internal state, and the serialized output contains whatever credentials were sitting in the environment.

**The architectural shift.** Move from credentials as stored assets to credentials as ephemeral attestations: generated on demand, scoped to a single operation, expired before they can be weaponized. Five patterns, in adoption priority order:

1. **Workload identity** (AWS IRSA, GCP Workload Identity, Azure Managed Identity). The correct starting point for any containerized, single-cloud deployment. The platform attests to the workload's identity via the cluster's OIDC provider; the agent's SDK exchanges that attestation for short-lived (typically one-hour) cloud credentials automatically. No code changes required. No secret exists in the environment to extract.
2. **Dynamic secrets** (HashiCorp Vault or equivalent). Covers what workload identity cannot reach: database credentials, third-party API keys, certificates. Vault issues a credential scoped to a single request with a configurable expiration (minutes to hours); the backing system cleans up the credential automatically on expiry.
3. **Network-layer injection** for legacy systems that cannot be modified to support the above (a sidecar/proxy attaches credentials at the network layer; the agent never sees them). This is a containment measure for systems you cannot yet modernize, not an architectural destination, pair it with a roadmap toward Pattern 1 or 2.
4. **Confidential computing** (Intel SGX/TDX, AMD SEV-SNP) for the highest-sensitivity contexts: regulated industries, multi-tenant isolation requirements, or threat models that include the cloud provider itself. VM-level isolation (TDX, SEV-SNP) carries roughly 2–10% overhead on CPU-bound workloads under current hardware generations, making it viable for inference and credential-handling services where the threat model justifies it. Process-level enclaves (SGX) impose significantly higher overhead and a hard memory ceiling (256 MB EPC by default, expandable but with paging penalties) that makes them impractical for most LLM workloads. Operational cost is the larger constraint in practice: attestation certificates require rotation, enclave signing keys require HSM-backed management, and any dependency update requires re-attestation. Reserve for regulated multi-tenant deployments or threat models that explicitly include the cloud provider.
5. **OAuth Token Exchange (RFC 8693)** , noted here only because it intersects credential *scope-narrowing* per delegation hop, which is relevant to blast-radius containment even outside full identity-architecture scope. Full delegation-chain treatment is out of scope for this guide; see Section 1.

**Decision framework: blast radius by pattern.**

| Pattern | Maximum Exposure Window | Blast Radius Scope |
|---|---|---|
| Static API key (no control, baseline) | Days to months, until manually revoked | Full scope of key's permissions, indefinitely |
| Dynamic secrets (Vault) | 15–60 minutes, configurable | Single resource type, single operation |
| Workload identity | 1 hour (cloud default, configurable lower) | IAM role scope; bounded by role design |
| Confidential computing | Not applicable (hardware-protected) | Bounded by enclave; inaccessible to hypervisor |

**Quick start.** Audit every agent deployment for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, or equivalent long-lived secrets in environment variables or image layers. Replace each with the platform-native workload identity mechanism. This single change removes the most common credential-extraction pathway (the CVE-2025-68664 class) and shrinks blast radius from "full cloud account access, indefinite" to "scoped role access, one-hour maximum."

## 3. Secure Tool Invocation

This section covers three adjacent attack surfaces that production deployments encounter together: the protocol layer agents use to reach tools (MCP), the supply chain of skills and extensions agents load, and the implementation of the tools themselves once they are invoked.

### 3.1 MCP Protocol Security

**The failure pattern.** MCP (Model Context Protocol, launched by Anthropic November 2024, now governed by AAIF under the Linux Foundation) is the de facto standard for agent-to-tool communication: 97M+ monthly SDK downloads, 10,000+ active public servers, first-class support across every major AI platform. Its trust model has two structural gaps the specification leaves open by design: OAuth 2.1 authentication is marked *optional*, and stdio transport, the most common local deployment mode - is explicitly *exempt* from the OAuth framework. First-party and third-party servers are indistinguishable at the protocol level. The documented attack classes:
- **tool poisoning** (malicious instructions hidden in a tool's description field, including via invisible Unicode tag characters U+E0000–U+E007F)
- **rug pulls** (a server behaves legitimately for weeks, then updates its tool definitions to request broader permissions or deliver manipulated content, with no client-side re-verification)
- **cross-server shadowing** (a malicious server reroutes a sensitive operation to a different, compromised server without notifying the operator)
- **sampling-based resource theft**
- **conversation hijacking** (documented by Palo Alto Networks Unit 42). The incident record: the first malicious MCP server (Sept 2025, impersonating an email service, 1,643+ downloads before discovery), CVE-2025-6514 (CVSS 9.6, mcp-remote RCE, 437,000+ downloads at disclosure), and the Smithery hosting-platform breach (3,000+ downstream applications affected).

**The control.** OAuth secures the *connection*; it does not secure the *content* of what a verified server sends. Both layers are required:

- **Pre-deployment evaluation, every server, no exceptions:** confirm the source repository exists (if public) and has been active within 90 days; cross-reference against a public vulnerability tracker such as the [Vulnerable MCP Project](https://vulnerablemcp.info/), paired with [CVE/NVD](https://nvd.nist.gov/) and the [GitHub Advisory Database](https://github.com/advisories); run a static scanner ([Cisco MCP Scanner](https://github.com/cisco-ai-defense/mcp-scanner) as the minimum viable check; [Snyk Agent Scan](https://github.com/snyk/agent-scan) as a runtime complement) before any production connection.
- **Transport requirements:** treat third-party stdio servers as equivalent to running an arbitrary local binary, full user privilege, no cryptographic provenance. For HTTP transport, OAuth 2.1 is required regardless of what the spec marks as optional. Three remote authorization patterns emerge from the spec's OAuth 2.1 base, each with a different security posture:
  - **User-direct authorization.** The MCP client initiates an OAuth 2.1 authorization code flow with PKCE; the user consents in a browser session; the resulting token is audience-bound to that specific MCP server via the RFC 8707 `resource` parameter, which the spec requires in both the authorization request and the token request. Use this when the agent acts on behalf of a human user and that user's identity is meaningful to the tool.
  - **Agent with shared IdP.** The agent already holds a token from an authorization server the MCP server also trusts. The agent presents that token directly in the `Authorization: Bearer` header with no new user-facing consent step. Use this in intra-organizational deployments where the agent platform and MCP server share a corporate IdP. The token must still be audience-bound to the MCP server (RFC 8707); do not accept a generic platform-wide token as a valid credential for the MCP server.
  - **Machine-to-machine (no user identity).** The agent acts as its own principal using the OAuth 2.1 `client_credentials` grant, with no user delegating principal involved. Use this for background tasks and automated pipelines. Scope the client to the minimum permissions the pipeline requires and bind the client registration to the specific MCP server URI (RFC 8707) to prevent token reuse across servers.

  In all three patterns: validate token audience binding before accepting any request; a token issued for a different resource is not a valid credential for the MCP server.
- **Gateway enforcement** for any deployment with more than one MCP server: route all agent-to-tool traffic through a single checkpoint (Cloudflare MCP Portals, or the open-source Linux Foundation `agentgateway` project) that enforces OAuth, applies per-tool permission policy, and captures full request/response payloads.
- **Runtime invariants:** no tool invocation may touch a data category outside its declared scope; no tool invocation may reference a server outside the approved registry; tool description hashes must be compared at every session start to detect rug-pull changes.

### 3.2 Supply Chain & Skill Verification

**The failure pattern.** An empirical study of 31,132 marketplace skills (Liu et al., [arXiv:2601.10338](https://arxiv.org/abs/2601.10338)) found 26.1% contained at least one vulnerability across prompt injection, data exfiltration, privilege escalation, and supply chain categories, with 5.2% showing high-severity patterns that suggest malicious intent. Poisoned skills are not just present, they are effective: adversarially rephrased skill-injection attacks reach an 81.4% success rate against frontier coding agents (Fujinuma et al., [arXiv:2606.01567](https://arxiv.org/abs/2606.01567)). [Snyk's ToxicSkills study](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) found hardcoded secrets in 10.9% of scanned skills. The Cato CTRL proof-of-concept showed how low the bar is: a single inserted function call in an otherwise-legitimate, open-source skill delivered ransomware, with the skill's stated purpose and description unchanged. The deeper structural problem is the **consent gap**: approving a skill's first execution can authorize a scope of action broader than what was previewed, and that approval persists as a standing grant, not a one-time decision, until explicitly revoked.

Skills are not the only artifact in the supply chain. MCP server packages are distributed software with their own binary supply chain, independent of the protocol they speak. A2A Agent Cards are metadata documents an orchestrator consumes to decide what to trust and invoke from a remote agent. Each carries distinct failure modes and requires its own verification controls.

#### 3.2.1 Skills

**The control: a four-tier verification model.**

1. **Tier 1 - automated pre-scan, required for all skills.** Run Cisco Skill Scanner (static pattern matching, behavioral dataflow analysis, optional LLM-based semantic review) or Snyk Agent Scan. Any Critical or High finding disqualifies the skill from proceeding without remediation.
2. **Tier 2 - manual structural review, required for skills requesting elevated permissions.** Check the `allowed-tools` field against the stated purpose (a text formatter requesting `Bash`/`Write`/`WebFetch` is a mismatch); scan bundled scripts for calls to undeclared domains, `eval()`/Base64-obscured code, or file paths reaching toward `~/.ssh` or `~/.aws`; verify author attribution.
3. **Tier 3 - organizational trust registry, required for production.** Pin approved skills to a specific version and hash; assign a named accountable owner distinct from the requester; require re-verification on any update.
4. **Tier 4 - runtime behavioral monitoring, required for skills with elevated permissions or production deployment.** Monitor executed behavior against the declared `allowed-tools` scope and Tier 2 baseline; flag any invocation touching a domain, file path, or tool absent from the approval record. See Section 5 (Evaluation Frameworks) for behavioral baselining implementation.

#### 3.2.2 MCP Server Packages

**The failure pattern.** An MCP server is a distributed software package (npm, PyPI, or container image) with a full binary supply chain independent of the protocol it speaks. CVE-2025-6514 (mcp-remote, CVSS 9.6) was not a protocol attack — it was a compromised package executing arbitrary code on connection. A server that passes verification today can be backdoored in its next release; version-pinned deployments are the only protection against silent updates.

**The control: three verification steps.**

1. **Step 1 - SBOM scan before any production connection.** Generate a software bill of materials (Syft) and scan for known CVEs (Grype) against the server package and all transitive dependencies. Any Critical or High finding blocks the connection until remediated. An SBOM describes a single package. Capturing what the agent as a whole is composed of requires an agent-level bill of materials spanning its tools, MCP servers, skills, models and policies, an inventory now specified as the AgBOM in the [OWASP Agent Control Standard](https://github.com/GenAI-Security-Project/agent-control-standard) with CycloneDX, SPDX and SWID serializations.
2. **Step 2 - version pinning, publisher verification and artifact provenance.** Pin the approved server to a specific version hash in your organizational registry, and treat any version update as untrusted until Step 1 completes again. Verify that the source repository matches the declared publisher to catch impersonation. A second check catches a different problem: a published package can carry code that is absent from its source repository, for example an exfiltration line added to the distributed tarball. Verify the shipped artifact against the source it claims to come from. Require build-linked attestation, npm provenance or PyPI attestations (both Sigstore-backed) for packages, and image signing (Sigstore/cosign) for containers, and verify it before instantiation. Where a package publishes no attestation, diff the tarball against the tagged source before approval and treat any divergence as the finding.
3. **Step 3 - update monitoring.** Subscribe to the server package's release feed and treat any new version as blocked by default until Steps 1 and 2 complete. This closes the same rug-pull window that Section 3.1 addresses at the protocol layer, but at the binary layer.

#### 3.2.3 A2A Agent Cards

**The failure pattern.** The A2A Agent Card (`/.well-known/agent-card.json`) is the metadata an orchestrator consumes to decide what to trust and invoke from a remote A2A agent — the structural equivalent of an MCP tool description. It declares the agent's skills, authentication requirements, and service endpoint. The A2A spec's default well-known URI discovery has no built-in integrity verification: any party who can serve that path can substitute a poisoned card. Skill description fields in Agent Cards carry the same prompt-injection risk as MCP tool description fields. Authentication scheme declarations can be downgraded or replaced to redirect credential acquisition to an attacker-controlled endpoint. There is no standard re-verification trigger when a card changes after initial approval.

**The control: three verification steps.**

1. **Step 1 - hash and pin at first approval.** On first contact with an A2A agent, record a content hash of the Agent Card and store it in your organizational registry alongside the approved agent identity. This is the baseline for all subsequent change detection.
2. **Step 2 - re-verify on every session start.** Fetch the Agent Card at the start of each session and compare its hash against the registry record before invoking any skill. Any change to skill descriptions, authentication schemes, or the service endpoint must be treated as an unapproved update and routed through re-review at the tier the agent's declared permissions require. This closes the same rug-pull window Section 3.1 addresses for MCP tool descriptions.
3. **Step 3 - restrict discovery to a curated registry.** Do not rely on open well-known URI resolution for production agents. The A2A spec describes curated registries as the standard approach for enterprise environments, providing centralized management, capability-based discovery, and support for access controls and trust frameworks. Maintain a registry of approved Agent Cards under organizational control; require authenticated extended cards for any agent with elevated access rather than accepting unauthenticated public cards.

**Environment risk stratification** determines blast radius independent of the artifact type — apply this before verification controls, not instead of them:

| Environment | Network Access | Filesystem Access | Blast Radius |
|---|---|---|---|
| Sandboxed code-execution VM (no network) | None | Temporary VM only | Minimal |
| Sandbox mode enabled, working-directory scoped | Allowlisted only | Current working directory | Contained |
| No sandbox | Full | Full user account | Enterprise-wide |

**Quick start.** Enable OS-level sandbox mode across all developer environments before building any review pipeline — it is a configuration change, not a process build, and it reduces the blast radius of any unverified artifact from full system access to working-directory scope.

### 3.3 Tool Implementation

**The failure pattern.** Protocol authentication governs how an agent reaches a tool, and supply-chain verification governs where the tool came from. Neither governs what the tool does with the arguments it receives. A large class of MCP vulnerabilities lives here: a tool that passes model-supplied arguments into a shell command, a database query, or a file path without validation turns a prompt injection upstream into command injection, SQL injection, or path traversal at the point of execution. The LLM sits between user intent and the tool call, so an argument that looks benign in the transcript can carry an injection payload the tool executes with its own privileges.

**The control.** Treat the tool boundary as a trust boundary, and never delegate security-critical validation to the model:

1. **Validate every parameter at the tool boundary.** Enforce a strict schema (type, range, format, allowlist) on each argument inside the tool handler, before it reaches any interpreter, query, or filesystem call. The model's output is untrusted input.
2. **Design constrained, use-case tools rather than general-purpose ones.** Replace an open primitive such as `query_database(sql)` with a narrow operation such as `get_order_status(order_id)`, and build the query server-side. A tool that cannot express a dangerous operation cannot be manipulated into performing one.
3. **Give tools least-privilege credentials.** Scope the tool's own credentials to the minimum it needs: read-only database connections, allowlisted tables, no ambient filesystem or network access beyond its declared purpose (Section 2).
4. **Keep code execution out of handlers.** Do not expose `exec`, `eval`, `subprocess`, or equivalent dynamic execution in a tool handler that receives model-supplied arguments. Where dynamic execution is the tool's purpose, run it in the isolated environment described in the risk-stratification table above.
5. **Treat tool output as untrusted input before it re-enters context.** A tool's response can carry injected instructions (Section 3.1 tool poisoning, Section 3.2.3 Agent Cards); validate and, where relevant, sanitize it before it is fed back to the model.

## 4. Guardrails

**The failure pattern.** Most production HITL (human-in-the-loop) implementations fail as security controls for three architecturally specific reasons: flat decision presentation (a README update and a production table deletion render identically, training reviewers to rubber-stamp), velocity-optimized success metrics (a reviewer who pauses for genuine review is rated as underperforming), and context-stripped interfaces (the reviewer sees the proposed action but not the reasoning chain or impact radius behind it). The result: AI safety incidents grew 50%+ from 2023–2024; documented production failures include an 847GB/15-million-record database deletion and a $25M fraudulent wire transfer executed after a deepfake video call, each with a nominal human-oversight control present and functionally absent.

**Input and output handling: reduce likelihood, do not assume prevention.** Prompt injection is the mechanism behind the failures in Sections 2, 3.1, and 3.2.3, and it is the default case: untrusted content reaches the model constantly, through retrieved documents, tool results, and delegated messages. A key limitation shapes every control here: at inference the model sees one token stream, so message roles, delimiters, and "system" framing are soft priors the model was trained to weight, not boundaries it can enforce. Injected text lives in the same pipeline and can imitate any of them. Prompt-layer measures therefore reduce the likelihood of a successful injection; they do not prevent it.
1. **Prefer structured message roles over string interpolation.** Assembling prompts through typed roles rather than concatenating untrusted text into one instruction string biases the model toward treating system text as authoritative and makes role-confusion attacks harder. Treat this as hardening, not a boundary.
2. **Tag retrieved content and tool results as untrusted data.** Carry provenance so downstream controls know which spans originated outside the operator's trust boundary.
3. **Screening models are a filter, not a boundary.** A separate guard or classifier model that inspects prompts and responses is worth deploying as one probabilistic layer, but it has a real false-negative rate. Research on adaptive attacks has shown that defenses reporting strong results under static testing can be systematically defeated once an attacker tailors the attack to the defense, so a classifier's reported detection rate is not a robustness guarantee ([Nasr et al., arXiv:2510.09023](https://arxiv.org/abs/2510.09023)).
4. **Filter output before it reaches a sink.** Screen model output before it is written to a database, sent over the network, or passed to another tool.

Because none of the above is a boundary, the controls that actually bound the damage are execution-layer: parameter validation at the tool boundary (Section 3.3), least-privilege tool credentials (Section 2), and the authorization framework below, which assumes injection will sometimes succeed and limits what the agent can do next.

**The control: a four-tier authorization framework**, with tier assignment made at design time by an orchestration-layer classifier, never accepted as self-reported by the agent, since a prompt-injected agent will label its own exfiltration attempt as low-risk if given the chance.

| Tier | Mechanism | Example Operations |
|---|---|---|
| 1 - Autonomous + audit sampling | No approval request; statistical post-hoc review (10% initial, 2–3% after 90-day baseline) | Synthetic test data, doc formatting from templates |
| 2 - Async notification | Approval requested; agent continues unrelated work; 4-hour window, auto-escalates on expiry | Production read queries, non-breaking config changes |
| 3 - Synchronous pre-approval | Agent halts; full context (reasoning trace, impact radius, validation checklist) required before approval renders | PII writes, pricing changes, cross-system writes |
| 4 - Dual authorization | Two independent reviewers, separate sessions; out-of-band verification for high-risk thresholds | Irreversible operations, any non-allowlisted external destination, financial/privileged-access changes |

Tier 4 triggers automatically for any external network request regardless of the agent's own stated risk assessment, destination classification overrides agent intent by design, closing the specific bypass where an injected agent self-labels its exfiltration attempt as routine.

**Interface engineering matters as much as the tier logic.** Four principles separate a functioning control from theater:
1. solve-verify asymmetry, the reviewer validates a recommendation, not a reconstructed analysis, so the interface must present plain-language action, tier rationale, impact radius, and a short validation checklist 
2. the approval affordance must be architecturally unavailable until required context has been traversed
3. approval rate is tracked as a time series and flagged for fatigue when it climbs within a shift
4. synthetic anomaly requests are injected at randomized intervals to measure genuine reviewer detection rate, not just throughput.

**Containment guardrails at the orchestration layer** (relevant wherever agents delegate to other agents, not only at the human-approval boundary): trust-boundary inspection at every delegation handoff (does the payload exceed declared scope, request undeclared permissions, or reference unapproved external endpoints); circuit breakers that open after repeated inspection or attestation failures and fail to a defined chain (secondary agent → cached last-verified response → human escalation , never silent autonomous retry); bulkheads that isolate compute, memory, and API quota per domain so a compromised low-sensitivity cluster cannot reach a high-sensitivity one; and a kill switch whose state lives **outside** the agent runtime (a compromised agent with write access to its own environment can otherwise disable its own kill switch). Kill switches require three granularities: individual agent, agent group, global, and a graduated degradation path (reduce autonomy, then tool access, then require checkpoint approval, then disable) rather than a single binary stop, because an instant global halt across a large swarm is itself an operational event that needs to be weighed against the threat it responds to.

**Quick start.** Map every operation type to a lifecycle and tier before writing approval code; implement tier classification in the agent's action layer, not the approval interface; enforce the Tier 4 two-reviewer rule as a database constraint, not a UI gate; connect approval logs to the Security Information and Event Management (SIEM) before go-live; test the kill switch in staging before day one, a kill switch that has never been drilled should be assumed non-functional.

## 5. Evaluation Frameworks

**The failure pattern.** Conventional threshold-based alerting does not work reliably against non-deterministic agent behavior. For example, an agent processing a malicious input will not necessarily trip a fixed token-count or error-code threshold. Evaluation has to operate at three distinct points:
1. before deployment (does this agent/server/skill meet a security bar at all)
2. during the deployment ramp (is the organization actually ready to operate the controls it has built)
3. continuously in production (has behavior drifted from baseline).

**Pre-deployment evaluation.** Use adversarial CTF-style platforms to train and calibrate security engineers against the actual vulnerability classes before they show up in your environment, the [OWASP FinBot capture-the-flag platform](https://owasp-finbot-ctf.org/) is the recommended vehicle for hands-on exposure to the Agentic Top 10 categories. Apply the same pre-deployment evaluation criteria documented in Sections 3.1 and 3.2 (MCP server scanner findings, skill verification tiers) as gating criteria, not advisory output: a Critical/High finding blocks production connection until remediated, full stop.

**Readiness evaluation.** Before any tiered guardrail system (Section 4) goes live, run it against a structured readiness checklist: are tier definitions documented and mapped to actual operation types (not inferred after the first incident); does the approval interface surface full context (tested by having an unfamiliar reviewer evaluate sample requests using only the interface); is the kill switch drilled, not just documented; is the classifier model version recorded with a defined recalibration procedure for when it changes. A graduated rollout, read-only with full audit (weeks 1–4), limited autonomy with high-density sampling (weeks 5–12), full tier architecture (months 4–6), steady state (month 7+), is the evaluation structure itself, borrowed from safety-critical systems practice (FAA AC 120-35D), not an optional staging preference.

**Continuous/behavioral evaluation.** Establish statistical baselines across five dimensions and treat deviation as the detection signal, since fixed thresholds do not transfer to probabilistic systems: tool-call frequency per agent identity, parameter entropy of tool invocations (anomalously low entropy suggests templated, automated exfiltration rather than organic task execution), inter-agent message volume relative to baseline, token-count ratios across model calls, and memory-write frequency against established patterns. Treat reasoning traces ("chain of thought") as a corroborating signal only, never as the primary evidentiary basis for an evaluation conclusion: Anthropic's own research found reasoning models verbalized use of an injected hint only 25% (Claude 3.7 Sonnet) to 39% (DeepSeek R1) of the time in sensitive-prompt test conditions , exactly the conditions where an evaluator would most need the trace to be honest. [Anthropic's Petri](https://www.anthropic.com/research/petri-open-source-auditing) auditing tool, by comparison, ran a pilot across 14 frontier models using 111 seed instructions and surfaced misaligned behaviors for human review, which is the right way to read eval output: assume you will find something, and design the eval to surface it rather than to produce a clean pass.

**Quick start.** Treat the scanner/checklist gates in Sections 3 and 4 as your first eval framework, they already exist, they are concrete, and most organizations are not yet enforcing them as hard gates. Layer behavioral baselining on top only after those gates are operating reliably.

## 6. Post-Incident Forensics

**The failure pattern.** Most production deployments capture operational telemetry (latency, error rates, token counts) and call it an audit trail. It is not one. [IBM research places average breach identification at 204 days](https://acsense.com/blog/ibm-2024-cost-of-data-breach-report/). An agent that misbehaved in October may not surface until April, and if the log lacks a verifiable record of every action, delegation, and approval, the investigation has no evidentiary foundation to reconstruct from. This gap now carries statutory weight: EU AI Act Article 12 record-keeping is a requirement for Annex III high-risk systems, applicable from [2 December 2027 under the AI Omnibus timeline](https://digital-strategy.ec.europa.eu/en/news/ai-omnibus-enters-force); non-compliance is enforced through the provider and deployer obligations (Articles 16 and 26), which carry administrative fines up to EUR 15M or 3% of worldwide annual turnover.

**The control: seven event categories**, most deployments today capture roughly three of them:

1. **Action events** - every tool invocation/API call/database write, with tool ID, parameters, response, agent identity, and the credential active at execution time. The credential field is where most implementations fail; without per-agent identity (Section 2), delegation-chain reconstruction is not incomplete, it is structurally impossible.
2. **Reasoning traces** - captured, but explicitly tagged `unverified` and treated as corroborating, not primary, evidence (see Section 5).
3. **Approval/HITL events** - approver identity, timestamp, rationale, and a reference to the specific artifact reviewed. An approval record with no artifact reference is a signature on a blank document.
4. **Memory/context write events** - provenance metadata (writer, timestamp, source, content hash) on every write, without which a poisoned memory update and a legitimate one are indistinguishable in the log.
5. **Credential lifecycle events** - issuance, usage, expiration, revocation for every credential an agent touches.
6. **Model call events** - provider, model, token usage, finish reason, conversation ID; map [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai) into a stable internal envelope rather than depending on the raw attribute names directly, since the convention remains in Development status as of this writing.
7. **Delegation chain events** - W3C Trace Context propagation (128-bit `trace-id`, per-span `parent-id`) across every agent-to-agent handoff, the only way to reconstruct "who delegated what to whom, in what order" without relying on timestamp correlation that clock drift makes unreliable. The `trace-id` serves as the global invocation ID: a single immutable identifier generated at the root invocation and propagated unchanged through every downstream agent, tool call, and MCP or A2A hop in the chain. It must be generated once at the entry point of each user- or system-initiated invocation, written into every event category above, and never reused or regenerated mid-chain; any break in propagation makes full trace reconstruction impossible.

   Both MCP and A2A carry the primitives for this but do not mandate them. The MCP specification reserves `traceparent`, `tracestate`, and `baggage` as `_meta` fields and states "when present, their values MUST follow W3C Trace Context and W3C Baggage formats respectively" without requiring that implementations include them. The A2A enterprise guidance recommends propagating trace context through W3C Trace Context headers and logging `taskId`, `sessionId`, and correlation IDs, but treats both as non-normative. This guide requires `traceparent` propagation in every MCP request and A2A interaction under your control as a security best practice: include it, and log a forensic gap notice for any hop where it is absent or dropped. For external agents, prefer those that surface a stable correlation ID (`taskId`, `sessionId`, or equivalent) in their responses; where an external agent does not, flag that agent in your registry as carrying an unresolvable forensic gap and factor that into its trust tier.

**Integrity architecture**, three components together:
1. per-entry cryptographic signing at write time
2. Merkle-tree append structure (Certificate Transparency model, any retroactive modification to a historical entry becomes detectable against an earlier published root hash;
3. Google's [Trillian](https://github.com/google/trillian), or its newer successor [Tessera](https://github.com/transparency-dev/tessera), provide production-ready implementations); and write-only forwarding to a destination where the agent's own credentials carry no delete permission.

**Two-stream pipeline.** A compliance stream (action, approval, delegation, model-call, decision events; 100% capture, no sampling, cryptographic integrity, retention-locked storage) and an operational stream (verbose reasoning traces, diagnostics, performance metrics; sampled, short retention, basic checksums only). Assignment is by event category, not by system importance or volume, this also resolves most data-minimization tension, since personal data confined to the operational stream ages out quickly and was never written to the protected compliance stream at all.

**Kill-switch runbook as a forensic artifact, not just a containment one.** A usable runbook specifies four things explicitly:
1. the exhaustive trigger conditions (so an on-call engineer is not exercising judgment under pressure about whether a threshold was met)
2. the authority chain (who can trigger an immediate halt versus who must sign off on restart , these should differ)
3. the ordered restart checklist (injection vector identified and mitigated, full credential rotation, log review of the window preceding the halt, explicit owner sign-off)
4.  the forensic preservation requirement (execution log, pending approval queue, memory contents, and active tool invocations snapshotted to immutable storage *before* any state is cleared , an automated restart that clears state as part of its sequence will destroy the evidence the investigation depends on).

**Quick start, in sequence:** 
1. establish per-agent identity before anything else, shared service-account identity makes every downstream attribution requirement impossible to satisfy
2. instrument action, approval, and model-call events first, since they cover the highest-priority regulatory obligations
3. propagate W3C Trace Context across delegation boundaries
4. add per-entry signing and Merkle append with a published baseline root hash
5. complete the remaining event categories
6. stand up the operational stream and behavioral baselines (Section 5) last, since they have no value without the compliance stream already running underneath them.

## 7. Curated External Reference Section

Maturity: GA (production-ready), Beta (publicly released with caveats), Experimental. Cost: Free, Moderate ($100–$2,000/mo at team scale), Enterprise. Status reflects early 2026; re-verify before procurement.

**Cost column definitions.** "Free" means self-hostable with no per-usage charge (open-source license). "Moderate" means a cloud-hosted or managed tier exists at roughly $100–$2,000/month at team scale. Where a tool lists both (e.g., Snyk Agent Scan, Langfuse), the open-source self-hosted version is free and the managed/SaaS version is Moderate. Cloudflare MCP Portals is commercial-only with no self-hosted option; its Moderate rating reflects current beta pricing, which may change at GA.

| Area | Tool | Type | Maturity | Cost | Notes |
|---|---|---|---|---|---|
| Secrets - dynamic | HashiCorp Vault Community | Open Source | GA | Free | BSL license; dynamic secrets, credential issuance |
| Secrets - workload identity | AWS IRSA / GCP WIF / Azure Managed Identity | Managed | GA | Free | Cloud-native; no cost beyond platform |
| Tool invocation - MCP static scan | Cisco MCP Scanner | Open Source | Beta | Free | Multi-engine; YARA + LLM-as-judge |
| Tool invocation & skill scanning | Snyk Agent Scan | Open Source / Commercial | Beta | Free/Moderate | Scans MCP servers and skills; runtime constraint enforcement and logging; 90–100% recall on confirmed-malicious skills in vendor testing |
| Tool invocation - MCP gateway | Cloudflare MCP Portals | Commercial | Beta | Moderate | Full audit trail; OAuth; tool-level permissions |
| Tool invocation - MCP gateway (OSS) | Linux Foundation agentgateway | Open Source | Beta | Free | Kubernetes-native; supports MCP and A2A |
| Supply chain - skill scanning | Cisco Skill Scanner | Open Source | Beta | Free | Static + behavioral dataflow + optional LLM review |
| Supply chain - skill scanning | NVIDIA SkillSpector | Open Source | Beta | Free | Two-stage static + optional LLM analysis across prompt injection, supply chain, excessive agency, and MCP-specific patterns; Apache 2.0; part of NVIDIA Verified Skills pipeline |
| Supply chain - SBOM baseline | Syft / Grype (Anchore) | Open Source | GA | Free | Traditional SBOM + CVE scanning; CI/CD native |
| Guardrails - HITL orchestration | LangGraph | Open Source | GA | Free | Static/dynamic interrupts; native checkpointing |
| Guardrails - HITL orchestration | Dapr Agents | Open Source | GA | Free | Durable agent workflows with deterministic replay + native HITL interrupts built on Dapr Workflows. |
| Guardrails - input/output | NeMo Guardrails (NVIDIA) | Open Source | GA | Free | Input/output moderation, jailbreak detection |
| Guardrails - PII | Presidio (Microsoft) | Open Source | GA | Free | PII identification/anonymization at ingestion |
| Guardrails - inter-agent comms & policy | Dapr | Open Source | GA | Free | mTLS sidecar isolation between agents, service-invocation access-control allowlists, OPA policy middleware, secrets API abstraction over Vault/Cloud stores, workflow level tool-access policies (to gate/block tools), PII scrubbing and input/output hooks |
| Guardrails - execution isolation | gVisor / Firecracker | Open Source | GA | Free | Kernel- and microVM-level sandboxing for agent-generated code and tool execution with ephemeral per-task environments |
| Eval - pre-deployment | OWASP FinBot (genai.owasp.org) | Framework / CTF | GA | Free | Hands-on Agentic Top 10 exposure |
| Eval - misalignment auditing | Anthropic Petri | Open Source | GA | Free | Pilot tested 14 frontier models across 111 seed instructions; surfaced misaligned behaviors for review |
| Forensics - observability | Langfuse | Open Source / Managed | GA | Free/Moderate | Session-level tracing; GDPR-native design |
| Forensics - log integrity | Tessera (transparency-dev), successor to Trillian | Open Source | GA | Free | Merkle append; recommended path for new deployments |
| Forensics - tracing standard | OpenTelemetry GenAI Semantic Conventions | Standard | Development | Free | Wrap in a versioned internal envelope; not yet stable |
| Forensics - runtime detection | Falco | Open Source | GA | Free | eBPF syscall monitoring; CNCF Graduated |
| Forensics - compliance mapping | CSA AI Controls Matrix v1.0 | Framework | GA | Free | 243 controls; EU AI Act + GDPR + NIST + ISO 42001 crosswalk |

## Appendix A: Source Ledger

| Source | Type | Application |
|---|---|---|
| OWASP Top 10 for Agentic Applications 2026 (Dec 9, 2025); OWASP Secure MCP Development Guide (Feb 16, 2026) | Standards Body | ASI classification and MCP guidance throughout |
| OWASP Agent Control Standard (GenAI Security Project) | Open Standard | Section 3.2.2 (AgBOM) |
| MITRE ATLAS v4.6.0–v5.4.0 | Standards Body | Technique codes referenced inline |
| CVE-2025-68664 (LangGrinch), CVE-2025-6514 (mcp-remote), CVE-2025-49596 (MCP Inspector) | CVE Record | Section 2 and 3.1 incident grounding |
| Liu et al., "Agent Skills in the Wild," arXiv:2601.10338 (2026); Fujinuma et al., "Defenses & Enablers for Skill Injection Attacks," arXiv:2606.01567 (2026) | Peer-Reviewed Research | Section 3.2 |
| Snyk ToxicSkills Study (Feb 2026) | Vendor Research | Section 3.2 |
| Cato CTRL, "Weaponizing Claude Skills with MedusaLocker" (2025) | Vendor Report | Section 3.2 |
| A2A Protocol Specification, Agent Discovery and Enterprise Implementation (a2aproject/A2A, docs/topics/agent-discovery.md and enterprise-ready.md) | Open Standard | Section 3.2.3 |
| MCP Specification 2026-07-28, Base Protocol, General fields (modelcontextprotocol.io/specification/2026-07-28/basic) | Open Standard | Section 6 |
| Palo Alto Networks Unit 42, MCP attack vectors research | Vendor Report | Section 3.1 |
| NIST SP 800-53 Rev. 5 (AU-9, AU-10, AU-5) | Standards Body | Section 6 |
| EU AI Act Article 12 (Regulation (EU) 2024/1689); AI Omnibus, in force 27 July 2026 (European Commission) | Regulatory Text | Section 6 |
| Anthropic, "Reasoning Models Don't Always Say What They Think" (2025); Anthropic Petri (2025) | Vendor Research | Section 5 |
| Cemri et al., MAST, arXiv:2503.13657 (2025) | Peer-Reviewed Research | Section 4 (orchestration guardrails) |
| IBM Cost of a Data Breach Report 2025 | Analyst Report | Section 6 |
| Obsidian Security, 2025 AI Agent Security Report | Vendor Report | Section 2 |
| Lucktemberg, "Agentic AI Security Stack" (book, in progress) | Author's Prior Publication | Primary structural source for this entire document |

## Appendix B: Acronym Reference

| Acronym | Expansion |
|---|---|
| AAIF | Agentic AI Foundation |
| ACS | Agent Control Standard (OWASP) |
| AgBOM | Agent Bill of Materials |
| ASI | Agentic Security Initiative (OWASP) |
| ATLAS | Adversarial Threat Landscape for Artificial-Intelligence Systems (MITRE) |
| BSL | Business Source License |
| CNCF | Cloud Native Computing Foundation |
| CSA | Cloud Security Alliance |
| CTF | Capture the Flag |
| CVE | Common Vulnerabilities and Exposures |
| CVSS | Common Vulnerability Scoring System |
| EPC | Enclave Page Cache |
| FAA | Federal Aviation Administration |
| GDPR | General Data Protection Regulation |
| HITL | Human-in-the-Loop |
| HSM | Hardware Security Module |
| IAM | Identity and Access Management |
| IRSA | IAM Roles for Service Accounts (AWS) |
| MAST | Multi-Agent System Failure Taxonomy |
| MCP | Model Context Protocol |
| OIDC | OpenID Connect |
| OWASP | Open Worldwide Application Security Project |
| PII | Personally Identifiable Information |
| PKCE | Proof Key for Code Exchange |
| RCE | Remote Code Execution |
| SBOM | Software Bill of Materials |
| SEV-SNP | Secure Encrypted Virtualization - Secure Nested Paging (AMD) |
| SGX | Software Guard Extensions (Intel) |
| SIEM | Security Information and Event Management |
| SPIFFE | Secure Production Identity Framework for Everyone |
| SVID | SPIFFE Verifiable Identity Document |
| TDX | Trust Domain Extensions (Intel) |
| UCAN | User Controlled Authorization Networks |
| WIF | Workload Identity Federation (GCP) |
| YARA | Yet Another Recursive Acronym (malware pattern matching tool) |
