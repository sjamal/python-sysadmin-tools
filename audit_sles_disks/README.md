# SLES Disk Audit & VM Costing

Scripts to audit disk layouts on SUSE Linux Enterprise Server (SLES) VMs via Ansible-collected `lsblk` JSON output, and to estimate Azure VM costs for SLES/SAP workloads.

## Directory Structure

```
audit_sles_disks/
├── audit_data/                  # Raw JSON input — one file per host IP (from Ansible)
├── reports/                     # Generated output (gitignored — do not commit)
├── parse_lsblk_out.py           # Parse flat lsblk Ansible output → CSV
├── parse_lsblk_out_min.py       # Minimal lsblk parse (key fields only)
├── parse_lsblk_nested.py        # Parse nested lsblk JSON → CSV
├── parse_suse_vm_sizes.py       # Parse Azure VM inventory → SLES VM size summary
├── parse_suse_vm_sizes_with_pricing.py  # VM size summary with cost estimates
└── process_audit.py             # Main audit processor: JSON → final_disk_audit.csv
```

## Scripts

### `process_audit.py`
Main entry point. Reads all JSON files from `audit_data/`, classifies disks as mounted, LVM PV, systemd-managed, or orphaned, and writes `reports/final_disk_audit.csv`.

```bash
cd audit_sles_disks
python process_audit.py
```

Output fields: `IP`, `LUN`, `DEVICE`, `SIZE`, `TYPE`, `MOUNT_STATUS`, `FSTAB_ENTRY`, `LVM_PV`, `SYSTEMD_UNIT`, `LIKELY_ORPHANED`, `NOTES`

---

### `parse_lsblk_out.py`
Parses raw Ansible `lsblk` text output (non-JSON) into a structured CSV with hostname, device, size, type, mountpoints, and UUID.

```bash
python parse_lsblk_out.py <ansible_output_file>
```

---

### `parse_lsblk_out_min.py`
Minimal variant of the lsblk parser — outputs only the most relevant fields.

```bash
python parse_lsblk_out_min.py <ansible_output_file>
```

---

### `parse_lsblk_nested.py`
Parses nested `lsblk --json` output from Ansible facts into a flat CSV.

```bash
python parse_lsblk_nested.py <lsblk_json_file>
```

---

### `parse_suse_vm_sizes.py`
Reads an Azure VM inventory CSV, filters for running SLES/SAP VMs, counts each VM size, and maps to vCPU counts.

```bash
python parse_suse_vm_sizes.py
# Edit csv_path inside the script to point to your AzureVirtualMachines.csv
```

---

### `parse_suse_vm_sizes_with_pricing.py`
Extends `parse_suse_vm_sizes.py` with monthly cost estimates per VM size based on SUSE licensing and Azure compute rates.

```bash
python parse_suse_vm_sizes_with_pricing.py
```

---

## Input Data

`audit_data/` contains one JSON file per host (named `<IP>.json`), collected via Ansible. Each file holds the `lsblk` output and disk metadata for that host.

> `audit_data/` is gitignored — it contains internal IP addresses. Store and share this data outside the repo (e.g. a secure fileshare or Azure Blob Storage).

> Hosts that were unreachable during the Ansible run are recorded with `DEVICE: OFFLINE`.

## Reports (Generated — Gitignored)

All output files under `reports/` are gitignored. Run the scripts locally to regenerate them.

| File | Source Script |
|------|--------------|
| `final_disk_audit.csv` | `process_audit.py` |
| `orphaned_disk_audit.csv` | `process_audit.py` |
| `detailed_disk_report.csv` | `process_audit.py` |
| `azure_disk_report.csv` | `parse_lsblk_out.py` |
| `azure_ams_detailed_disk_report.csv` | `parse_lsblk_nested.py` |
| `azure.ams.lsblk.out.csv` | `parse_lsblk_out.py` |
| `azure.ams.lsblk.nested.out.csv` | `parse_lsblk_nested.py` |
