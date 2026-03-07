# Taxonomy of Terms and Definitions

> **Status:** Draft
> **Last Modified:** 2026-03-07

## Purpose

This document establishes a shared vocabulary for the Security and Privacy Working Group. A common taxonomy reduces ambiguity in discussions, aligns deliverables across the Agentic AI Foundation, and provides a reference point for external stakeholders.

The taxonomy is intended to be a living document. Once mature, these definitions will be proposed for adoption across all AAIF working groups.

## How to Use This Document

- Terms are listed alphabetically within each category.
- Each entry includes a short definition and, where relevant, notes on scope or usage within this working group.
- When a term was explicitly discussed or debated in a meeting, the relevant meeting date is cited.

## Terms

### Agent Behavior

| Term | Definition | Notes |
|------|-----------|-------|
| Agent derailment | An unintended deviation in an AI agent's behavior that causes it to pursue goals or take actions outside its intended scope, without malicious external cause. | Raised during discussion of non-malicious agent misbehavior ([2026-03-03](../meeting-notes/2026-03-03.md)). Distinct from adversarial attacks. |
| Agent sabotage | Deliberate manipulation of an AI agent's behavior by an external party, causing it to act against its intended purpose. | Discussed alongside derailment as an edge case between security and reliability ([2026-03-03](../meeting-notes/2026-03-03.md)). |
| Blast radius | The scope and extent of damage or data exposure that can result from a compromised, misconfigured, or rogue agent. | Samantha Coyle raised this in the context of protecting data from rogue agents ([2026-03-03](../meeting-notes/2026-03-03.md)). |
| Human in the loop (HITL) | A design pattern in which a human must review, approve, or intervene in an AI agent's actions at defined checkpoints before the agent may proceed. | Identified as a key consideration during the initial brainstorm ([2026-02-17](../meeting-notes/2026-02-17.md)). |
| Multi-agent persuasion | The risk that one AI agent manipulates or unduly influences another agent's decision-making through adversarial or misleading communication. | Brainstormed as a mitigation area ([2026-02-17](../meeting-notes/2026-02-17.md)). |
| Rogue agent | An AI agent that operates outside its authorized boundaries, whether due to compromise, misconfiguration, or emergent behavior. | Used in discussion of blast radius and data protection ([2026-03-03](../meeting-notes/2026-03-03.md)). |

### Data and Privacy

| Term | Definition | Notes |
|------|-----------|-------|
| PII obfuscation | Techniques for masking, redacting, or transforming personally identifiable information so that it cannot be recovered or linked to an individual during agent processing. | Listed as a brainstorm topic ([2026-02-17](../meeting-notes/2026-02-17.md)) and folded into Theme D ([2026-03-03](../meeting-notes/2026-03-03.md)). |
| Privacy-preserving execution | Patterns in which an AI agent can operate on encrypted or protected data without exposing the underlying content, using techniques such as zero-knowledge proofs or trusted execution environments. | Ty described ZK-proof patterns; Tony Douglas cited TEEs and encrypted vector databases ([2026-03-03](../meeting-notes/2026-03-03.md)). |
| Protected data | Information subject to regulatory or contractual protections (e.g., HIPAA, GDPR), which may include health records, financial data, or other categories that AI agents must handle with specific safeguards. | Tom Sheffler raised whether AI agents introduce new categories of protected data ([2026-03-03](../meeting-notes/2026-03-03.md)). |
| Sensitive data | An umbrella term encompassing secrets, PII, proprietary information, and any data whose exposure would cause harm. Preferred over the narrower term "secrets" when the intent is to cover all confidential data categories. | The group debated "secrets" vs. "sensitive data" and converged on "sensitive data" as the broader, less ambiguous term ([2026-03-03](../meeting-notes/2026-03-03.md)). |
| Secrets | Traditional credentials and cryptographic material — such as API keys, tokens, passwords, and environment variables — that grant access to systems or services. | Distinguished from the broader "sensitive data" during terminology discussion. Ofek Dadush raised secrets management; David Deng proposed the narrower scope ([2026-03-03](../meeting-notes/2026-03-03.md)). |

### Identity and Authorization

| Term | Definition | Notes |
|------|-----------|-------|
| Agent identity | A verifiable identifier assigned to an AI agent that distinguishes it from other agents and human users within a system. | Samantha Coyle raised agent-to-agent and agent-to-MCP-server authentication ([2026-02-17](../meeting-notes/2026-02-17.md)). |
| Delegated authorization | A mechanism by which a human or system grants an AI agent a scoped set of permissions to act on its behalf, typically with constraints on what actions the agent may perform. | Discussed alongside capability-based auth and tool invocation restrictions ([2026-02-17](../meeting-notes/2026-02-17.md)). |

### Security Practices

| Term | Definition | Notes |
|------|-----------|-------|
| Hooks and checkpoints | Standardized interception points in an agentic AI platform's execution pipeline where security controls, logging, or policy enforcement can be applied. | Bar Kaduri proposed hooks and checkpointing standards ([2026-02-17](../meeting-notes/2026-02-17.md)). |
| Prompt injection | An attack in which an adversary crafts input that causes an AI agent to override its instructions, bypass safeguards, or execute unintended actions. | Identified as a mitigation area during ideation ([2026-02-17](../meeting-notes/2026-02-17.md)). |
| Red teaming | Structured adversarial testing of AI systems in which testers simulate attacks to identify vulnerabilities, failure modes, and security gaps. | Listed as a brainstorm topic under pen testing and red teaming best practices ([2026-02-17](../meeting-notes/2026-02-17.md)). |

### Infrastructure and Architecture

| Term | Definition | Notes |
|------|-----------|-------|
| Agentic AI | AI systems composed of one or more autonomous agents that can perceive their environment, make decisions, invoke tools, and take actions with limited or no human intervention. | Foundational term for the working group; used throughout all meetings. |
| Trusted execution environment (TEE) | A secure, hardware-isolated area of a processor that ensures code and data loaded inside are protected from the rest of the system, including the operating system. | Tony Douglas cited TEE work in the context of privacy-preserving agent workflows ([2026-03-03](../meeting-notes/2026-03-03.md)). |
| Zero-knowledge proof (ZKP) | A cryptographic method by which one party can prove to another that a statement is true without revealing any information beyond the validity of the statement itself. | Ty described ZKP patterns where agents return only boolean results to prevent data leakage ([2026-03-03](../meeting-notes/2026-03-03.md)). |
