# Python SysAdmin Tools

A collection of production-ready Python utilities for system administration, infrastructure auditing, and operational analytics. Designed for DevOps and SysAdmin teams managing complex IT environments.

## Features

- **Disk Auditing** — Parse and analyze Linux block device configurations, identify storage issues, and generate compliance reports
- **VM Sizing Analysis** — Extract SUSE VM specifications and correlate with pricing data
- **Data Processing** — Format transformation and analysis tools for infrastructure data
- **Enterprise-Grade** — Built for enterprise infrastructure at scale

## Tools

### Disk & Storage Analysis

#### `parse_lsblk_out.py`
Parse standard `lsblk` output and generate structured reports on disk partitioning and device hierarchies.

```bash
lsblk > devices.txt
python tools/parse_lsblk_out.py devices.txt
```

#### `parse_lsblk_nested.py`
Handle nested disk configurations with hierarchical device relationships (useful for complex LVM/RAID setups).

```bash
lsblk > devices.txt
python tools/parse_lsblk_nested.py devices.txt
```

#### `parse_lsblk_out_min.py`
Minimal parser for lightweight processing and integration into pipeline scripts.

```bash
lsblk | python tools/parse_lsblk_out_min.py
```

### VM & Sizing Analysis

#### `parse_suse_vm_sizes.py`
Extract SUSE VM instance specifications from cloud provider metadata.

```bash
python tools/parse_suse_vm_sizes.py
```

#### `parse_suse_vm_sizes_with_pricing.py`
Correlate VM sizes with pricing data for cost analysis and budgeting.

```bash
python tools/parse_suse_vm_sizes_with_pricing.py
```

### Data Processing

#### `process_audit.py`
Aggregate and transform audit data from multiple sources into standardized formats for reporting.

```bash
python tools/process_audit.py --source audit_data/ --output reports/
```

### Full Audit Suite

#### `audit_sles_disks/`
Complete disk auditing pipeline including:
- Multi-format device parsing
- Disk capacity tracking
- Orphaned partition detection
- Nested/complex storage hierarchy analysis
- Report generation with timestamps

See [audit_sles_disks/README.md](audit_sles_disks/README.md) for detailed documentation.

## Installation

### Requirements
- Python 3.8+
- Standard library only (no external dependencies for core tools)

### Setup

```bash
git clone https://github.com/sjamal/python-sysadmin-tools.git
cd python-sysadmin-tools
pip install -r requirements.txt  # If using optional dependencies
```

## Usage Examples

### Audit a system's disk configuration
```bash
# Capture current device state
lsblk > current_state.txt

# Parse and analyze
python tools/parse_lsblk_out.py current_state.txt > disk_report.json

# Track changes over time
python tools/process_audit.py --baseline baseline.json --current current.json --report diff_report.md
```

### Cost analysis for VM deployments
```bash
# Analyze instance sizing and pricing
python tools/parse_suse_vm_sizes_with_pricing.py --region us-east-1 --output cost_analysis.csv
```

## Use Cases

- **Infrastructure Auditing** — Regular compliance checks and capacity planning
- **Migration Planning** — Analyze storage requirements before cloud migrations
- **Cost Optimization** — Correlate VM sizes with actual pricing for budget forecasts
- **Automated Reporting** — Integrate into CI/CD pipelines for infrastructure health dashboards
- **Change Tracking** — Compare infrastructure state across time periods

## Output Formats

Tools generate output in multiple formats for integration with downstream systems:
- JSON (machine-readable, structured)
- CSV (spreadsheet-compatible, reporting)
- Markdown (human-readable reports)
- YAML (infrastructure-as-code compatible)

## Development

### Project Structure
```
.
├── tools/                          # Reusable utility scripts
│   ├── parse_lsblk_out.py         # Standard parser
│   ├── parse_lsblk_nested.py      # Hierarchical parser
│   ├── parse_suse_vm_sizes.py     # Instance sizing
│   └── process_audit.py            # Audit aggregation
└── audit_sles_disks/               # Full audit suite
    ├── README.md
    ├── tasks/                      # Ansible playbooks for data collection
    ├── audit_data/                 # Sample audit outputs
    └── reports/                    # Generated reports
```

### Adding New Tools

1. Create script in `tools/` directory
2. Ensure it accepts stdin/stdout for pipeline integration
3. Include docstring with usage examples
4. Add to relevant section in this README

## Best Practices

- **Idempotency** — Tools can be safely re-run without side effects
- **Minimal Dependencies** — Core functionality uses only Python stdlib
- **Format Flexibility** — Input/output formats designed for pipeline chaining
- **Logging** — All tools support verbose logging for debugging
- **Error Handling** — Graceful degradation with informative error messages

## License

[See LICENSE file](LICENSE)

## Contributing

Contributions welcome! Please ensure:
- [ ] Scripts follow the style conventions in existing tools
- [ ] New tools include usage documentation
- [ ] Code works with Python 3.8+ and minimal dependencies
- [ ] Changes are tested with sample data included in repo

## See Also

- [ansible/disk_reports](https://github.com/sjamal/ansible) — Ansible playbooks for collecting raw audit data
- [python](https://github.com/sjamal/python) — Broader Python utilities collection
- [hybrid-governance-automation](https://github.com/sjamal/hybrid-governance-automation) — Enterprise automation framework that can invoke these tools

## Questions?

Open an issue or submit a PR. This is an active project receiving regular updates.
