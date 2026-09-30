# Runtime Governance Patterns

**3.1 Approval Checkpoint Pattern**

**Pattern Metadata**

| Attribute | Value |
| :---- | :---- |
| **Pattern Identifier** | SP-XXX (to be assigned) |
| **Pattern Category** | Runtime Governance |
| **Status** | Candidate |
| **Security Objectives** | Integrity, Accountability |
| **Privacy Objectives** | Data Minimization |
| **Applicable Lifecycle** | Design, Runtime |
| **Related Patterns** | Tool Approval, Tool Parameter Validation, Runtime Policy Enforcement, Audit Trail, Delegation Constraint, Rollback |

**Intent**  
 Make a human or policy approval apply to the exact action that executes, for a stated period, and keep what the approval allowed separate from what the service later reports actually happened.

**Problem**  
 An approval is often recorded as a flag next to a request. The action that runs later can differ from what was shown to the approver (other arguments, another target, a regenerated artifact), the approval can be reused after it should have lapsed, and a recorded approval is easily read as proof that the effect happened. Three failures follow: an action runs under an approval that was given for something else, an old approval authorizes a new action, and an audit trail reports an effect that no service ever confirmed.

**Context**  
 Apply this pattern when an agent's tool calls or workflows change state outside the agent (tickets, payments, code, infrastructure) and a person or policy must agree first. It matters most when the agent can regenerate or modify its proposed action between approval and execution, when execution is asynchronous or retried, and when an auditor later has to answer both "was this allowed" and "did it happen".

**Solution**  
 Bind the approval to the action. The approval record states what was approved: the action or tool, the target, the arguments or artifact (directly or as a digest over a canonical form that the record names), any constraints, who or what approved, the validity interval, and how many times it may be used. Where a value is sensitive, bind a digest of it instead of the raw value, and keep only the fields the check needs. Where some variation is acceptable (for example a timestamp field), the approval says which fields may vary rather than leaving it implicit.

Check the binding where the action executes. The enforcement point recomputes the bound fields, including any digest, from the action that is about to run and compares them with the approval record; it does not accept a digest or a match claim supplied with the action, and it does not compare against the proposal that was shown. A changed action needs a new applicable approval. An approval outside its validity interval or already used up is rejected. Validity is judged against the enforcement point's clock, with a stated tolerance for clock skew; the approval record carries the interval, the enforcement point carries the clock and the tolerance. If the approval cannot be checked, the action does not run. An approval record that fails its own integrity check is an integrity failure, not a non-match, and an approval that cannot be checked is reported as unavailable; the three are reported separately. The approval must come from a source the acting agent cannot write to or impersonate; establishing the approver's identity and authority is an input from the Identity & Trust Working Group. An approval permits an action within the agent's existing authority; it does not grant new privileges.

Keep decision, execution and effect as three records. The approval is a decision. The execution attempt is a second record. The effect is what the target service reports, correlated to the execution through an identifier whose meaning and scope the service defines. The execution record carries two identifiers and keeps them apart: the execution identifier, which the enforcement point assigns when it releases the action and against which the approval's use is charged, and the service's identifier, recorded as the service returned it or recorded as absent. One execution identifier is expected to yield one service identifier; a second, different one is recorded, not discarded, and is a conflict. A retry under the same execution identifier that returns a different service identifier is a conflict between receipts, charged as one use; whether the service acted twice is exactly what the conflict leaves open. An approval never stands in for an execution, and an execution never stands in for a confirmed effect.

Report absence as absence. Missing confirmation makes the effect unconfirmed, not "did not happen". A repeated identical receipt is one effect, deduplicated under the service's own rules for receipt identity; receipts that disagree are a conflict and stay visible. So do two receipts under one execution identifier that name different service identifiers.

**Consequences**  
 **Benefits**  
 • An approval cannot silently authorize a different or later action.  
 • Auditors can answer "was it allowed", "was it attempted" and "was it confirmed" separately.  
 • Duplicate receipts do not inflate the count of effects, and a retry under the same execution identifier is charged as one use; it yields one effect only where the service honors that identifier.  
 **Drawbacks**  
 • Binding arguments needs a canonical form, named in the record, and a rule for acceptable variation; without one, benign changes cause spurious re-approval. The form decides what the digest binds: a digest over one canonical serialization of the whole argument object binds the number and order of array elements, while a check that compares per-field digests one at a time, or combines them as an unordered set, does not bind the count unless the count is itself a field.  
 • Effect confirmation depends on the target service returning something usable and on configured trust in that response.  
 • Frequent approvals invite approval fatigue, where people approve without reading.  
 **Residual Risks**  
 • A stored approval record is evidence of a decision, not by itself a mechanism that prevents an unapproved call; enforcement lives at the execution point.  
 • A digest does not conceal low-entropy arguments; treat bound values according to their sensitivity.  
 • Binding shows the executed action matches what was approved, not that the approver understood what they approved; what the approver sees should be derived from the bound content, not from the agent's own description of it.  
 • If the action or resource state can change between the check and the effect, the pattern needs an explicit freshness or atomicity rule; it does not provide one on its own.  
 • Binding shows that the check found a match; it does not show that the check itself is correct or complete. A check that omits a rule still reports matches for everything else, so the check needs tests that fail when a rule is removed, and a passing binding is no stronger than those tests.

**Related Patterns**  
 Tool Approval and Tool Parameter Validation (both in 3.3) overlap with the binding step; this pattern is the governance view across tools and workflows, and where the boundary sits is open for the group. Runtime Policy Enforcement (3.1) supplies the enforcement point; this pattern states what it requires of that point (recomputing the binding from the action about to run, judging validity by its own clock and a stated skew tolerance, and refusing when the approval cannot be checked) without defining the point itself. Semantic Constraint (3.1) governs what an action may mean; this pattern binds what an approval covers, and a constraint carried in the approval record is one input to that binding. Audit Trail (3.7) holds the three records. Delegation Constraint (3.6) covers approvals given on someone else's behalf, and Rollback (3.2) covers undoing an effect that was confirmed but should not have happened. Kill Switch (3.2) meets this pattern at two points. A cooling-off queue that holds a high-risk dispatch until an operator or a counter releases it is an approval, and this pattern states what that release binds and how it is checked. Compensating rollback reads the in-flight execution log; that log is the execution record here, and a compensating call needs both the execution identifier, to know what “ applicable approval" (V2) and from "check unavailable" as released, and the service identifier, to address what was done. The authorization boundary that Kill Switch calls purpose binding is the existing authority this pattern assumes and does not grant.

**Implementation Considerations**  
 Implementation guidance for this pattern is intentionally omitted from this catalog. Refer to the Agentic AI Security Best Practices Guide for details.

**Appendix: Proposed Validation Cases (input for the Best Practices Guide)**

Validation belongs to the Best Practices Guide under section 1.4. These cases are kept here while the pattern is Candidate so the group can see what the Solution commits an implementation to. They are proposed expectations for the group to settle, not results.

| Case | Situation | Expected result |
| :---- | :---- | :---- |
| V1 | Baseline: matching valid approval, service confirmation meeting the configured trust | Approval applies; service-reported effect confirmed |
| V2 | Action or artifact changed outside the approved scope | Approval does not apply; a new applicable approval is required |
| V3 | Approval expired | Rejected; the enforcement point's clock and stated skew tolerance decide, not the agent's |
| V4 | Service confirmation missing | Effect unconfirmed, not evidence that nothing happened |
| V5 | Identical receipt delivered again | One effect, deduplicated under the service's receipt-identity rules |
| V5a | Two receipts under one execution identifier that disagree (different content or different service identifier) | Both recorded; the effect is a conflict, not one effect and not two, and stays visible; resolving it is outside this pattern. |
| V6 | A second, distinct execution under an approval whose uses are exhausted | Rejected |
| V6a | Retry of one execution (same execution identifier) | One use, not two; a receipt returned on retry that differs from the one already recorded is V5a |
| V7 | Approval record fails its own integrity check (signature or record digest does not verify) | Rejected as an integrity failure, reported distinctly from "no  |
| V8 | Approval cannot be checked (approval source unreachable) | Action does not run; reported as unavailable, distinct from V2 (does not apply) and V7 (integrity failure) |

**Notes for the Working Group**

Open for the group: which fields an approval must bind at minimum; what counts as sufficient confirmation of an effect; how delegated or multi-party approvals fit; and whether revocation before execution is in scope and, if so, from which source its status comes. Revocation after the check and before the effect is the same time-of-check/time-of-use gap the freshness risk names.

For section 5 (Inter Pattern Relationships): the boundary between this pattern and Tool Approval, and what this pattern requires of Runtime Policy Enforcement, are stated under Related Patterns above and offered as input.

