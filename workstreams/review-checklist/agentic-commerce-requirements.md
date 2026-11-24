# Agentic Commerce requirements for the cross-WG review

Status: Draft input to the Cross-WG Security and Privacy Review Checklist, prepared by Francesco Marinoni Moretto as the Agentic Commerce WG point of contact for this checklist (action item of the 2026-11-10 meeting). It is the author's reading, open for correction, and the Agentic Commerce WG has not reviewed it yet.

## How to use it

A purchase made by an agent has to answer five questions, in the order they come up. For each question, this page lists the groups it touches and the questions a reviewer can ask of a deliverable that covers that step. A sixth section covers stopping an agent, which the 2026-11-10 meeting recorded as a cross-WG seam.

The public sources behind each step, with the date each was read, are in the commerce view of the Agentic Standards Map: https://frmoretto.github.io/agentic-standards-views/commerce-needs-aaif.html

## 1. Finding the merchant and the surfaces it offers

Touches Security and Privacy and Identity and Trust. Discovery declarations include well-known files, agent cards, server cards, catalog entries and DNS names.

Review questions:

- Can an agent check that a declared surface is published by the merchant it names?
- When two declarations of the same merchant disagree, does the deliverable say what the agent does?

## 2. Knowing what is sold, and by whom

Touches Identity and Trust and Security and Privacy. Seller identity is identity work too.

Review questions:

- Does the deliverable say how the business behind an endpoint is identified?
- Who checks that the seller controls the identifiers it presents, such as a domain, a product identifier or a registry entry?

## 3. Knowing which agent is buying, and for whom

Touches Identity and Trust and Security and Privacy.

Review questions:

- Before checkout, can the merchant verify which agent is calling, on whose behalf and within which limits?
- How does the merchant learn, in time, that the agent's authority has been withdrawn?
- Which buyer data may the agent pass to the merchant, and where is that scope stated?
- Does the deliverable cover an agent buying for a person as well as a workload acting on its own behalf?

## 4. Agreeing the terms, authorising and paying

Touches Security and Privacy, with the payment guardrails named in this workstream's README: fund draining, account leaks and payment-agent scope limits.

Review questions:

- Is the payment authority scoped by amount, payee, time and number of uses, and can the payee check that scope?
- Can each party show afterwards what the buyer agreed to, at which price and on which terms?
- When a purchase is cancelled, what happens to credentials or mandates already issued for it?

## 5. Keeping the evidence

Touches Observability and Traceability, with Security and Privacy for integrity and retention.

Review questions:

- Given a disputed order, can buyer, merchant and payment network each produce a record of what happened, refusals included, and do the records match?
- Does the record tell a check that failed apart from a check that did not run?
- Which party keeps which record, and for how long?

## 6. Stopping an agent

Touches Security and Privacy (kill switch), Identity and Trust (revocation) and Workflows and Process Integration (bounded autonomy).

Review questions:

- Who can stop the agent while it acts?
- What happens to authority it has already used, such as a payment in flight or a credential already issued?

## Sources and disclosure

- Commerce view: https://frmoretto.github.io/agentic-standards-views/commerce-needs-aaif.html
- Agentic Standards Map, seams note: https://frmoretto.github.io/agentic-standards-map/seams.html
- Meeting notes of 2026-11-10 in this repository.

The author takes part in some of the external work the map cites, such as UCP and the IETF AUDIT and vCon groups; the map's disclosure page lists it.
