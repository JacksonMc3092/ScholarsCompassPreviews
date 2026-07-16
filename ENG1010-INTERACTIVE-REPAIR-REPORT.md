# ENG 1010 Interactive-Function Repair Report

## Scope

This pass repairs chapter-specific controls that appeared in the protected ENG 1010 chapter HTML but did not have matching JavaScript functions in the shared site script.

The work is isolated in the new root-level `interactive-tools.js` module. The shared `app.js` loads that module after completing navigation, accessibility, theme, and disclosure initialization. No chapter prose, examples, headings, or activity directions were rewritten.

## Chapters repaired

### Chapter 1: Annotating

- Maintains the accessible annotation-card pressed state.
- Preserves the existing local practice-progress behavior.

### Chapter 3: Strategies for Getting Started

- Interactive cluster diagram: add, edit, drag, clear, save, and load nodes
- Brainstorm list: add ideas, drag or keyboard-move ideas between columns, save, and clear
- Outline builder: add editable main points, supporting points, and details; save and restore locally
- Freewriting timer: start, pause, reset, and save writing locally
- Question generator and saved-question list
- Two-method prewriting challenge launcher

### Chapter 5: Argumentation

- Academic-conversation example cycler
- Agree, disagree, and complicate position selector
- Keyboard access for position choices
- Save and clear a nuanced position locally
- Counterargument-and-response builder

### Chapter 7: Quoting, Paraphrasing, and Signal Phrases

- Direct-quotation quick check with accessible feedback
- Paraphrase coaching check that flags overly brief or overly similar wording without claiming to determine plagiarism or correctness
- Practice-progress persistence where the chapter supplies progress controls

### Chapter 8: Using Sources in Your Argument

- Quote-sandwich generator
- Clipboard copy with a manual-copy fallback when browser permissions block clipboard access

### Chapter 9: Crafting Powerful Thesis Statements

- Working-thesis coaching check
- Topic-to-thesis scaffold generator
- The generator leaves the substantive claim for the student rather than inventing unsupported evidence or conclusions

### Chapter 10: Analysis and Synthesis

- Bloom’s Taxonomy detail viewer
- Keyboard access for taxonomy levels
- Quote-sandwich paragraph generator

### Chapter 11: Designing Effective Paragraphs

- PIE paragraph generator using the student’s Point, Illustration, and Explanation fields

## Technical organization

- `app.js` remains the shared shell and single source for navigation, accessibility, sidebar, theme, index order, callout normalization, and shared progress behavior.
- `interactive-tools.js` contains only chapter-specific learning tools.
- The chapter pages continue to load `app.js`; no fourteen-page script-tag edit was required.
- The interactive module is loaded relative to `app.js`, so it works from the root, `/1010/`, and `/1020/` paths without hard-coded domain URLs.
- Student-entered text is rendered through `textContent` rather than injected as executable HTML.
- Local saves use browser `localStorage`; tools still work during the current session when storage is unavailable.

## Static verification

- Both JavaScript source files passed a Node syntax check before deployment.
- The complete set of named inline function calls in the fourteen ENG 1010 chapter files was compared with the functions exposed by `app.js` and `interactive-tools.js`.
- Every named handler found in the chapter HTML has a matching definition after this repair.
- The deployed `app.js` retains its complete closing initialization sequence and loads `interactive-tools.js?v=1`.
- The deployed interactive module begins and ends as a complete self-contained function and includes the Chapter 3 through Chapter 11 repair set.

## Browser-review checklist

The following representative controls should be reviewed on the GitHub Pages preview:

1. Chapter 3: add and drag a cluster node, save/load it, add a list item, and start/pause the timer.
2. Chapter 5: select “Complicate,” cycle the conversation example, and generate a counterargument response.
3. Chapter 7: answer the quotation quick check and test one close paraphrase and one substantially revised paraphrase.
4. Chapter 8: build and copy a quote sandwich.
5. Chapter 9: analyze a working thesis and generate a thesis scaffold.
6. Chapter 10: open a Bloom’s Taxonomy level with mouse and keyboard, then generate a quote sandwich.
7. Chapter 11: generate a PIE paragraph.

## Verification boundary

Static syntax and handler coverage are verified. Automated live-browser execution was not reliable in the development environment, so final behavior approval depends on the preview-site click-through rather than an unsupported claim of complete browser validation.

## Content-integrity statement

This repair changes functionality only. It does not revise chapter substance and does not alter the approved Chapter 14 ideology definition.