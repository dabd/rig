# Future Tokens fidelity review

Reviewed on 2026-09-06 against all ten complete `SKILL.md` files in
[dabd/FUTURE_TOKENS at 7a453aca](https://github.com/dabd/FUTURE_TOKENS/tree/7a453aca335eeb9854c6ca74b5f46c2451bebddc).
Rig's initial concise adaptation was commit `63b8c87`. The fork was not changed.
The maintained local copies live in `claude-shared/skills/`; Codex and the
installed profiles use links to those copies. These are local adaptations,
not an automatically synchronized mirror of the fork.

The first rewrite preserved the skills' headline purposes but weakened some
distinctive methods and narrowed some supported uses. This review restores
those capabilities while retaining concise entrypoints and conditional references.

## Findings and corrections

| Skill | Finding | Correction or retained behavior |
| --- | --- | --- |
| antithesize | Discovery emphasized only rival theses; an alternative could leave the original recommendation unchanged. Some opposition methods disappeared. | Route by purpose; require material opposition for a rival thesis; retain failure modes, cruxes, and evidence. Restore reparameterization, subgroup/reference-class tests, repeated-risk reasoning, and lived-experience/foil modes in the reference. |
| dimensionalize | Fidelity and complexity lost some of their original subcriteria; measurement endpoints were implicit. | Restore validity across time/scale/context, cognitive load and overfitting checks, and interpretable endpoints. Keep hard constraints separate from controllable dimensions. |
| excavate | No consequential loss found. | Keep the layered assumption map, five assumption types, crux/uncertainty/leverage distinctions, probes, and diagnostic boundary. No edit needed. |
| handlize | Contextual novelty became optional, allowing generic advice to pass as an extracted handle. | Check what changes relative to the user's existing practice; require operational substance for burned terms, honour their requested treatment, and flag connected-model dependence. |
| inductify | The compact procedure underrepresented values, evidence structure, timing, base rates, and absent commonalities. | Restore these comparison dimensions and checks for competing patterns, near-duplicate cases, shared sources, and unknown mechanisms. |
| metaphorize | A conceptual default made applicable mathematical transfer too optional. Source selection and preservation of essential premises were implicit. | Carry relevant formalism with units and a worked transfer unless the user requests conceptual-only treatment. Make invariants checkable, reject exclusions that remove required premises, and retain composite/reverse-map checks. |
| negspace | The general omission audit lost some of its distinctive continuation/pivot analysis. | Reconstruct expected continuations at specific textual discontinuities. Keep genre expectations, alternative explanations, and the prohibition on invented probabilities or hidden-motive claims. |
| rhetoricize | Generic wording analysis obscured the multi-axis and grammatical transformations. | Restore thesis/posture/context, same-stance/opposing/neutral comparisons, and named grammatical mechanisms. Preserve facts, modality, quantifiers, attribution, and optional satire boundaries. |
| rhyme | The rewrite became too system/mechanism-focused for lightweight creative uses. | Restore visual, narrative, role and sequence cues; vary breadth/tightness by purpose; retain source-knowledge, timescale, abstraction-level, and anchoring checks. Support requested composite and opposite patterns without demanding a full model. |
| synthesize | Decision sufficiency and explanatory scope became a generic quality check; generativity was weakly specified. | Restore same-question checks, representative cases from both inputs, answering from the synthesis alone, and omission-to-risk tracking. Seek added implications while allowing an honest finding of limited generativity. |

## Deliberate differences retained

- Fixed finding counts, paragraph minimums, compulsory output tiers, and numeric
  quality cutoffs remain removed. Requested depth, formats, and constraints
  still govern the result.
- Qualitative textual expectations replace claims of measured perplexity or
  next-sentence probabilities. No such measurements are available in this workflow.
- Quantifiers and uncertainty remain factual constraints during rhetorical
  transformations. Changing them is not merely a change of tone.
- Mathematical transfer requires applicable assumptions. Numerical examples
  do not establish calibration, waiting-time distributions, or observed gains.
- Useful critical constraints are retained even when the user cannot control
  them. Evidence-poor induction is labelled tentative instead of judged by
  sentence count alone.
- A brief self-check belongs in ordinary synthesis; independent studies,
  ongoing measurement, and tool mutations require their own task scope.

## Regression probes

These are reusable behavioral acceptance cases for a future independent
evaluation. They guided the source review; they are not recorded model-test runs.

| Skill | Probe | Behavior to check |
| --- | --- | --- |
| antithesize | Oppose adopting microservices for a low-traffic team whose stated benefit is future scale. Separately falsify "every request completes under 100 ms" with one valid 150 ms request. | The first yields a standalone opposing recommendation using the actual constraints. The second gives a counterexample without manufacturing a rival worldview. |
| dimensionalize | Compare queue designs with a mandatory retention rule, controllable concurrency, and workload-dependent latency. | Treat retention as a gate, define usable endpoints, check whether the latency measure remains comparable, and avoid inventing numeric F/L/C scores. |
| excavate | Diagnose "launch a premium tier next quarter" when demand, delivery capacity, and values are uncertain. | Distinguish assumption types, map dependencies without circular paraphrase, locate cruxes, and propose probes without deciding the launch policy. |
| handlize | A team already follows "communicate clearly"; a text adds "each handoff names an accepting owner" and the undefined phrase "future-proof collaboration." | Test novelty in that context; retain the concrete handoff mechanism if new, reject empty relabelling, and allow no survivors for an entirely empty input. |
| inductify | Infer a general rule from two retellings of one successful launch, then compare genuinely distinct successes and failures. | Treat the retellings as dependent evidence. Examine base rates, counter-patterns, values/constraints, and absent expected similarities before extrapolating. |
| metaphorize | Map a stable work queue to issue handling with 20 arrivals/day and a 5-day mean residence time. Then remove the stable-flow assumption. | Carry L = lambda * W to a hypothetical 100-item average with units and assumptions. Do not infer tail latency or claim the transfer still holds after removing a required premise. |
| negspace | A memo says a pilot "missed its adoption target" and immediately pivots to "our long-term commitment remains strong," without an outcome or next step. | Anchor the missing continuation at the pivot, distinguish plausible omissions from necessary premises, and avoid asserting cancellation or deceptive intent. |
| rhetoricize | "The team delayed two launches; customer impact remains uncertain." | Explore framing and agency while preserving who acted, the count, and uncertainty. Do not turn uncertainty into established harm. |
| rhyme | Give loose narrative or visual inspiration for an escalating automation failure; separately request strict operational parallels. | Allow creative cues in the first case. Demand stronger structural/functional overlap and clearer non-transfers in the second without building a full metaphor by default. |
| synthesize | Reconcile focus benefits and coordination costs of remote work for a mixed-task team. Contrast this with two positions answering different questions. | Preserve cases from both inputs and give usable conditions, limitations, and supported added implications. Clarify different questions instead of forcing agreement. |

## Validation boundary

Review covered the original and revised entrypoints plus every existing
supporting reference. Structural checks cover frontmatter, reference resolution,
and installation links. They do not establish behavioral equivalence or prove
that a particular model performs better. No independent model benchmark was run.
