# Attested Isolated Runtime

> **Status:** Draft. Contributed to the design-patterns workstream for working group review.
> A design pattern for the "Privacy-preserving execution" topic area.

**Also known as:** TEE-isolated agent runtime, confidential agent execution, attested enclave gateway

## About this draft

This is the first pattern submitted under the design-patterns workstream topic area
"Privacy-preserving execution (ZK proofs, TEEs, encrypted vector DBs)". It covers the
trusted-execution and hardware-attestation portion of that topic. Zero-knowledge proofs and
encrypted vector databases deserve their own patterns and are left open.

The draft is deliberately opinionated in three places, flagged inline as **Open question**,
because those are the points where the workstream should push back before this becomes final.

Contributions are welcome from anyone implementing the attestation stacks referenced at the
end of this document. The pattern is written against five independent hardware attestation
stacks and requires none of them, and review from people who operate those stacks in
production would improve it considerably. See the working group charter for how to
participate.

## Context

An agent processes data whose exposure is constrained by regulation, contract, or
classification. It runs on infrastructure the data owner does not operate: a public cloud
region, a partner tenant, a managed inference endpoint, or a customer environment where the
agent vendor is the party being audited.

Four roles matter here, and they belong to different organizations.

| Role | Interest |
|------|----------|
| Data owner | Inputs are not exposed during processing |
| Agent operator | Runs the workload and wants it to be adoptable |
| Infrastructure operator | Controls the host, the hypervisor, and the orchestrator |
| Relying party | A tool, a peer agent, an auditor, or a regulator making a decision about the agent without the ability to inspect it |

This pattern applies when the infrastructure operator sits inside the threat model. Where the
host is trusted, the containment and authorization patterns elsewhere in this catalog cover
the ground at lower cost.

## Problem

Software-only controls place the enforcement mechanism in the same trust domain as the thing
being constrained. When a policy engine, an audit logger, and the agent they govern all run
under one operating system at one operator's privilege level, four properties the relying
party depends on become unverifiable.

**The policy that executed is unprovable.** A bundle hash gets checked by a process running on
the host the operator controls, so the check carries the same privilege as the artifact it
checks. A swapped bundle is undetectable from inside that domain.

**A decision can be altered in memory.** A deserialization bug or a compromised transitive
dependency in the evaluator executes in the same address space as the evaluation. The verdict
changes and the log records the changed verdict as legitimate.

**The audit trail shares a fate with the workload.** Any party holding the signing key can
construct a consistent history after the fact. A relying party has no way to distinguish a
recorded history from a reconstructed one, which makes the trail worth exactly as much as its
custodian's word.

**Data in use is readable.** Encryption at rest and in transit leave a plaintext window during
execution. Prompts, retrieved documents, tool responses, and model weights sit in
host-accessible memory, reachable by a privileged operator, a co-tenant isolation escape, or a
crash dump.

These are structural properties of the deployment. Diligence and additional controls inside
that domain leave them in place, because the enforcement, the evidence, and the adversary all
occupy one privilege level, and the set of parties able to subvert them stays the same.

## Forces

- Relying parties need to verify claims about an agent without an audit relationship with its
  operator, and no in-band mechanism gives them that today.
- Confidential computing hardware is unavailable in many regions, instance families, and
  on-premises estates.
- Attestation costs latency at session setup and carries ongoing operational burden.
- Enclave memory is finite, which bounds what can live inside the boundary.
- Every component moved inside the boundary expands both what the isolation protects and the
  attack surface the isolation exists to defend.

## Solution

Move the enforcement point and its evidence production into a hardware-isolated execution
environment that the host operator can neither read nor modify, then require the relying party
to verify that environment before releasing anything of value.

Four elements make up the pattern. Deployments that implement three of the four are common and
give up most of the benefit, so the elements are listed with the failure that follows from
skipping each one.

### 1. Isolate the enforcement point and leave the agent outside

Run the policy decision point, the classification and redaction logic, and the evidence signer
inside a Trusted Execution Environment. AMD SEV-SNP, Intel TDX, or ARM CCA serve CPU
workloads. GPU confidential computing applies where model weights need protection in device
memory.

The agent stays outside. Agent code executes attacker-influenced input as its normal mode of
operation, which makes it the component most likely to be subverted, and enclosing it grows
the trusted computing base by precisely that component. What belongs inside the boundary is the
small, auditable, slow-changing code whose integrity the relying party depends on. The agent,
its inference path where weights need no protection, and the tool implementations all stay
outside.

Draw the boundary so that a fully compromised agent still cannot alter policy, forge evidence,
or read data the policy denied it.

> **Open question.** This placement is the pattern's strongest claim. A workstream member who
> believes the agent belongs inside the boundary should say so, because the rest of the pattern
> follows from this line.

### 2. Generate the signing key inside the boundary and bind evidence to it

The key that signs evidence gets generated inside the isolated environment, never leaves it,
and has its public part included in the attested measurement so a verifier can confirm the key
originated there.

Skipping this element is the most common implementation error, and it quietly removes most of
the value. Attestation evidence with no binding to the key signing the requests describes a
machine and can be replayed by any party holding a copy. RFC 8747 defines the
proof-of-possession confirmation claim for this purpose and RFC 9711 carries it in an
attestation token.

### 3. Seal policy to the measurement and release data on appraisal

Bind the policy bundle digest into the attested measurement so that a relying party checking
the measurement simultaneously learns which rules were in force. Then order the operations so
that the relying party, or a key release service acting for the data owner, verifies the
appraisal before releasing credentials, decryption keys, or scopes.

Gating release on the appraisal is what makes attestation a control. Evidence emitted after the
work completes supports recordkeeping and leaves the outcome of the work unchanged.

### 4. Emit verifiable evidence per unit of work and have a separate party appraise it

Each session or action produces a signed record covering what executed, under which policy
digest and enforcement mode, against what data class, and which tools were invoked. A verifier
independent of the operator appraises that evidence against reference values and revocation
state, then issues a signed result the relying party consumes. Anchoring records in an
append-only transparency log lets a third party confirm a record existed and was not withheld.

Separating the verifier from the relying party has a practical payoff: tools avoid implementing
platform-specific quote parsing, and vendor verification logic lives in one place.

## Structure

```
  Untrusted host                      Isolated environment (attested)
  +------------------------+          +----------------------------------+
  | Agent runtime          |          | Policy decision point            |
  |  model inference       |          |  sealed policy bundle digest     |
  |  planner, memory       |-- call --| Classification and redaction     |
  |  tool clients          |<-verdict-| Evidence signer                  |
  +------------------------+          |  key generated in-boundary       |
             |                        +---------------+------------------+
             |                          measurement   |  signed evidence
             v                          + bound key    v
  +------------------------+          +----------------------------------+
  | Tools, data sources    |<- keys --| Verifier (independent party)     |
  | (relying parties)      | released |  reference values, revocation    |
  +------------------------+ on pass  |  issues signed appraisal         |
                                      +---------------+------------------+
                                                      v
                                      +----------------------------------+
                                      | Transparency log (optional)      |
                                      +----------------------------------+
```

The agent sits on the untrusted side of the boundary. That placement is the pattern.

## Implementation notes

**Put the boundary at the interception point.** MCP deployments have a natural seam at the
tool-call boundary: intercept, evaluate, redact, and sign inside the boundary, and leave the
client and the tool implementations outside it. Agent-to-agent paths have their seam at the
delegation issuance point.

**Extend the measurement chain past the platform.** Firmware, kernel, and image measurements
tell a verifier which container executed. They say nothing about the system prompt, the tool
schema set, or the policy bundle, and those artifacts determine agent behavior. Include the
digests of agent-defining artifacts in the measured set so the evidence answers a question a
relying party actually asked.

> **Open question.** Which artifacts belong in the measured set. System prompt, policy bundle,
> tool schemas, and model weights digest are tractable. Retrieved context and memory state are
> dynamic and possibly unbounded, and the workstream should decide whether they are in scope
> for this pattern or belong with secure memory lifecycle management.

**Define a re-attestation interval.** Evidence produced at session start describes the process
at session start. Agent sessions run long. Either re-attest on an interval or bind evidence per
action, and record the choice in policy so operators can reason about it.

**Fail closed and price the cost.** An unreachable verifier, stale revocation data, or an
unrecognized measurement should deny. This makes agent availability depend on verifier
availability, which is a real tradeoff that deserves a deliberate decision ahead of the first
incident.

**Plan for measurement churn from the start.** Firmware updates, kernel patches, base image
bumps, and policy changes all change measurements. Reference value distribution needs an owner,
and in most organizations today it has none.

**Specify a software-only mode.** A signed-but-unattested mode producing structurally identical
evidence lets teams develop, test, and run conformance suites with no confidential computing
hardware, and lets relying-party policy distinguish the two assurance levels explicitly.
Adoption stalls at hardware procurement without it.

> **Open question.** Whether this catalog wants a shared assurance vocabulary that other
> patterns and other working groups can reference, covering signed, attested, and
> transparency-anchored levels. The Identity and Trust WG is looking at the same question from
> the identity side, and duplicating it in two places would be worse than either group owning
> it.

## Trade-offs

### What the pattern gains

- The host operator moves from trusted to untrusted, which is what makes cross-organization
  claims about an agent checkable.
- Policy enforcement and its evidence stop sharing a fate with the workload they govern.
- Data in use gains protection, closing the plaintext execution window.
- A relying party decides on evidence and needs no audit relationship with the operator.

### What the pattern costs

- Attestation and key release add latency at session setup, and per-action attestation adds it
  per action.
- Hardware availability bounds where the pattern can be deployed at all.
- Enclave memory limits bound what fits inside, which bites hardest where weights need
  protection.
- Operational burden is ongoing and routinely underestimated: reference value management,
  revocation freshness, TCB version floors, and firmware upgrade coordination.
- Verifier availability becomes a dependency in the request path. Caching appraisals trades
  freshness for availability.
- Trust moves to a different set of parties. Silicon vendors, reference value publishers,
  transparency log operators, and verifiers all become trusted. The pattern improves on
  trusting a host operator and still requires trust.

### What the pattern does not do

- It leaves misbehavior possible. An agent under prompt injection or goal drift produces
  entirely valid evidence of having done the wrong thing. The pattern makes what executed
  checkable and says nothing about whether it was correct.
- It offers no defense against TEE side channels, covering cache, timing, speculative
  execution, and power analysis.
- It covers no action that stays inside a deployed binary. Logic that never crosses an
  instrumented boundary is bound by measurement and build provenance alone.
- It addresses neither availability nor denial of service.
- It leaves the human in the loop exposed to interface-layer manipulation.

## Anti-patterns

**Attestation theater.** Attestation reports get produced and nothing consumes them. No
verifier sits in the path, no relying-party policy keys off the appraisal, and no data release
depends on it. The report answers an audit question and changes no outcome. Test for this by
asking what breaks when attestation returns a failure. An answer of "nothing" identifies
recordkeeping.

**Unbound evidence.** Attestation reports get published while requests are signed with a key
that lives in the host filesystem. The evidence describes a machine, replays freely, and proves
nothing about the requester.

**Attest once, trust forever.** Verification happens at connection establishment and the result
is treated as valid for the session lifetime. Agent sessions run long and a measurement
describes a moment.

**Enclosing the agent.** The whole agent, its planner, its memory, and its tool clients go
inside the boundary on the theory that more inside means more secure. The trusted computing
base now contains the component that ingests attacker-controlled input, and a prompt-injected
agent inside the enclave reaches everything the enclave protects.

**Self-appraisal.** The operator runs the verifier, appraises its own evidence, and presents the
result as third-party verified. This has the security properties of a self-signed audit log.

**Fail-open verification.** An unreachable verifier, an unparseable quote, or stale revocation
data is treated as a pass to keep production moving. The control goes absent under exactly the
conditions that indicate compromise, and nothing surfaces its absence.

**Hardware as the whole answer.** A TEE gets deployed and the agent is declared governed.
Absent sealed policy, bound keys, and gated release, a TEE is an isolated environment running
ungoverned code.

## Related patterns

| Pattern | Relationship |
|---------|--------------|
| Agent containment and runtime intervention | Complementary. Both live outside the trust boundary drawn here |
| Human-in-the-loop authorization | Approvals become evidentiary once the approval record is bound into the attested claim |
| Blast radius containment | Applies on both sides of the boundary |
| Secure memory and memory lifecycle management | Memory state is a candidate for the measured artifact set, per the open question above |
| Agent authorization models | This pattern supplies evidence that an authorization decision can be conditioned on |

The identity, key binding, and delegation-composition side of this subject belongs with the
Identity and Trust WG. A companion draft has been offered there so the two land consistently.

## References

### Standards

- RFC 9334, Remote ATtestation procedureS (RATS) Architecture
- RFC 9711, Entity Attestation Token
- RFC 8747, Proof-of-Possession Key Semantics for CWTs
- IETF SCITT, Supply Chain Integrity, Transparency and Trust
- SLSA build provenance

### Hardware attestation stacks

- AMD SEV-SNP attestation report
- Intel TDX quote and DCAP verification
- ARM Confidential Compute Architecture
- NVIDIA GPU confidential computing attestation
- TPM 2.0 quote

### Implementations, disclosed as the contributor's own work

- cMCP, Confidential MCP Runtime (MIT). Evaluates MCP tool-call policy inside a TEE and emits a
  signed per-session claim, with a software-only mode that needs no hardware. Reference for the
  boundary placement in element 1.
- TRACE, Trust Runtime Attestation and Compliance Evidence (CC BY 4.0). Record format, anchoring
  protocol, and verification rules for hardware-attested agent governance records, with a
  conformance suite.
- Agent Manifest (Apache 2.0). Binds agent-defining artifacts into one attestable record.
  Reference for the measurement-chain extension note.
- Agent Governance Toolkit (MIT, maintained under Microsoft). MCP Security Gateway 1.0 and Agent
  Hypervisor Execution Control 1.0 cover untrusted-side controls that compose with this pattern.

## Contributor and disclosure

Imran Siddique, Opaque Systems.

Opaque Systems sells confidential computing infrastructure and the contributor authored several
of the implementations listed above, which makes this pattern commercially favorable to the
contributor's employer. Three properties of the draft exist to constrain that bias: it is
written against five independent attestation stacks and requires none of them, it specifies a
software-only mode as a legitimate deployment so members without confidential computing
hardware stay in scope, and it enumerates costs and limits at the same length as benefits. The trade-offs and anti-patterns sections are where review pressure will
do the most good.
