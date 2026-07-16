# ENG 1010 Chapter-Order Review

## Status

The reordered sequence was discussed previously as a proposed instructional arc. It was not yet approved for implementation. This review confirms the proposal against the protected June 5 content baseline and the current preview-site navigation.

## Recommended sequence

1. **Annotating Your Way to Greatness**
2. **Active Reading Strategies**
3. **Understanding Rhetoric: The Art of Persuasion**
4. **Values, Assumptions, and Ideology**
5. **Strategies for Getting Started**
6. **Crafting Powerful Thesis Statements**
7. **Designing Effective Paragraphs**
8. **Summarizing Your Way to Synthesis**
9. **Analysis and Synthesis**
10. **Argumentation: Joining the Academic Conversation**
11. **Finding and Evaluating Sources**
12. **Quoting, Paraphrasing, and Signal Phrases**
13. **Using Sources in Your Argument**
14. **Revision: From Draft to Final**

## Instructional arc

The sequence moves through a coherent writing process:

**engage with a text → understand its rhetorical situation → identify its values and assumptions → generate ideas → form a thesis → build paragraphs → summarize and synthesize → enter an argument → research → quote and paraphrase → integrate sources → revise**

Placing rhetoric and values early gives students a framework for understanding what texts do before they begin producing claims of their own. Placing revision last preserves its role as a global-to-local reconsideration of the complete draft.

## Old-to-new map

| Existing chapter | Current title | Proposed chapter |
|---:|---|---:|
| 1 | Annotating Your Way to Greatness | 1 |
| 2 | Active Reading Strategies | 2 |
| 13 | Understanding Rhetoric: The Art of Persuasion | 3 |
| 14 | Values, Assumptions, and Ideology | 4 |
| 3 | Strategies for Getting Started | 5 |
| 9 | Crafting Powerful Thesis Statements | 6 |
| 11 | Designing Effective Paragraphs | 7 |
| 4 | Summarizing Your Way to Synthesis | 8 |
| 10 | Analysis and Synthesis | 9 |
| 5 | Argumentation: Joining the Academic Conversation | 10 |
| 6 | Finding and Evaluating Sources | 11 |
| 7 | Quoting, Paraphrasing, and Signal Phrases | 12 |
| 8 | Using Sources in Your Argument | 13 |
| 12 | Revision: From Draft to Final | 14 |

## Existing references affected by renumbering

The protected chapter content contains a small, manageable set of explicit chapter-number references:

- Current Chapter 2 points readers back to current Chapter 1.
- Current Chapter 12 points to current Chapters 9, 6, 7, and 8.
- Current Chapters 13 and 14 point to one another.
- The ENG 1010 index contains fourteen numbered chapter cards.
- The shared `app.js` chapter array contains the numbered sidebar sequence.
- Chapter page `data-page` values and some local-storage keys use current chapter identifiers.

The cross-references should be updated as part of one controlled reorder, not piecemeal.

## URL-preservation recommendation

Do **not** simply rename or overwrite the current `chapter-N.html` files. Those URLs may already appear in Blackboard modules, course packets, browser bookmarks, and external links.

Recommended implementation:

1. Introduce stable, title-based chapter URLs, such as `understanding-rhetoric.html` and `values-assumptions-ideology.html`.
2. Update the ENG 1010 index and shared navigation to use the new sequence and stable URLs.
3. Leave each existing numbered URL in place as a lightweight redirect with a visible fallback link to the corresponding chapter.
4. Preserve stable internal identifiers for local progress so a chapter does not become a different chapter merely because its display number changes.
5. Update all visible chapter-number references and the Works Consulted entry in the revision chapter.
6. Test old URLs, new URLs, sidebar order, index order, keyboard navigation, mobile layout, print output, and no-JavaScript fallback.

This approach allows future chapters to be inserted or reordered without breaking links again.

## Content-integrity rule

The reorder changes sequence, chapter numbers, navigation, and cross-references only. It does not authorize rewriting, shortening, replacing, or expanding chapter substance.

## Decision required before implementation

Approve the recommended sequence and the stable-URL/redirect approach before the preview files are reorganized.
