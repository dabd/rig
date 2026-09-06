## Prose (shared across profiles)

Use the installed **prose** skill for substantial engineering drafts or edits
where its genre guidance helps: PR descriptions, design documents, incident
reports, tickets, and email. Typo fixes and short messages (chat replies,
review comments, and commit messages) use the floor below; load a writing
skill for those only when requested. The laconic and aggressive compression
registers are opt-in. If the plugin is unavailable, use the floor and report
the missing dependency only when it prevents an explicitly requested workflow.

The floor that applies even before the skill loads:

- Default to clear, concise paragraphs, each developing one main idea. Use
  lists or tables when they make parallel information, steps, or comparisons
  easier to follow. Avoid nested lists unless the hierarchy needs them.
- Use familiar words, concrete examples, and precise verbs. Prefer plain
  language to jargon. Include technical detail when it helps the reader
  understand the result, reasoning, or a material limit; match the explanation
  to the background knowledge evident in the request and conversation.
- Lead with the point. State it; don't announce it. Let each sentence build on
  the previous one and develop important points with enough evidence and
  explanation to be useful. Concision must preserve needed context and support.
- Plain verbs. No figurative `delve`, `leverage`, `unlock`, `tap into`;
  literal and domain senses are fine.
- Cut emphasis adverbs, reflex hedges, and filler. Keep one honest hedge
  when the uncertainty is real.
- Avoid stock phrases and empty emphasis such as `Bottom Line:`, `foster`,
  `it's worth noting`, `importantly`, `genuinely`, and `Question? Answer.`.
  Do not add canned conclusions such as `In short:` or
  `The simplest mental model is:`. Literal domain uses remain valid.
- Active voice with named actors, except where the genre wants otherwise
  (blameless postmortems).
- No em or en dashes; use a comma, colon, period, or ' - '.
- No contrast templates (`not just X but Y`, `isn't X, it's Y`); state the
  point directly.
- State the intended action directly. Avoid unsolicited descriptions of what
  will not happen, what stays unchanged, or how the response will be divided.
  Include exclusions or unchanged behavior when needed to explain scope,
  correctness, a material risk, or an explicit user constraint.
- Avoid invented compound labels such as `exact-head checks` and
  `editorial-row layouts`, vague qualifiers, and needless hyphenated
  descriptions. Use literal verbs and prepositions; retain established
  technical terms when they help the reader.
- No mannered prose: when a literal phrase is available, use it. Keep
  sentences short and break paragraphs often.

Some profiles normalize unicode punctuation in written files with a hook.
Replies have no linter; hold the floor yourself as you draft. When
you name a banned term rather than use it, put it in backticks.
