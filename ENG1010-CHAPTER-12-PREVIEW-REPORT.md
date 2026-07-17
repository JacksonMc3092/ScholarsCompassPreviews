# ENG 1010 Chapter 12 HTML Preview Report

## Status

The approved Chapter 12 content has replaced the placeholder page in the preview repository.

Student-facing chapter: **Chapter 12: Finding and Evaluating Sources**  
Current preview path: `1010/chapter-6.html`  
Full-deployment path and filename will be updated during the approved direct-renaming pass.

## Content integrated

The HTML preview includes the complete approved instructional architecture:

1. Research as a route from topic to question to keywords
2. Library databases, Google Scholar, and the open web
3. A repeatable search cycle and practical search operators
4. SIFT
5. Lateral reading and click restraint
6. Credibility versus usefulness
7. The approved ethos, logos, and pathos reminder
8. Peer-reviewed academic, other scholarly, popular, trade or professional, government, advocacy, primary, and reference sources
9. Source-log guidance and completed example
10. MLA information gathering and citation models
11. Source-triage practice
12. A guided source-log entry and research checkpoint
13. Attribution and Works Consulted

The approved Revision 1 source-type material and rhetorical connections are fully integrated. The placeholder notice and placeholder prose have been removed.

## Interactive elements

The preview includes four chapter-specific tools:

- **Keyword Builder:** combines student-entered concepts and alternatives into starting search strings without generating a thesis or argument.
- **Three-Lane Route Chooser:** recommends an appropriate starting lane for a stated research need.
- **Source Triage:** lets students classify five practice source cards as Keep, Maybe, or Not for This Paper and compare their decisions with explanatory guidance.
- **Source Log:** saves one entry in browser local storage and supports load, clear, and clipboard-copy actions.

The tools are contained in `1010/chapter-12-tools.js`. Student-entered text is handled as text rather than executable HTML.

## Styling and responsive behavior

Chapter-specific presentation is isolated in `1010/chapter-12.css`.

- Two-column cards and forms collapse to one column on mobile.
- Comparison tables are wrapped for horizontal scrolling on narrow screens.
- Interactive controls use explicit labels.
- Dark-mode variants are included for chapter cards, fields, tables, and output areas.
- Print rules hide interactive buttons and preserve substantive content.
- No-JavaScript users retain all chapter prose, examples, instructions, source cards, and tables.

## Shared-shell integration

The page retains the stabilized Scholar's Compass shell:

- native button-based chapter disclosures;
- skip-to-main support through the shared script;
- approved ENG 1010 sidebar order;
- theme toggle;
- back-to-top control;
- quick navigation;
- print support;
- mobile container corrections;
- shared callout normalization.

The page loads `app.js?v=20-preview` followed by `chapter-12-tools.js?v=1`.

## Static verification

- The placeholder file was replaced rather than supplemented with a shortened alternate chapter.
- The deployed file begins with a complete HTML document and closes with the footer, shared script, chapter tool script, `body`, and `html` tags.
- Twelve numbered chapter sections are present.
- The approved peer-review, popular-source, trade/professional-source, and rhetorical-appeal material appears in the deployed page.
- The chapter-scoped JavaScript file is a complete self-contained function with initialization for all four tools.
- The chapter-scoped CSS includes mobile, dark-mode, table-overflow, and print rules.

## Browser-review checklist

1. Open Chapter 12 through the ENG 1010 preview homepage or sidebar.
2. Confirm all twelve section headers expand and collapse.
3. Test the Keyword Builder with two concepts and comma-separated alternatives.
4. Test each Route Chooser option.
5. Complete at least two Source Triage cards and compare decisions.
6. Save, reload, copy, and clear a Source Log entry.
7. Check the academic/popular/professional comparison table on desktop and mobile.
8. Toggle dark mode.
9. Open print preview and confirm all chapter sections appear.
10. Disable JavaScript or use a no-script test and confirm the substantive chapter remains readable.

## Verification boundary

Repository structure, content integration, handler coverage, and source-file completeness are verified. Final visual and browser-behavior approval depends on the GitHub Pages preview click-through.

## Content-integrity statement

This implementation preserves the approved Chapter 12 substance and Revision 1 additions. It does not alter the protected content of any other chapter and does not touch the canonical Scholar's Compass repository.
