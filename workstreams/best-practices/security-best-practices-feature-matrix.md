# Agentic AI Security Best Practices — Feature Matrix

Derived from the _Agentic AI Security Best Practices Guide (Draft v0.1)_ and supplemented by the _Google ADK Safety and Security for AI Agents_ guidance. Each best practice is listed alongside the features required to support it.

**Sources**

- \[SPAA-BP-Guide\] Lucktemberg et al., _Agentic AI Security Best Practices Guide_, AAIF Security & Privacy WG, Draft v0.1
- \[ADK-Safety\] Google, _Safety and Security for AI Agents_, Agent Development Kit documentation, https://adk.dev/safety/

---

## 1. Secrets Management

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 1.1.1 | Eliminate static, long-lived credentials from agent environments | Create short-lived workload identity (AWS IRSA, GCP Workload Identity, Azure Managed Identity) | Technology | [SPAA-BP-Guide] |
| 1.1.2 | Eliminate static, long-lived credentials from agent environments | Automated credential rotation | Technology | [SPAA-BP-Guide] |
| 1.2.1 | Issue credentials on-demand with narrow scope (per request) and short TTL | Use a dynamic secrets engine (HashiCorp Vault or equivalent) for per-request credential scoping | Technology | [SPAA-BP-Guide] |
| 1.2.2 | Issue credentials on-demand with narrow scope and short TTL | Auto-expiry and cleanup | Technology | [SPAA-BP-Guide] |
| 1.3.1 | Inject credentials at the network layer for legacy systems | Sidecar/proxy credential injection outside of agent | Technology | [SPAA-BP-Guide] |
| 1.4.1 | Isolate secrets in hardware-protected enclaves for highest-sensitivity workloads | Confidential computing (Intel SGX/TDX, AMD SEV-SNP) | Technology | [SPAA-BP-Guide] |
| 1.4.2 | Isolate secrets in hardware-protected enclaves for highest-sensitivity workloads | Enclave-attested key release | Technology | [SPAA-BP-Guide] |
| 1.5.1 | Audit every deployment for long-lived secrets in environment variables or image layers | Secrets-scanning CI/CD integration | Technology | [SPAA-BP-Guide] |
| 1.5.2 | Audit every deployment for long-lived secrets in environment variables or image layers | Environment variable auditing | Process | [SPAA-BP-Guide] |
| 1.5.3 | Audit every deployment for long-lived secrets in environment variables or image layers | Container image layer scanning | Technology | [SPAA-BP-Guide] |

---

## 2. Secure Tool Invocation — MCP Protocol Security

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 2.1.1 | Evaluate every MCP server before connection | Source repository existence check | Process | [SPAA-BP-Guide] |
| 2.1.2 | Evaluate every MCP server before connection | Recent activity verification (≥90-day threshold) | Process | [SPAA-BP-Guide] |
| 2.1.3 | Evaluate every MCP server before connection | Cross-reference against Vulnerable MCP Project tracker | Process | [SPAA-BP-Guide] |
| 2.1.4 | Evaluate every MCP server before connection | Static scanning (Cisco MCP Scanner) | Technology | [SPAA-BP-Guide] |
| 2.1.5 | Evaluate every MCP server before connection | Runtime scanning (Invariant mcp-scan) | Technology | [SPAA-BP-Guide] |
| 2.2.1 | Require authenticated, encrypted transport for all HTTP MCP connections | OAuth 2.1 with PKCE | Technology | [SPAA-BP-Guide] |
| 2.2.2 | Require authenticated, encrypted transport for all HTTP MCP connections | Token audience binding (RFC 8707) | Technology | [SPAA-BP-Guide] |
| 2.2.3 | Require authenticated, encrypted transport for all HTTP MCP connections | TLS enforcement | Technology | [SPAA-BP-Guide] |
| 2.3.1 | Treat stdio MCP servers as untrusted local binaries | Sandbox isolation for stdio-transport servers | Technology | [SPAA-BP-Guide] |
| 2.3.2 | Treat stdio MCP servers as untrusted local binaries | No production deployment without explicit review | Process | [SPAA-BP-Guide] |
| 2.4.1 | (Multiple MCP servers) Route all agent-to-tool traffic through a single enforcement gateway | MCP gateway (Cloudflare MCP Portals or Linux Foundation `agentgateway`) | Technology | [SPAA-BP-Guide] |
| 2.4.2 | (Multiple MCP servers) Route all agent-to-tool traffic through a single enforcement gateway | Per-tool permission policy | Process,Technology | [SPAA-BP-Guide] |
| 2.4.3 | (Multiple MCP servers) Route all agent-to-tool traffic through a single enforcement gateway | Full request/response payload capture | Technology | [SPAA-BP-Guide] |
| 2.5.1 | Enforce runtime invariants against tool poisoning and rug pulls | Tool description hash comparison at every session start | Technology | [SPAA-BP-Guide] |
| 2.5.2 | Enforce runtime invariants against tool poisoning and rug pulls | Out-of-scope data-category blocking | Technology | [SPAA-BP-Guide] |
| 2.5.3 | Enforce runtime invariants against tool poisoning and rug pulls | Server allow-registry enforcement | Process | [SPAA-BP-Guide] |

---

## 3. Secure Tool Invocation — Supply Chain & Skill Verification

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 3.1.1 | Automatically pre-scan all skills before use (Tier 1) | Static pattern matching using automated scanner (Cisco Skill Scanner or Snyk Agent Scan) for static pattern matching | Technology | [SPAA-BP-Guide] |
| 3.1.2 | Automatically pre-scan all skills before use (Tier 1) | Behavioral dataflow analysis using utomated scanner (Cisco Skill Scanner or Snyk Agent Scan) | Technology | [SPAA-BP-Guide] |
| 3.1.3 | Automatically pre-scan all skills before use (Tier 1) | Block on Critical/High findings from automated scanner | Process | [SPAA-BP-Guide] |
| 3.2.1 | Manually review skills requesting elevated permissions (Tier 2) | `allowed-tools` field validation against stated purpose | Process | [SPAA-BP-Guide] |
| 3.2.2 | Manually review skills requesting elevated permissions (Tier 2) | Scanning for undeclared domain calls, `eval()`, and Base64-obscured code | Process | [SPAA-BP-Guide] |
| 3.2.3 | Manually review skills requesting elevated permissions (Tier 2) | Sensitive path access detection (`~/.ssh`, `~/.aws`) | Process | [SPAA-BP-Guide] |
| 3.2.4 | Manually review skills requesting elevated permissions (Tier 2) | Author attribution verification | Process | [SPAA-BP-Guide] |
| 3.3.1 | Maintain an organizational trust registry for all production skills (Tier 3) | Version and hash pinning | Technology | [SPAA-BP-Guide] |
| 3.3.2 | Maintain an organizational trust registry for all production skills (Tier 3) | Named accountable owner distinct from requester | People | [SPAA-BP-Guide] |
| 3.3.3 | Maintain an organizational trust registry for all production skills (Tier 3) | Re-verification gate on any update | Process | [SPAA-BP-Guide] |
| 3.4.1 | Identify blast radius of environment before running verification | Sandboxed code-execution VMs (no network) or allowlist network access only.  | Process,Technology | [SPAA-BP-Guide] |
| 3.4.2 | Identify blast radius of environment before running verification | Filesystem access controls | Technology | [SPAA-BP-Guide] |

---

## 4. Guardrails

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 4.1.1 | Classify every operation into an authorization tier at design time | Orchestration-layer tier classifier | Technology | [SPAA-BP-Guide] |
| 4.1.2 | Classify every operation into an authorization tier at design time | Classification enforced by architecture (not self-reported by agent) | Technology | [SPAA-BP-Guide] |
| 4.1.3 | Classify every operation into an authorization tier at design time | Operation-type-to-tier mapping table | Process | [SPAA-BP-Guide] |
| 4.2.1 | Tier 1 — Autonomous with audit sampling | Statistical post-hoc audit (10% initial, 2–3% after 90-day baseline) | Process | [SPAA-BP-Guide] |
| 4.2.2 | Tier 1 — Autonomous with audit sampling | Operation logging | Technology | [SPAA-BP-Guide] |
| 4.3.1 | Tier 2 — Asynchronous notification with approval window | Async approval queue | Technology | [SPAA-BP-Guide] |
| 4.3.2 | Tier 2 — Asynchronous notification with approval window | 4-hour timeout with auto-escalation | Technology | [SPAA-BP-Guide] |
| 4.3.3 | Tier 2 — Asynchronous notification with approval window | Agent ability to continue unrelated work during wait | Technology | [SPAA-BP-Guide] |
| 4.4.1 | Tier 3 — Synchronous pre-approval with full context | Agent halt mechanism for Human in the Loop approval | Technology | [SPAA-BP-Guide] |
| 4.4.2 | Tier 3 — Synchronous pre-approval with full context | Interface surfacing reasoning trace, impact radius, and validation checklist as data to review for approval | Technology | [SPAA-BP-Guide] |
| 4.4.3 | Tier 3 — Synchronous pre-approval with full context | Context-complete approval interface | Technology | [SPAA-BP-Guide] |
| 4.4.4 | Tier 3 — Synchronous pre-approval with full context | Approval affordance unavailable until required context is traversed | Technology | [SPAA-BP-Guide] |
| 4.5.1 | Tier 4 — Dual authorization for irreversible/high-risk operations | Two independent reviewer sessions | Technology | [SPAA-BP-Guide] |
| 4.5.2 | Tier 4 — Dual authorization for irreversible/high-risk operations | Out-of-band verification | Technology | [SPAA-BP-Guide] |
| 4.5.3 | Tier 4 — Dual authorization for irreversible/high-risk operations | Automatic trigger for any non-allowlisted external network request | Technology | [SPAA-BP-Guide] |
| 4.5.4 | Tier 4 — Dual authorization for irreversible/high-risk operations | Database-constraint enforcement (not UI gate) | Technology | [SPAA-BP-Guide] |
| 4.6.1 | Prevent approval fatigue and rubber-stamping | Approval rate time-series tracking | Technology | [SPAA-BP-Guide] |
| 4.6.2 | Prevent approval fatigue and rubber-stamping | Fatigue flagging when approval rate climbs within a shift | Technology | [SPAA-BP-Guide] |
| 4.6.3 | Prevent approval fatigue and rubber-stamping | Synthetic anomaly injection at randomized intervals | Process | [SPAA-BP-Guide] |
| 4.7.1 | Enforce containment at every delegation boundary | Trust-boundary inspection at each agent-to-agent handoff | Technology | [SPAA-BP-Guide] |
| 4.7.2 | Enforce containment at every delegation boundary | Scope/permission/endpoint validation | Technology | [SPAA-BP-Guide] |
| 4.7.3 | Enforce containment at every delegation boundary | Circuit breakers on repeated inspection failures | Technology | [SPAA-BP-Guide] |
| 4.7.4 | Enforce containment at every delegation boundary | Bulkheads isolating compute, memory, and API quota per domain | Technology | [SPAA-BP-Guide] |
| 4.8.1 | Maintain an out-of-runtime kill switch with graduated degradation | Kill switch state stored outside the agent runtime | Technology | [SPAA-BP-Guide] |
| 4.8.2 | Maintain an out-of-runtime kill switch with graduated degradation | Three granularities (individual, group, global) | Process | [SPAA-BP-Guide] |
| 4.8.3 | Maintain an out-of-runtime kill switch with graduated degradation | Graduated degradation path (reduce autonomy → restrict tool access → require checkpoint approval → disable) | Process | [SPAA-BP-Guide] |
| 4.8.4 | Maintain an out-of-runtime kill switch with graduated degradation | Staging drills required before go-live | People | [SPAA-BP-Guide] |
| 4.9.1 | Design tools defensively using developer-set context, not model input | Tool context policy enforcement (e.g., allowlisted tables, select-only query policy) | Process | [ADK-Safety] |
| 4.9.2 | Design tools defensively using developer-set context, not model input | Deterministic developer-set `ToolContext` / `InvocationContext` values used for policy validation | Technology | [ADK-Safety] |
| 4.9.3 | Design tools defensively using developer-set context, not model input | Tool-level action scope limited to declared capabilities (no undeclared write, delete, or external calls) | Technology | [ADK-Safety] |
| 4.10.1 | Apply callbacks and plugins as pre/post-execution validation for model and tool I/O | `before_tool_callback` / `BeforeToolCallback` intercepting all tool invocations before execution | Technology | [ADK-Safety] |
| 4.10.2 | Apply callbacks and plugins as pre/post-execution validation for model and tool I/O | Agent state and session context accessible in callback for parameter validation | Technology | [ADK-Safety] |
| 4.10.3 | Apply callbacks and plugins as pre/post-execution validation for model and tool I/O | Security plugins applied at the runner level for consistent cross-agent policy enforcement | Technology | [ADK-Safety] |
| 4.10.4 | Apply callbacks and plugins as pre/post-execution validation for model and tool I/O | PII redaction plugin applied as a before-tool callback before data is sent to external services | Technology | [ADK-Safety] |
| 4.11.1 | Use a lightweight LLM as a safety judge to screen inputs and outputs | Gemini Flash Lite (or equivalent low-cost model) configured as a safety-judge callback | Technology | [ADK-Safety] |
| 4.11.2 | Use a lightweight LLM as a safety judge to screen inputs and outputs | Prompt injection and jailbreak detection via judge model | Technology | [ADK-Safety] |
| 4.11.3 | Use a lightweight LLM as a safety judge to screen inputs and outputs | Content safety and brand safety evaluation on user input, tool I/O, and model output | Technology | [ADK-Safety] |
| 4.11.4 | Use a lightweight LLM as a safety judge to screen inputs and outputs | Predetermined safe fallback response returned when judge model flags input as unsafe | Process | [ADK-Safety] |
| 4.12.1 | Apply model-level content safety filters on all model output | Non-configurable safety filters blocking CSAM and PII by default | Technology | [ADK-Safety] |
| 4.12.2 | Apply model-level content safety filters on all model output | Configurable content filters with per-category thresholds (hate speech, harassment, sexually explicit, dangerous content) using probability and severity scores | Technology | [ADK-Safety] |
| 4.13.1 | Define safety and brand guidelines in system instructions | System instruction defining prohibited and sensitive topics | Process | [ADK-Safety] |
| 4.13.2 | Define safety and brand guidelines in system instructions | System instruction defining brand voice, tone, values, and target audience | Process | [ADK-Safety] |
| 4.13.3 | Define safety and brand guidelines in system instructions | System instruction specifying required disclaimer language | Process | [ADK-Safety] |

---

## 5. Eval Frameworks

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 5.1.1 | Train engineers against real agentic vulnerability classes before deployment | Hands-on training with adversarial CTF platforms (OWASP FinBot / genai.owasp.org) | People | [SPAA-BP-Guide] |
| 5.2.1 | Use scanner and checklist gates from Sections 3 and 4 as hard blocking criteria | MCP scanner integration as a gating step | Technology | [SPAA-BP-Guide] |
| 5.2.2 | Use scanner and checklist gates from Sections 3 and 4 as hard blocking criteria | Skill verification tiers enforced as prerequisites | Process | [SPAA-BP-Guide] |
| 5.2.3 | Use scanner and checklist gates from Sections 3 and 4 as hard blocking criteria | Critical/High findings block production deployment | Process | [SPAA-BP-Guide] |
| 5.3.1 | Run a structured readiness checklist before any guardrail system goes live | Tier-definition documentation review | Process | [SPAA-BP-Guide] |
| 5.3.2 | Run a structured readiness checklist before any guardrail system goes live | Approval-interface context completeness test by unfamiliar reviewer | People | [SPAA-BP-Guide] |
| 5.3.3 | Run a structured readiness checklist before any guardrail system goes live | Kill switch tested | Process | [SPAA-BP-Guide] |
| 5.3.4 | Run a structured readiness checklist before any guardrail system goes live | Classifier model version record with recalibration procedure | Process | [SPAA-BP-Guide] |
| 5.4.1 | Use a graduated rollout structure for eval | Read-only + full audit phase (weeks 1–4) | Process | [SPAA-BP-Guide] |
| 5.4.2 | Use a graduated rollout structure for eval | Limited autonomy + high-density sampling (weeks 5–12) | Process | [SPAA-BP-Guide] |
| 5.4.3 | Use a graduated rollout structure for eval | Full tier architecture (months 4–6) | Process | [SPAA-BP-Guide] |
| 5.4.4 | Use a graduated rollout structure for eval | Steady state (month 7+) | Process | [SPAA-BP-Guide] |
| 5.5.1 | Establish statistical baselines for continuous behavioral evaluation | Baseline tool-call frequency per agent identity | Technology | [SPAA-BP-Guide] |
| 5.5.2 | Establish statistical baselines for continuous behavioral evaluation | Parameter entropy analysis of tool invocations | Technology | [SPAA-BP-Guide] |
| 5.5.3 | Establish statistical baselines for continuous behavioral evaluation | Inter-agent message volume tracking | Technology | [SPAA-BP-Guide] |
| 5.5.4 | Establish statistical baselines for continuous behavioral evaluation | Token-count ratio monitoring | Technology | [SPAA-BP-Guide] |
| 5.5.5 | Establish statistical baselines for continuous behavioral evaluation | Memory-write frequency baselining | Technology | [SPAA-BP-Guide] |
| 5.5.6 | Establish statistical baselines for continuous behavioral evaluation | Deviation-based alerting (not fixed thresholds) | Technology | [SPAA-BP-Guide] |
| 5.6.1 | Treat reasoning traces as corroborating evidence only | Explicit `unverified` tagging on all reasoning traces | Process | [SPAA-BP-Guide] |
| 5.6.2 | Treat reasoning traces as corroborating evidence only | Primary detection signal derived from behavioral/statistical baselines, not trace content | Process | [SPAA-BP-Guide] |

---

## 6. Post-Incident Forensics

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 6.1.1 | Capture the seven required event categories | Action events with credential field | Technology | [SPAA-BP-Guide] |
| 6.1.2 | Capture the seven required event categories | Reasoning traces tagged `unverified` | Technology | [SPAA-BP-Guide] |
| 6.1.3 | Capture the seven required event categories | Approval/HITL events with artifact reference | Technology | [SPAA-BP-Guide] |
| 6.1.4 | Capture the seven required event categories | Memory/context write events with provenance metadata | Technology | [SPAA-BP-Guide] |
| 6.1.5 | Capture the seven required event categories | Credential lifecycle events | Technology | [SPAA-BP-Guide] |
| 6.1.6 | Capture the seven required event categories | Model call events mapped to OpenTelemetry GenAI conventions in a stable internal envelope | Technology | [SPAA-BP-Guide] |
| 6.1.7 | Capture the seven required event categories | Delegation chain events with W3C Trace Context (128-bit `trace-id`, per-span `parent-id`) | Technology | [SPAA-BP-Guide] |
| 6.2.1 | Establish per-agent identity before any instrumentation | Per-agent identity (not shared service accounts) | Process | [SPAA-BP-Guide] |
| 6.2.2 | Establish per-agent identity before any instrumentation | Identity propagated through all log events and delegation chains | Technology | [SPAA-BP-Guide] |
| 6.3.1 | Enforce cryptographic log integrity | Per-entry cryptographic signing at write time | Technology | [SPAA-BP-Guide] |
| 6.3.2 | Enforce cryptographic log integrity | Merkle-tree append structure (Tessera/Trillian) | Technology | [SPAA-BP-Guide] |
| 6.3.3 | Enforce cryptographic log integrity | Published baseline root hash | Process | [SPAA-BP-Guide] |
| 6.3.4 | Enforce cryptographic log integrity | Write-only forwarding to a destination where agent credentials carry no delete permission | Technology | [SPAA-BP-Guide] |
| 6.4.1 | Separate compliance and operational log streams | Compliance stream: 100% capture, no sampling, cryptographic integrity, retention-locked storage | Technology | [SPAA-BP-Guide] |
| 6.4.2 | Separate compliance and operational log streams | Compliance stream event types: action, approval, delegation, model-call, and decision events | Process | [SPAA-BP-Guide] |
| 6.4.3 | Separate compliance and operational log streams | Operational stream: sampled, short retention, basic checksums | Technology | [SPAA-BP-Guide] |
| 6.4.4 | Separate compliance and operational log streams | Operational stream event types: reasoning traces, diagnostics, and metrics | Process | [SPAA-BP-Guide] |
| 6.5.1 | Maintain a forensics-grade kill-switch runbook | Explicit trigger conditions | Process | [SPAA-BP-Guide] |
| 6.5.2 | Maintain a forensics-grade kill-switch runbook | Defined authority chain (halt authority vs. restart authority) | People | [SPAA-BP-Guide] |
| 6.5.3 | Maintain a forensics-grade kill-switch runbook | Ordered restart checklist (vector identified → credential rotation → log review → owner sign-off) | Process | [SPAA-BP-Guide] |
| 6.5.4 | Maintain a forensics-grade kill-switch runbook | Forensic state snapshot to immutable storage before any state is cleared | Technology | [SPAA-BP-Guide] |

---

## 7. Identity and Authorization

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 7.1.1 | Perform a threat and risk assessment before implementing any security controls | Risk assessment scoped to agent capabilities, domain, and deployment context | People | [ADK-Safety] |
| 7.1.2 | Perform a threat and risk assessment before implementing any security controls | Risk category coverage: misalignment and goal corruption, harmful content generation, brand safety, unsafe actions, data exfiltration | Process | [ADK-Safety] |
| 7.2.1 | Use agent-auth (service account identity) with least-privilege IAM for shared-access scenarios | Agent service account explicitly authorized in external system IAM policies | Technology | [ADK-Safety] |
| 7.2.2 | Use agent-auth (service account identity) with least-privilege IAM for shared-access scenarios | Read-only or narrowly scoped IAM permissions preventing unintended write/delete actions | Technology | [ADK-Safety] |
| 7.2.3 | Use agent-auth (service account identity) with least-privilege IAM for shared-access scenarios | Action attribution logging to user when all agent actions share an agent identity | Technology | [ADK-Safety] |
| 7.3.1 | Use user-auth (OAuth delegation) when different users require different access levels | OAuth token acquired from frontend and forwarded by agent to external system | Technology | [ADK-Safety] |
| 7.3.2 | Use user-auth (OAuth delegation) when different users require different access levels | Authorization decision made by external system based on controlling user's identity | Technology | [ADK-Safety] |
| 7.3.3 | Use user-auth (OAuth delegation) when different users require different access levels | OAuth scope narrowing via in-tool guardrails to limit delegation to minimum required access | Technology | [ADK-Safety] |

---

## 8. Sandboxed Code Execution

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 8.1.1 | Sandbox all model-generated code execution to prevent host environment compromise | Hermetic execution environment with no outbound network connections or API calls | Technology | [ADK-Safety] |
| 8.1.2 | Sandbox all model-generated code execution to prevent host environment compromise | Full data cleanup between executions to prevent cross-user state exfiltration | Technology | [ADK-Safety] |
| 8.1.3 | Sandbox all model-generated code execution to prevent host environment compromise | Server-side sandboxed code execution (e.g., Vertex Gemini Enterprise API `tool_execution` tool) | Technology | [ADK-Safety] |
| 8.1.4 | Sandbox all model-generated code execution to prevent host environment compromise | Code Executor tool integration with Vertex Code Interpreter Extension for data analysis workloads | Technology | [ADK-Safety] |

---

## 9. Network Controls and Perimeter Security

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 9.1.1 | Confine all agent API calls within a VPC Service Controls perimeter to prevent data exfiltration | VPC-SC perimeter enclosing all agent-accessible resources | Technology | [ADK-Safety] |
| 9.1.2 | Confine all agent API calls within a VPC Service Controls perimeter to prevent data exfiltration | Perimeter policy blocking API calls to resources outside the defined boundary | Technology | [ADK-Safety] |
| 9.2.1 | Combine network perimeter controls with tool-use guardrails for fine-grained action control | Tool-level guardrails applied in addition to perimeter (perimeter provides coarse controls only) | Process | [ADK-Safety] |

---

## 10. Output Handling and UI Security

| ID | Best Practice | Feature Required | Type | Citation / Notes |
|---|---|---|---|---|
| 10.1.1 | Escape all model-generated content before rendering in browser UIs | HTML and JavaScript escaping of all model output before DOM insertion | Technology | [ADK-Safety] |
| 10.1.2 | Escape all model-generated content before rendering in browser UIs | Prevention of model-generated `<img>`, `<script>`, and URL injection that could trigger exfiltration | Technology | [ADK-Safety] |
| 10.1.3 | Escape all model-generated content before rendering in browser UIs | Content Security Policy (CSP) headers blocking execution of injected scripts | Technology | [ADK-Safety] |
