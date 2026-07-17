# ENG 1010 Regression and Deployment-Readiness Report

**Date:** July 17, 2026  
**Repository:** `JacksonMc3092/ScholarsCompassPreviews`  
**Scope:** ENG 1010 homepage, fourteen chapter pages, shared shell, shared and chapter-specific interactive tools, and the approved Chapter 12 replacement

## Overall status

**Ready to enter deployment packaging.**

The preview has passed the preservation, chapter-order, shared-shell, mobile, accessibility, print, no-JavaScript, interactive-handler, and Chapter 12 content checks needed to prepare a main-site deployment package. The canonical Scholar’s Compass repository has not been changed.

Two small normalization items should be completed inside the deployment package rather than treated as reasons to delay the package:

1. Rewrite the homepage chapter cards into the approved order at the HTML level. The current preview uses JavaScript to reorder and renumber the original cards, so the ordinary browser experience is correct, but a no-JavaScript homepage still exposes the old order.
2. Repair the visible section-number gap in Active Reading Strategies. That chapter currently moves from Section III to visible Sections V and VI after an earlier section was removed. The substantive material should remain unchanged; only the visible Roman numerals need normalization.

Neither item affects the approved preview experience reviewed in a normal browser. Both should be corrected before the main-site cutover.

## Protected baseline and approved changes

The June 5 package remains the protected ENG 1010 baseline for Chapters 1–5 and 7–14. Chapter 6 in that package was a placeholder and is the only chapter whose substantive content was intentionally replaced.

Approved changes represented in the preview are:

- shared-shell accessibility and mobile stabilization;
- approved student-facing chapter order;
- repair of missing chapter-specific interactive functions;
- complete Chapter 12 content replacing the old Chapter 6 placeholder;
- approved Chapter 12 distinctions among peer-reviewed academic, other scholarly, popular, and trade or professional sources;
- approved light connections to ethos, logos, and pathos;
- chapter-scoped Chapter 12 styles and tools.

No other chapter was authorized for a substantive rewrite during this phase.

## Approved student-facing chapter sequence

1. Annotating Your Way to Greatness
2. Active Reading Strategies
3. Summarizing Your Way to Synthesis
4. Quoting, Paraphrasing, and Signal Phrases
5. Understanding Rhetoric: The Art of Persuasion
6. Values, Assumptions, and Ideology
7. Strategies for Getting Started
8. Crafting Powerful Thesis Statements
9. Designing Effective Paragraphs
10. Analysis and Synthesis
11. Argumentation: Joining the Academic Conversation
12. Finding and Evaluating Sources
13. Using Sources in Your Argument
14. Revision: From Draft to Final

The shared navigation array matches this sequence. The preview homepage cards are reordered and renumbered at page initialization.

## Regression matrix

| Area | Result | Evidence and deployment note |
|---|---|---|
| Fourteen-chapter inventory | Pass | All fourteen ENG 1010 chapter files are present. The Chapter 12 placeholder has been replaced with the approved full chapter. |
| Homepage order | Pass with deployment normalization | JavaScript presents the approved order. Static HTML still contains the old order and must be rewritten during deployment for no-JavaScript consistency and to remove reordering flash. |
| Sidebar order and current-chapter state | Pass | Shared navigation is generated from the approved sequence and compares the current filename with the chapter destination. |
| Internal chapter links | Pass for current preview | Existing chapter destinations are present. Numbered labels are normalized in the preview. All visible labels and destinations must be rewritten together when files are renamed. |
| Section disclosures | Pass | Shared initialization converts legacy clickable headers into keyboard-operable controls and preserves native buttons already present in stabilized pages. |
| Skip link and main landmark | Pass | Shared initialization supplies or normalizes the skip link, main landmark, and focus target. |
| Sidebar keyboard behavior | Pass | Open, close, Escape, focus return, overlay close, and mobile close behavior are present in the shared script. |
| Mobile layout | Pass | The centered chapter-container correction is active at tablet and phone widths. The user reviewed and approved the corrected mobile presentation. |
| Narrow-screen tables | Pass | Shared table wrappers and Chapter 12 comparison tables allow horizontal scrolling instead of forcing page overflow. |
| Dark mode | Pass | Shared theme persistence remains active. Chapter 12 includes scoped dark-mode rules for cards, tables, fields, and outputs. |
| Print output | Pass | Shared print rules expose all chapter sections. Chapter 12 hides interactive buttons while retaining instructional content and examples. |
| No-JavaScript chapter access | Pass | Chapter content remains visible without JavaScript. Interactive enhancements are supplemental. The homepage order normalization remains a deployment task. |
| Shared callout labels | Pass | Highlight, example, and tools callouts use the approved Key Insight, Example, and Toolkit labels with corrected spacing. |
| Chapter-specific tools | Pass for handler coverage | Every named handler found during the interactive audit has a matching definition in the shared interactive module. |
| Chapter 12 tools | Pass for source completeness and visual review | Keyword Builder, Route Chooser, Source Triage, and Source Log are scoped to Chapter 12. The user reviewed the live chapter and approved it. |
| Local save and copy behavior | Pass with migration requirement | Local storage is guarded against browser failures and clipboard actions include fallbacks. Full deployment must preserve or migrate existing keys when filenames and chapter identities change. |
| Chapter 12 source integrity | Pass | Critical CT State, Caulfield/SIFT, Civic Online Reasoning, Google Scholar, and MLA references were checked against current authoritative pages. |
| Protected prose | Pass with stated boundary | Chapter 12 is the only intentional substantive replacement. Shared-shell and function repairs were separated from chapter prose. |
| Canonical repository | Pass | The canonical repository remains untouched during preview work. |

## Findings to carry into deployment

### 1. Static homepage order

The preview’s JavaScript reorders and renumbers the original chapter cards. This produces the approved experience when JavaScript runs, but the deployment should not rely on client-side rearrangement for the primary structure.

Deployment action:

- write the approved order directly into `1010/index.html`;
- give every card its final visible number and destination;
- keep the JavaScript order array as the shared navigation source;
- verify that the static page and generated sidebar match exactly.

### 2. Active Reading visible section numbering

The Active Reading page currently contains visible Sections I, II, III, V, and VI because a prior Section IV is no longer present.

Deployment action:

- change the visible “V. Adapting Strategies for Digital vs. Print Reading” to “IV.”;
- change the visible “VI. Practice Exercises & Application” to “V.”;
- preserve all substantive text and existing section IDs unless a separate accessibility reason requires changing them.

### 3. Stable progress and local-storage identities

The preview preserves original filenames while displaying the new chapter sequence. The main deployment will rename files. Some existing tools use filename-based or legacy chapter-based storage keys.

Deployment action:

- inventory every `localStorage` key used by `app.js`, `interactive-tools.js`, and `chapter-12-tools.js`;
- choose stable semantic identifiers that do not depend on a chapter’s position;
- migrate any existing main-site keys once, without deleting the old value until the new value is confirmed;
- retain the future-facing Chapter 12 source-log key or migrate it explicitly if its final identifier changes;
- test completed-chapter state, practice trackers, prewriting saves, thesis tools, quote tools, and the Chapter 12 source log before and after migration.

### 4. Shared CSS maintenance debt

The shared `styles.css` remains a large accumulated stylesheet containing duplicated historical chapter rules. The stabilization layer safely overrides the most important conflicts, but the file remains difficult to maintain.

Deployment action for this release:

- do not attempt a broad CSS rewrite during cutover;
- preserve the tested shared stylesheet and stabilization layer;
- include cache-version updates so browsers receive the deployed corrections.

Future maintenance action:

- consolidate repeated chapter CSS only in a separate, reversible phase with screenshot and interaction comparison testing.

## Direct-renaming map for the main-site package

The following map converts the protected source files into the approved final chapter numbers.

| Current content file | Final file | Final chapter |
|---|---|---|
| `chapter-1.html` | `chapter-1.html` | Annotating |
| `chapter-2.html` | `chapter-2.html` | Active Reading |
| `chapter-4.html` | `chapter-3.html` | Summarizing |
| `chapter-7.html` | `chapter-4.html` | Quoting, Paraphrasing, and Signal Phrases |
| `chapter-13.html` | `chapter-5.html` | Understanding Rhetoric |
| `chapter-14.html` | `chapter-6.html` | Values, Assumptions, and Ideology |
| `chapter-3.html` | `chapter-7.html` | Strategies for Getting Started |
| `chapter-9.html` | `chapter-8.html` | Crafting Powerful Thesis Statements |
| `chapter-11.html` | `chapter-9.html` | Designing Effective Paragraphs |
| `chapter-10.html` | `chapter-10.html` | Analysis and Synthesis |
| `chapter-5.html` | `chapter-11.html` | Argumentation |
| `chapter-6.html` | `chapter-12.html` | Finding and Evaluating Sources |
| `chapter-8.html` | `chapter-13.html` | Using Sources in Your Argument |
| `chapter-12.html` | `chapter-14.html` | Revision |

Because several destination names are currently occupied by different chapters, deployment must be staged through temporary filenames or a single tree-level commit. Files must not be renamed sequentially in a way that overwrites unrecovered content.

## Required deployment-package edits

The deployment package should update these items as one coordinated change:

1. all fourteen filenames according to the map above;
2. `1010/index.html` card order, numbers, links, and progress metadata;
3. the ENG 1010 chapter array in `app.js`;
4. each page’s title, visible chapter number where shown, `data-page`, canonical metadata if added, and chapter-specific asset paths;
5. every internal chapter link and visible numbered reference;
6. the Revision chapter’s Works Consulted reference to the thesis chapter;
7. Chapter 12 scoped CSS and tool-script names or paths if they are renamed;
8. local-storage identity and migration logic;
9. cache-busting versions for shared CSS, stabilization CSS, shared JavaScript, and chapter-scoped assets;
10. Active Reading’s visible section numbering;
11. static no-JavaScript navigation order.

## Deployment verification checklist

### Structure and navigation

- Homepage cards appear in the approved order before JavaScript rearrangement.
- Sidebar order exactly matches the homepage.
- Every card and sidebar item opens the intended chapter.
- Current-chapter highlighting follows the renamed files.
- All old internal chapter references have been rewritten.
- No destination file was overwritten during the rename operation.

### Accessibility

- First Tab reveals the skip link.
- Skip link moves focus to the main content.
- Every section header works with Enter and Space.
- Sidebar opens from the hamburger, closes with its button, closes with Escape, and returns focus correctly.
- Visible focus remains clear in light and dark modes.
- Form fields have associated labels.
- Status and feedback messages use appropriate live regions.

### Responsive behavior

- Homepage and every chapter are checked at desktop, tablet, and 375-pixel phone widths.
- No page produces horizontal body overflow.
- Tables scroll within their wrappers on narrow screens.
- Chapter 1 annotation cards and Chapter 12 comparison tables remain readable.
- Quick navigation does not crowd mobile content.

### Interactive behavior

- Chapter 1 annotation and progress controls.
- Chapter 3 legacy-content prewriting tools after its final move to Chapter 7.
- Argument position and counterargument tools.
- Quotation and paraphrase checks.
- Quote-sandwich tools.
- Thesis analyzer and scaffold.
- Bloom’s Taxonomy and analysis tools.
- PIE paragraph builder.
- Chapter 12 keyword, route, triage, save, load, copy, and clear actions.
- Existing saved data is preserved or migrated.

### Print and no-JavaScript

- Print preview exposes every section in every chapter.
- Interactive buttons do not obscure print output.
- Chapter prose, examples, tables, and activities remain visible without JavaScript.
- The no-JavaScript homepage follows the approved order.

### Content integrity

- Chapters 1–5 and 7–14 retain the protected baseline substance.
- Approved shell changes do not remove examples, exercises, attribution, or Works Consulted material.
- Chapter 12 contains the approved source-type and rhetorical additions.
- The approved Chapter 14 ideology definition remains intact after its move to final Chapter 6.

## External-link review

Critical Chapter 12 references were checked during this pass and remain available through their authoritative publishers or institutions:

- CT State Library Research Basics;
- Caulfield’s “Four Moves” and its note connecting the framework to SIFT;
- Civic Online Reasoning;
- MLA’s Works Cited quick guide;
- Google Scholar help.

The deployment package should still run a final external-link crawl immediately before cutover because third-party pages and video resources can change independently of Scholar’s Compass.

## Rollback and release discipline

Before changing the canonical repository:

1. record the exact canonical `main` commit;
2. create a deployment branch or immutable backup ref from that commit;
3. build the complete rename and update set in the preview repository first;
4. compare the preview deployment commit against the approved preview baseline;
5. review the rendered homepage and representative chapters;
6. apply the approved deployment commit to the canonical repository;
7. verify the public site after GitHub Pages finishes publishing;
8. retain the pre-deployment commit as the immediate rollback point.

## Verification boundary

This report combines repository inspection, the existing static and browser-test records, current source verification, and the user’s visual approval of the stabilized preview and Chapter 12. The development environment could not perform a dependable automated crawl of the published GitHub Pages domain. Therefore, the final deployment package must include a live public-site smoke test after publishing before the release is declared complete.

## Decision

The ENG 1010 preview is **deployment-package ready**. It is not yet authorized for direct publication to the canonical site. The next work item is to build the full direct-renaming deployment package in `ScholarsCompassPreviews`, perform the checks above, and present that package for approval before touching `academic-writing-guide`.
