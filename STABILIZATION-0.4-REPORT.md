# Scholar’s Compass Shared-Shell Stabilization 0.4

## Scope

This pass stabilizes the shared chapter shell in the preview repository. It does not revise, shorten, reorder, or replace instructional chapter content.

## Shared corrections

- Skip-to-main-content link and main-content target
- Keyboard-operable chapter disclosures
- Restored white, larger, bold section-heading typography
- Consistent `Key Insight`, `Example`, and `Toolkit` callout tabs
- Additional space between callout tabs and their content
- Two-column margin-conversation cards on wider screens and one column on narrow screens
- Responsive tables and writing fields
- Mobile quick-navigation protection to prevent content obstruction
- Print rules that expose all chapter sections
- No-JavaScript fallback that leaves chapter content available

## Verification matrix

| Page | Desktop | 375 px mobile | Main/skip route | Section controls | Horizontal overflow |
|---|---|---|---|---|---|
| ENG 1010 Chapter 1 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 2 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 3 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 4 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 5 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 6 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 7 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 8 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 9 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 10 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 11 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 12 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 13 | Pass | Pass | Pass | Pass | Pass |
| ENG 1010 Chapter 14 | Pass | Pass | Pass | Pass | Pass |
| ENG 1020 Chapter 1 spot-check | Pass | Pass | Pass | Pass | Pass |
| ENG 1020 Chapter 5 spot-check | Pass | Pass | Pass | Pass | Pass |
| ENG 1020 Chapter 15 spot-check | Pass | Pass | Pass | Pass | Pass |

## Interaction checks

- First Tab stop reaches the skip link.
- Activating the skip link moves focus to `main-content`.
- Enter toggles a collapsed chapter section and updates its expanded state.
- The sidebar opens with focus on its close control, closes with Escape, and returns focus to the hamburger control.
- Chapter 1 margin-conversation cards render in two equal columns without internal overflow at desktop width.
- The callout tab reads `Key Insight` and has 64 px of top clearance before the content.
- Print media exposes all section content, including sections collapsed on screen.
- Representative ENG 1010 and ENG 1020 chapters retain visible section content when JavaScript is unavailable.

## Outside this stabilization pass

The following remain separate work packages:

- Repairing chapter-specific interactive activities that call missing JavaScript functions
- Developing the substantive Chapter 6 content
- Confirming and implementing the proposed ENG 1010 chapter order
- Consolidating the large duplicated core stylesheet

## Content-integrity statement

No chapter prose, examples, activity directions, or approved Chapter 14 definitions were changed during Stabilization 0.4.
