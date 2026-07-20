# Roadmap

Planned scripts for infrastructure auditing, system health checks, and operational data analysis.

---

## In Progress

_Nothing currently active._

---

## Planned

### Host & System Auditing

- [ ] **memory_audit.py** — Parse `/proc/meminfo` or `free -m` output across multiple hosts (via Ansible JSON output) and report total, used, available, and swap per host. Flag hosts below configurable thresholds.
- [ ] **process_audit.py** — Identify top CPU and memory consumers per host from `ps aux` output. Useful for baseline comparison before and after changes.
- [ ] **service_status_checker.py** — Read a list of expected services per host role and verify running state via `systemctl` output. Report missing or failed services.
- [ ] **cron_auditor.py** — Collect all crontab entries across system and user cron directories. Output a unified schedule table sorted by user and frequency.
- [ ] **open_ports_auditor.py** — Parse `ss -tlnp` or `netstat` output and compare against an expected ports whitelist per host role. Flag unexpected listeners.

### Access & Identity

- [ ] **ssh_key_auditor.py** — Enumerate `~/.ssh/authorized_keys` entries across user home directories. Report key age (if stored), key type, and whether the key matches a known inventory.
- [ ] **sudo_rules_auditor.py** — Parse `/etc/sudoers` and `/etc/sudoers.d/` files across hosts. Summarise which users/groups have elevated access and flag broad rules (e.g. `ALL=(ALL) NOPASSWD: ALL`).
- [ ] **user_account_auditor.py** — Compare `/etc/passwd` and `/etc/group` entries against a managed user list. Report unmanaged accounts, locked accounts, and accounts with shells.

### Capacity & Inventory

- [ ] **swap_usage_monitor.py** — Track swap usage trends across hosts and flag systems with sustained high swap utilisation. Pairs with `disk_growth_forecaster.py` in `python-machine-learning`.
- [ ] **package_inventory.py** — Parse `rpm -qa` or `dpkg --list` output and generate a normalised package inventory per host. Useful for patch compliance and EOL tracking.
- [ ] **patch_compliance_checker.py** — Compare installed package versions against a known-good baseline or CVE list. Output a compliance gap report per host.

### Reporting

- [ ] **host_summary_report.py** — Aggregate outputs from multiple audit scripts into a single per-host summary Markdown or HTML report. Designed for scheduled reporting pipelines.
- [ ] **drift_detector.py** — Compare two audit snapshots (before/after a change window) and output a structured diff of changed values across all audited dimensions.

---

## Ideas / Backlog

- Ansible facts parser: extract and normalise `ansible -m setup` JSON output for bulk querying
- Certificate expiry monitor: scan all cert files on hosts and report those expiring within N days
- Systemd unit file linter: validate unit files against a set of hardening best practices

---

## Notes

- Scripts should accept Ansible-style JSON inventory output as input where applicable.
- All audit scripts should support `--output json|csv|markdown` for pipeline composability.
- No live host connections from within scripts — all inputs are pre-collected data files.
