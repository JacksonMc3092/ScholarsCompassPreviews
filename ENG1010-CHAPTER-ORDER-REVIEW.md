# ENG 1010 Chapter-Order Review

## Status

Approved by the instructor and implemented in the preview repository as the student-facing display order.

The preview keeps the existing `chapter-N.html` filenames for safe testing. For full deployment to the main Scholar’s Compass site, the approved baseline is to rename the chapter files to match the new sequence and update all site references in one coordinated release. Blackboard links only to the ENG 1010 homepage, so numbered-file compatibility redirects are not required unless the final link audit finds meaningful outside traffic.

## Approved sequence

1. **Annotating Your Way to Greatness**
2. **Active Reading Strategies**
3. **Summarizing Your Way to Synthesis**
4. **Quoting, Paraphrasing, and Signal Phrases**
5. **Understanding Rhetoric: The Art of Persuasion**
6. **Values, Assumptions, and Ideology**
7. **Strategies for Getting Started**
8. **Crafting Powerful Thesis Statements**
9. **Designing Effective Paragraphs**
10. **Analysis and Synthesis**
11. **Argumentation: Joining the Academic Conversation**
12. **Finding and Evaluating Sources**
13. **Using Sources in Your Argument**
14. **Revision: From Draft to Final**

## Instructional arc

The approved sequence moves through this progression:

**annotate → read actively → summarize accurately → quote and paraphrase responsibly → understand rhetoric and worldview → generate ideas → form a thesis → build paragraphs → analyze and synthesize → argue → research → integrate sources → revise**

The early placement of summarizing and source-handling gives students practical reading-to-writing moves before they encounter the more abstract work of rhetoric, values, assumptions, and ideology.

## Preview-file-to-display-number map

| Preview file | Chapter title | Display number |
|---|---|---:|
| `chapter-1.html` | Annotating Your Way to Greatness | 1 |
| `chapter-2.html` | Active Reading Strategies | 2 |
| `chapter-4.html` | Summarizing Your Way to Synthesis | 3 |
| `chapter-7.html` | Quoting, Paraphrasing, and Signal Phrases | 4 |
| `chapter-13.html` | Understanding Rhetoric: The Art of Persuasion | 5 |
| `chapter-14.html` | Values, Assumptions, and Ideology | 6 |
| `chapter-3.html` | Strategies for Getting Started | 7 |
| `chapter-9.html` | Crafting Powerful Thesis Statements | 8 |
| `chapter-11.html` | Designing Effective Paragraphs | 9 |
| `chapter-10.html` | Analysis and Synthesis | 10 |
| `chapter-5.html` | Argumentation: Joining the Academic Conversation | 11 |
| `chapter-6.html` | Finding and Evaluating Sources | 12 |
| `chapter-8.html` | Using Sources in Your Argument | 13 |
| `chapter-12.html` | Revision: From Draft to Final | 14 |

## Deployment baseline

- Rename the numbered chapter files to match the approved sequence during the full main-site deployment.
- Update the homepage cards, shared sidebar array, chapter metadata, internal links, visible chapter numbers, and Works Consulted references together.
- Run a final inbound-link audit before deployment. Add redirects only for numbered URLs that have a demonstrated external use.
- Preserve chapter substance and stable progress identifiers while filenames and display numbers change.
- ENG 1020 navigation remains unchanged unless a shared technical repair requires otherwise.

## Preview implementation

- The shared sidebar uses the approved order and display numbers.
- The ENG 1010 index cards are reordered at page load and receive the approved display numbers.
- Existing preview filenames remain stable during testing.
- Explicit numbered chapter-link labels are normalized to the new display number while preserving their destination.
- The shared accessibility, mobile, print, and no-JavaScript stabilization remains in place.

## Content-integrity rule

The reorder changes sequence, display numbers, navigation, filenames at deployment, and numbered cross-reference labels only. It does not authorize rewriting, shortening, replacing, or expanding chapter substance.

## Final deployment verification

Before promotion to the main repository, verify:

1. renamed files and all internal links;
2. index-card and sidebar order;
3. current-page highlighting and progress persistence;
4. chapter-number references in prose and Works Consulted entries;
5. mobile layout, keyboard navigation, print output, and no-JavaScript fallback;
6. results of the inbound-link audit.