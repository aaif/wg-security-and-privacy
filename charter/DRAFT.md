# Agentic AI Foundation Working Group Charter

## Security & Privacy

### 1. Working Group Name

- **Working Group Name:** Security & Privacy
- **Short Name / Acronym:** S&P
- **Date Approved:** TBD
- **Last Updated:** 2026-04-17
- **Homepage / Repo:** https://github.com/aaif/wg-security-and-privacy
- **Primary Contact (Chair/Lead):** Alex Frazer (Chair) <alex@runlayer.com>

### 2. Purpose and Mission

#### Mission Statement

The Security & Privacy Working Group advances the Agentic AI Foundation's mission by establishing security and privacy as a shared discipline across the Agentic AI ecosystem. Producing open threat models, a shared taxonomy, and design patterns that providers, consumers, and peer working groups can adopt to share responsibility for trustworthy agentic AI.

#### Why this Working Group exists

This Working Group was formed to address:

- Agentic AI introduces novel security challenges — such as multi-agent persuasion, tool invocation risks, delegated authorization boundaries, and agent memory vulnerabilities — that are not adequately covered by existing frameworks.
- Privacy risks expand as AI agents operate autonomously across services, handling sensitive data with limited human oversight and increasing blast radius when failures occur.
- The ecosystem lacks a shared vocabulary, reusable design patterns, and open threat models specific to agentic AI security and privacy.

#### Alignment to Foundation Goals

The work of this WG supports:

- Pre-competitive collaboration that produces open outputs benefiting the entire agentic AI ecosystem, not just individual members.
- Security and privacy as an intersecting layer across all AAIF working groups, providing a shared discipline that strengthens every group's deliverables.

### 3. Scope

#### In Scope (what the WG will do)

- Threat Modeling and Attack Analysis
- Security Architecture and Design Patterns
- Agent Control and Containment
- Data Protection and Privacy
- Cross-WG Collaboration

#### Out of Scope (what the WG will not do)

- **Ethics, bias, and value-judgment questions** — Deferred to the Governance and Policy WG.
- **Interpreting or prescribing regulatory compliance** — This group may monitor standards and understand regulatory requirements at a technical level to inform its own technical controls, but will not duplicate regulatory or compliance work.
- **Certification of agentic systems or tools** — Certification criteria and programs are outside the scope of this group.

#### Assumptions and Dependencies

- **Assumptions:** Depends on and presumes coordination with other working groups and other AAIF/LF initiatives.
- **Dependencies:** Depends on and presumes coordination with other working groups and other AAIF/LF initiatives.

### 4. Goals, Deliverables, and Success Criteria

#### 3-6 Month Goals (recommended: 3–6)

- Release v0 Taxonomy of Terms and Definitions (internal)
- Deliver Agentic AI Threat Model Gap Analysis (internal)
- Release v1 Security and Privacy Design Patterns Catalog (public)
- Complete first Cross-WG collaboration

#### Planned Deliverables

For each deliverable, define owner, format, and target date.

- **Taxonomy of Terms and Definitions (v0)** — Format: Spec, Target: 2026-06-01
- **Security and Privacy Design Patterns Catalog** — Format: Spec, Target: 2026-10-01
- **Agentic AI Security Best Practices Guide** — Format: Report, Target: 2026-10-01
- **Agentic AI Threat Modeling: Gap Analysis and Framework Design** — Format: Report, Target: 2026-07-01
- **Cross-WG Security and Privacy Review Checklist** — Format: Report, Target: 2026-06-01

#### Definition of Done (DoD)

A deliverable is considered complete when:

- Reviewed/approved via WG process
- Published in repo/site

#### Success Metrics (KPIs) (pick a small set)

- **Adoption:** number of references in talks/projects/social media posts
- **Quality:** alignment and adherence to deliverable standards
- **Community:** engagement of members (average participation %)
- **Timeliness:** % of milestones delivered on schedule

### 5. Working Methods

#### Operating Model

- Consensus-driven
- Work tracked in: GitHub repo
- Primary artifacts: reports, specs, reference implementations, guidance docs, test suites

#### Meetings

- **Cadence:** Biweekly
- **Duration:** 60 minutes
- **Time Zone Considerations:** Best effort meeting timing selection (with periodic review)
- **Open Meetings:** Yes
- **Minutes/Notes:** GitHub repo
- **Recordings:** All meeting recordings are stored in LFX dashboard

#### Communication Channels

- **Async:** Mailing list, Discord/Slack
- **Sync:** Zoom
- **Announcements:** Mailing list, Discord/Slack

### 6. Membership and Participation

#### Who can participate

Participation is open to all individuals and organizations consistent with foundation policies.

#### Member Roles

- **Participants:** anyone attending meetings or contributing asynchronously.
- **Contributors:** individuals making substantive contributions (issues, PRs, docs, reviews).
- **Maintainers/Approvers (optional):** individuals with approval rights in repositories.
- **Chairs/Co-Chairs:** individuals responsible for operations and facilitation.

#### Joining

To join, a participant should sign up via the AAIF working group registration form using a business email address from an AAIF member organization.

#### Expectations

- Follow the Code of Conduct and collaboration norms.
- Make contributions in the open (issues/PRs) whenever possible.
- Declare conflicts of interest when relevant.

### 7. Governance and Decision-Making

#### Leadership Structure

- **Chair:** Alex Frazer (Runlayer)
- **Co-Chair:** Junjie Bu (Google)
- **Tech Lead(s) (optional):** None
- **Secretary/Program Manager (optional):** None

#### Selection and Term

- **Chairs are selected by:** election — simple majority
- **Term Length:** 12 months
- **Renewal:** Allowed, max consecutive terms: 2
- **Removal/Resignation:** motion with 2nd; supermajority vote

#### Decision Process

- **Default method:** rough consensus documented in issues/meeting notes.
- **When consensus cannot be reached:**
  - **Escalation path:** TC
  - **Fallback vote rules (if used):** quorum [%], threshold — simple majority, voting eligibility — all active members.

#### Quorum (if voting is used)

Quorum is met when 50% eligible voters are present or 50% have responded asynchronously.

### 8. Relationship to Other Groups

#### Internal Coordination

- **Liaison(s) to other WGs:** [Names/roles]
- **Shared deliverables/dependencies:** [list]

#### External Coordination (optional)

- **Standards bodies / industry groups:** [names]
- **Upstream/downstream projects:** [names]
- **Policy for external statements:** [who can speak on behalf of WG]

### 9. Intellectual Property, Licensing, and Compliance

> Use language consistent with foundation policies; customize only if you have explicit approval.

#### Licensing

- **Code contributions:** [e.g., Apache-2.0/MIT] (or "per repository license")
- **Documentation/specs:** [e.g., CC-BY-4.0] (or "per repository license")

#### Contribution Requirements

Contributions must comply with: [DCO/CLA policy], repository contribution guidelines, and review requirements.

#### Antitrust and Competition Law

- Meetings and communications must follow the foundation's antitrust guidelines.
- Avoid discussions of pricing, market allocation, or other restricted topics.

#### Code of Conduct

This WG adheres to the Linux Foundation Project's Code of Conduct.

### 10. Security, Safety, and Responsible AI (Agentic AI-Specific)

#### Security Practices

- **Threat modeling expectations:** [required/optional]
- **Vulnerability disclosure process:** [link or description]
- **Security review gates for releases:** [e.g., dependency scanning, SAST, SBOM]

#### Agentic Safety and Risk Management

- **Safety considerations relevant to this WG:** [e.g., tool access control, prompt injection defenses, autonomy bounds]
- **Required practices (if any):** [e.g., evaluation harnesses, red teaming, abuse case documentation]
- **Data handling expectations:** [e.g., avoid sensitive data in issues/logs]

#### Privacy

- **Guidance for handling personal data:** [policy link/summary]
- **Logging/telemetry guidelines:** [what is acceptable]

### 11. Deliverable Lifecycle and Publication

#### Release Cadence

- **Expected cadence:** [quarterly/biannual/annual/as needed]
- **Versioning scheme:** [SemVer/date-based/spec versioning]

#### Review and Approval

- **Required reviewers:** [roles]
- **Approval mechanism:** [LGTM count, maintainer approval, chair sign-off]

#### Archival / Deprecation

- **Deprecation policy:** [how and when]
- **Sunset criteria:** [e.g., no activity for N months, goals achieved]

### 12. Resources and Budget (Optional)

- **Expected infrastructure needs:** [CI, hosting, domains]
- **Funding requests (if any):** [events, audits, tooling]
- **Sponsor engagement model (if applicable):** [brief description]

### 13. Amendments

This charter may be amended by:

Vote of the Working Group, with minimum 1 week notice and documentation in repo, and subject to TC approval if required.

### 14. Ratification

By approving this charter, the Working Group commits to operating transparently, in the open, and in alignment with foundation policies.

- **Approved By:** [TOC / Governing Board / Steering Committee]
- **Date:** [YYYY-MM-DD]
- **Signatories (optional):** [Names/Titles]

---

## Optional Appendix A: Role Descriptions

### Chair

Runs meetings, sets agendas, ensures notes, drives milestones, represents WG in cross-WG coordination.

### Maintainer/Approver

Responsible for repository health, reviews/merges, release readiness, and technical direction.

### Contributor

Provides substantive work items (PRs/docs/issues), participates in reviews and discussions.
