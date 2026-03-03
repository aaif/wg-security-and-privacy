# Security and Privacy Working Group — Meeting Notes

**Date:** February 17, 2026

---

## Welcome

- Review the starting point for this WG
  - Why are we here? Who are we? What problems are we solving? How will we solve those problems?
  - What do we want to get out of this WG? What do we expect to contribute here?
  - What are the expected outcomes? What will we deliver to the community?

---

## Discussion Topics

### Attestation of Agent and Model in Use

- Zero knowledge models
- Agent Threat Model Framework
- Attack taxonomy
- Red-team scenarios
- Testing harness definitions

### Agent Identity and Delegated Authorization

- We need a "capability" based auth model
- OAuth doesn't cut it
- How does an Agent authenticate to an MCP server?
- How does an Agent represent itself to infrastructure?
- How does an Agent authenticate and authorize itself to another agent?
- Restrict and audit what a user and agent can do — together, and separately
- An app can talk to a database, and now with agents/AI this app may talk to this database under some context
- What tools can a user run/execute? How to ensure an agent can only invoke a tool it should?
- Should we advise against multiple agents within a single application?
- What about operational practices? Are there good sources for best operational practices for agentic AI security? Does that area need more work?
  - Wes: We have published this: <https://engineering.block.xyz/blog/genai-security-principles>
  - Wes: Happy to refine this with the group

### Prompt Injection Mitigation

- Needs standardization
- Social engineering resistance
- Testing corpus

### Personally Identifiable Information (PII) Obfuscation

### Secure Memory Specification

- Data classification
- Crypto standards

### Auditability and Forensics

- Decision traceability
- Tools invocation and audit logs
- Memory access logs — see Secure Memory Specification
- Observability
- "Conversation" traceability — i.e. associating tools + messages into a single context (conversation)

### Attack Surface Management / Continuous Threat Exposure Management

### Commerce and Payments

- Open standards
- DeFi integration / Blockchain

### Tooling and Plugins

- Agent tool manifest
- Agent middleware as a solution for guardrails, context management, etc.
  - We created a library extension to the PydanticAI framework to enable operations such as: `before_run`, `after_run`, `before_model_request`, `after_tool_call`, etc. — <https://github.com/vstorm-co/pydantic-ai-middleware>
  - Most "guardrails" solutions work by validating the agent's input or output. But what about the steps in between — when the agent calls the tool?
  - Middleware could help create custom hooks which would allow for dynamic addition of context, e.g. before starting the tool "X" we fetch additional instructions / search in long-term memory
  - This functionality is inspired by the Langchain library.

### Eval Framework for Compliance/Security of an Agent

### Agent + Model Attack Surface

- Model weaknesses that translate into agent vulnerabilities
- How to measure the security of an AI Agent. Are there any observability tools (features) for the security layers?

### Agentic AI Memory Layer and Security

- What are the security standards for working with memory layers?
- Context: we've created a memory layer and want to tackle the security layer now to make it more enterprise-ready

### Certification Criteria for Different Levels of AI Systems

### Agentic Security Critic or Verifiers as Plugin to Workflows

---

## Scope (In/Out) Topics

- Checkpointing
- Sandboxing

---

## Potential Deliverables

*(To be defined)*

---

## Other Initiatives

- OWASP — Agentic Team
- AIUC-1

---

## Taxonomy

*(To be defined)*
