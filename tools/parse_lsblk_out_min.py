import sys
import re
import csv

def parse_ansible_output(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    output = []
    current_ip = None
    current_hostname = "N/A"
    is_unreachable = False

    for i, line in enumerate(lines):
        clean_line = line.strip()
        
        # Detect host start
        if " | CHANGED | " in line or " | UNREACHABLE! " in line:
            current_ip = line.split('|')[0].strip()
            is_unreachable = "UNREACHABLE!" in line
            current_hostname = "N/A"
            if is_unreachable:
                output.append({"IP": current_ip, "HOSTNAME": "OFFLINE", "DISK": "N/A", "UUID": "N/A", "MOUNT": "N/A"})
            continue

        # Skip JSON error content for unreachable hosts
        if is_unreachable:
            continue

        # Identify Hostname (usually first line after 'CHANGED' header)
        if current_ip and current_hostname == "N/A" and clean_line and "NAME" not in clean_line:
            current_hostname = clean_line
            continue

        # Skip headers and empty lines
        if not clean_line or "NAME" in clean_line or clean_line == current_hostname:
            continue

        # Parse lsblk Disk Rows
        # Remove tree characters: ├─, └─, │
        row_data = re.sub(r'[├─└─│\s]+', ' ', line).strip()
        parts = row_data.split()
        
        if len(parts) >= 4:
            name = parts[0]
            mount = "N/A"
            uuid = "N/A"
            # Extract UUID and Mount based on common formats
            for p in parts[4:]:
                if p.startswith('/'):
                    mount = p
                elif '-' in p or len(p) > 15: # UUIDs are long or hyphenated
                    uuid = p
            
            output.append({
                "IP": current_ip,
                "HOSTNAME": current_hostname,
                "DISK": name,
                "UUID": uuid,
                "MOUNT": mount
            })

    # Output to CSV
    writer = csv.DictWriter(sys.stdout, fieldnames=["IP", "HOSTNAME", "DISK", "UUID", "MOUNT"])
    writer.writeheader()
    writer.writerows(output)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_ansible_output(sys.argv[1])
    else:
        print("Usage: python3 script.py [ansible_output.txt]")

