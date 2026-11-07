# Corpus record and release audit

Read this when setting up the corpus manifest or running the completion audit. Paths in `manifest.json` are relative to the manifest's directory unless absolute. Save the manifest and search log alongside the downloaded corpus, not only in the lecture.

## Minimal corpus layout

```text
project/
  lecture.md
  corpus/
    manifest.json
    search-log.md
    fulltext/
    notes/
    gaps.md
```

Adapt names and locations to the user's workspace. Keep a stable ID even if a paper's citation changes. The full-text copy may be PDF, HTML, or TEI XML when that is the lawful complete source. Supplements that underpin a result should have their own paths and hashes.

## Manifest schema

```json
{
  "scope": "Question, inclusion and exclusion criteria, date range",
  "cutoff": "2026-09-28",
  "search_log": "search-log.md",
  "lecture": "../lecture.md",
  "unresolved_candidates": [],
  "records": [
    {
      "id": "P001",
      "title": "Exact title",
      "authors": "Authors",
      "year": 2026,
      "doi": "10.example/123",
      "primary_url": "https://publisher.example/paper",
      "kind": "original",
      "full_text": {
        "path": "fulltext/P001.pdf",
        "sha256": "64-character lowercase hexadecimal digest",
        "version": "version of record",
        "retrieved": "2026-09-28",
        "pages": 12
      },
      "reading": {
        "status": "complete",
        "note_path": "notes/P001.md",
        "evidence_locators": ["p. 4, Eq. (3)", "p. 8, Fig. 2", "supplement p. 2"],
        "equations": [
          {
            "source_locator": "p. 4, Eq. (3)",
            "latex": "R=K/C",
            "variables": {
              "R": "Achievable rate of completed rounds; nonnegative scalar, rounds/s",
              "K": "Available signature supply rate; nonnegative scalar, signatures/s",
              "C": "Signature consumption per completed round; positive count, signatures/round"
            },
            "meaning": "Divide the available supply per second by consumption per round to obtain the supply-limited round rate",
            "assumptions": "No network bottleneck"
          }
        ],
        "no_central_equation_reason": ""
      },
      "source_coverage_path": "notes/P001-source-coverage.md",
      "lecture_sections": ["Signature throughput and consensus"]
    }
  ]
}
```

For a work with no central equation, set `equations` to `[]` and give a concrete `no_central_equation_reason`; record key parameters or rules in its reading note. If a formula is your own consequence rather than copied from the paper, label it **lecture derivation** and cite the source premises separately. An `unresolved_candidates` entry should include title/URL, reason full text is missing, sources tried, and effect on coverage. Do not set the array empty until screening resolves those entries.

`reading.equations` records the central technical reading; it is not an inventory of every source formula. For each target original, add `source_coverage_path` pointing to the separate ledger below. The current audit script does not validate this field or enumerate source items; the release review must inspect it manually.

## Source coverage ledger

Create this ledger before drafting and reconcile it against the final artifact. State the exact source version and included body, appendices and supplements. Complete coverage is the default for target originals; an explicitly selected scope may be narrower. A supporting reference used only for a definition or visual convention is not automatically a target for full reproduction. Keep that distinction explicit and do not quietly demote requested papers to reduce the work.

Inventory all numbered and unnumbered scientific formulas, substantive inline expressions, figures, tables and meaningful subpanels/views. Include scientific content embedded in HTML or interactive components; ignore only non-scientific decoration such as logos and interface controls. Exact repeated formulas can share an entry with every original occurrence listed. If a source has none of a particular item type, record zero with a checked scope instead of manufacturing an item.

Use a compact table or equivalent structured file:

| Source item | Exact source location | Lecture destination | Treatment and verification | Status |
|---|---|---|---|---|
| Equation 3 | p.4, Eq.(3) | Method, formula 2 | Original expression; all quantities and operations explained | covered |
| Unnumbered equation U1 | p.5, paragraph beginning “…” | Worked derivation | Equivalent notation; symbol mapping checked | covered |
| Figure 2a–d | p.8, all four panels | Experiment, figure 4 | Original panels; axes, legends and labels readable | covered |
| Table 1 | p.9 | Results, table 2 | Values transcribed and checked against source | covered |
| Interactive figure U2 | HTML section/selector and source asset | Explanatory appendix | Meaningful states retained; full interactive source linked | gap |

Use `covered` only after checking both fidelity and the delivered rendering; `gap` means work remains. Name the missing content or access problem rather than substituting a vague “discussed in text.” For source equations, reproduce the mathematical content or a demonstrably equivalent form, with explicit notation mapping and local teaching explanation. Merely mentioning the topic is not coverage.

For figures and tables, retain all scientific panels, annotations, labels, legends, scales, units, values and uncertainty. Splitting a wide figure, translating labels or transcribing a table is acceptable when no scientific information is lost. Clearly identify originals, faithful redrawings and explanatory schematics. A faithful redrawing can preserve coverage when appropriate, but retain original images when the user explicitly requires them. New teaching schematics cannot substitute for source figures. For animation or interactivity, identify the representative scientific states and preserved panels; do not imply that one arbitrary frame contains every result.

Link each new teaching diagram to its source code/configuration/data and the inspected field convention or primary-paper style reference. For architectures, verify that its arrows describe the actual computation and its input/output types, module order, dimensions, branches and repeated blocks match the source. Distinguish trained functionality from an architectural guarantee; keep tool interfaces outside the model unless they actually belong to it.

At release, report counts by item type and scope, covered destinations and unresolved gaps in the project notes. Preserve secondary required content in an explanatory appendix when useful. Do not remove a source item merely to make the prose shorter, hide a gap by shrinking an image beyond readability, or claim all items are covered because only the numbered figures were counted. This ledger supports a manual coverage review; it cannot prove its own source enumeration is exhaustive.

## Per-paper note: required substance

For each target original, the note should let another researcher locate and check the result without guessing. A background reference used only for a specific definition or convention needs a verified passage, locator and accurate read scope, not a claim of full-paper reading:

- Bibliographic identity, version, local full-text path and retrieval date.
- Research question; one-sentence contribution in the paper's own model.
- Method trace for central technical papers: a concrete input, actors and what each knows, ordered operations, intermediate states or messages, verification, output, and the step that contributes the paper's new idea. Separate the contribution from inherited components and assumptions.
- Central equations or quantitative rules, exact page/equation/figure locations, each quantity's concrete meaning, role/source, type/dimensions and units, derivation or independent numerical check, and operational interpretation. Check dimensions, normalization, conditioning, and whether a mathematical map represents a deterministic physical operation. Follow the [formula explanation requirement](../SKILL.md#explain-each-formula-as-a-computation-or-argument) when translating these notes into a lecture; a variable-to-unit mapping alone is not an explanation.
- One small hand-checkable worked example of the central mechanism when feasible: record the input, intermediate result, output and calculation. Label self-constructed examples and clarify their scope where misunderstanding is likely; do not pass them off as paper experiments or exact implementations. Do not require a ritual “does not prove” sentence after every example.
- Proof/model assumptions, empirical setup and uncertainty, explicit limitations, and the strongest conclusion actually supported.
- Where a system or security claim is central, distinguish what the equation proves, what the protocol adds, and what further assumptions are required for the advertised property.
- Experimental guidance and access when relevant: original prompts/protocols and locators, candidate categories or hypotheses supplied, available tools, returned information, forbidden operations and their enforcement, and which findings were independently inferred. Record a short decisive excerpt or translation for the lecture when those details change the interpretation.
- Required source formulas/figures/tables and their destinations in the source coverage ledger. For unfamiliar concepts, note the prerequisite chain, concrete examples and system locations the lecture must explain.
- Relation to predecessor, contrary evidence, and which lecture section uses it.

Avoid mechanically filling a note with an abstract and a generic “future work” line. For surveys, explain search method and categories; for standards, identify normative parameter tables and version; for empirical reports, preserve measurements separately from projections.

Before accepting a central paper's lecture section, read only that section and try to explain its mechanism to a newcomer. If you can repeat the symbols and objections but cannot walk through a single input-to-output run, the section is not yet teachable. Rewrite its main explanation rather than attaching an afterthought paragraph.

The release review must check two things separately: complete coverage of the required original formulas/figures/tables, and adequate explanation of every scientific formula actually used in the handout, including supporting definitions and statistics. Check that the reader can identify each quantity, describe the operations and their rationale, and interpret the output. Also check unfamiliar non-mathematical concepts, concrete experimental objects and diagram locations. Record gaps and repairs in the notes; the manifest's central-equation fields or an arithmetic check do not certify coverage or understanding.

## Search log and closure decision

Record each search date, database/site, full query, filters, results screened, exclusions with reason, and newly eligible IDs. Track backward and forward citation passes and the final pass with no new eligible works. Note that indexing, publication and access change after the cutoff. The closure statement should say **comprehensive within the documented scope and cutoff**, never “all existing papers” without a falsifiable enumeration.

The audit script returns a nonzero exit code when its required fields, local full texts, hashes, reading evidence, paper-to-lecture mapping or candidate-gap closure are missing. It does not inspect the source coverage ledger, verify every formula or panel, judge explanation quality, or inspect PDF layout. A passing script is one documentation check, not proof of complete source coverage, exhaustive search or scientific correctness. Before release, manually reconcile the ledger, run a reader-comprehension and concision pass, and inspect the final rendered output.
