# Accessibility audit

Audit level: **implemented-controls review and automated interaction checks; not a formal WCAG conformance certification**.

The shared 2D viewer targets WCAG 2.2 AA for the implemented controls. Source review and Playwright evidence confirm:

- one visible Japanese page title and coherent heading structure;
- semantic buttons, selects, fieldsets, tables, captions, and regions;
- skip links to main content and past the map, with focus transfer asserted in E2E;
- keyboard-selectable SVG edges, visible focus styling, and `aria-pressed` view state;
- labels for city, disabled scenario/profile/origin/destination/phase controls, and map views;
- status marks plus text and line styles, so meaning is not color-only;
- persistent static-planning disclaimer and visible source attribution;
- table alternatives for edges, sources, readiness, and gaps;
- polite live-region announcements and assertive readable error state;
- reduced-motion media rule;
- M6/profile and non-computed selectors disabled rather than pretending to operate;
- KPI null reasons and the 3D unavailable fallback exposed as readable text.

Evidence:

- UI unit tests: 27 passed.
- E2E: 17 passed; one deterministic screenshot test intentionally skipped outside the designated desktop project.
- Desktop screenshots: `reports/UI_SCREENSHOTS/`.

Remaining human checks: measured color contrast with a dedicated analyzer, screen-reader testing on Windows/macOS, zoom/reflow at 200–400%, Japanese copy review, and representative assistive-technology user testing.
