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
