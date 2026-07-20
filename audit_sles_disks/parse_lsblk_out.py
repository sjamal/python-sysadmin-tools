import sys
import re
import csv

def parse_ansible_output(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output = []
    current_ip = None
    current_hostname = "N/A"
    is_unreachable = False

    for i, line in enumerate(lines):
        # 1. Detect Host Start
        if " | CHANGED | " in line or " | UNREACHABLE! " in line:
            current_ip = line.split('|')[0].strip()
            is_unreachable = "UNREACHABLE!" in line
            current_hostname = "N/A"
            if is_unreachable:
                output.append({
                    "IP": current_ip, "HOSTNAME": "OFFLINE", "NAME": "N/A", 
                    "MAJ:MIN": "N/A", "SIZE": "N/A", "TYPE": "N/A", 
                    "MOUNTPOINTS": "N/A", "UUID": "N/A"
                })
            continue

        if is_unreachable: continue

        # 2. Capture Hostname (first line after header)
        clean_line = line.strip()
        if current_ip and current_hostname == "N/A" and clean_line and "NAME" not in clean_line:
            current_hostname = clean_line
            continue

        # 3. Parse lsblk Rows
        # Remove tree chars (├─, └─, │) and normalize spacing
        row_clean = re.sub(r'[├─└─│]+', '', line).strip()
        if not row_clean or "NAME" in row_clean or row_clean == current_hostname:
            continue

        parts = row_clean.split()
        if len(parts) >= 4:
            # Basic fields are positional
            name, maj_min, size, dev_type = parts[0], parts[1], parts[2], parts[3]
            
            # Mountpoints and UUIDs can be missing or swapped; we check the strings
            mount, uuid = "N/A", "N/A"
            for p in parts[4:]:
                if p.startswith('/'): mount = p
                elif '-' in p or len(p) > 10: uuid = p
            
            output.append({
                "IP": current_ip, "HOSTNAME": current_hostname, "NAME": name,
                "MAJ:MIN": maj_min, "SIZE": size, "TYPE": dev_type,
                "MOUNTPOINTS": mount, "UUID": uuid
            })

    writer = csv.DictWriter(sys.stdout, fieldnames=["IP", "HOSTNAME", "NAME", "MAJ:MIN", "SIZE", "TYPE", "MOUNTPOINTS", "UUID"])
    writer.writeheader()
    writer.writerows(output)

if __name__ == "__main__":
    if len(sys.argv) > 1: parse_ansible_output(sys.argv[1])
    else: print("Usage: python3 script.py [filename]")

