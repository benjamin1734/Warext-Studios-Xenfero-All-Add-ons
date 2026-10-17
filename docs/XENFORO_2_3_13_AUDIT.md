# XenForo 2.3.13 — Warext Studios static audit (2026-10-17)

All twelve add-on repositories are checked from their current GitHub `main` branches using the workflow in `.github/workflows/xenforo-2.3.13-static-audit.yml`. The workflow validates PHP 8.4 syntax, XenForo minimum-version declarations, XML exports and extension-to-PHP file mappings. It publishes a Markdown artifact.

**This is not a claim of live XenForo compatibility.** XenForo 2.3.13 is commercial software. The check does not run a licensed core installation or compare proprietary template bodies/method signatures.

Live verification checklist:
1. Install each Release ZIP on a fresh **licensed XenForo 2.3.13** instance with PHP 8.4, then upgrade an existing install without wiping any data.
2. Verify ACP navigation, permissions, routes, cron/jobs, alerts, moderator reports and uninstall/upgrade migrations.
3. Check template modification anchor results, especially `PAGE_CONTAINER`, `editor`, `thread_view`, `post_macros`, profile menus and Resource Manager integration.
4. Verify shared AI provider, browser editor behavior, bulk moderation workflows and Minecraft Vote webhook/NuVotifier delivery with test secrets.
5. Verify generated Release ZIP contains correct `upload/`, `addon.json`, `_data` and no outdated staging files.

Static compatibility corrections tracked for the October audit: Referral 1.2.1, Turkish Writing 1.1.1, Thread Freshness 1.2.4, AI Content Inspector 1.2.1, Portfolio 1.2.3, and the central catalog's User Content Manager version 1.1.1.

## 2026-10-17 performance pass

- **Portfolio v1.2.4:** tag synchronization uses batched normalized-tag lookups, grouped use-count aggregation, a bulk orphan-map removal and a transaction, with fake-database regression checks for shared tags and deletion.
- **Thread Freshness v1.2.5:** alternative suggestions load candidates as one finder batch, preloading forum relations and retaining visibility/order semantics; repository regression tests cover order and permissions.
- **Minecraft Vote v1.2.3:** added a vote-date/server ranking aggregation index to new installs and an upgrade step for existing installs; NuVotifier queued deliveries preload the Server relation; release regression checks validate both paths.

No synthetic speedup percentage is claimed: production-scale SQL EXPLAIN, database benchmarks and licensed XenForo 2.3.13 runtime tests are still outstanding.

- **Bug Reporting v1.2.2:** pre-normalizes the incoming description once per candidate batch rather than repeating Unicode normalization for up to 30 reports; a regression also corrected the decomposed Turkish capital İ behavior in text matching. CI + Release passed.
