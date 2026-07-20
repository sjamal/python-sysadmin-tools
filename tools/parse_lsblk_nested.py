import sys
import re
import csv

def parse_ansible_output(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by the Ansible host header pattern
    host_blocks = re.split(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s\|.*)', content)
    
    rows = []
    
    # Iterate through blocks (header followed by its content)
    for i in range(1, len(host_blocks), 2):
        header = host_blocks[i]
        body = host_blocks[i+1]
        
        ip = header.split('|')[0].strip()       
        
        if "UNREACHABLE!" in header:
            rows.append({"IP": ip, "HOSTNAME": "OFFLINE", "NAME": "N/A", "MAJ:MIN": "N/A", "SIZE": "N/A", "TYPE": "N/A", "MOUNTPOINTS": "N/A", "UUID": "N/A"})
            continue

        lines = body.strip().split('\n')
        hostname = lines[0].strip() # First line is the S301... hostname
        
        for line in lines[1:]:
            if "NAME" in line or not line.strip(): continue
            
            # Clean the ASCII tree characters
            clean_line = re.sub(r'[├─└─│\s]+', ' ', line).strip()
            parts = clean_line.split()
            
            if len(parts) >= 4:
                # Logic: NAME, MAJ:MIN, SIZE, TYPE are 0, 1, 2, 3
                # Remaining parts are Mountpoints or UUID
                name, majmin, size, dtype = parts[0], parts[1], parts[2], parts[3]
                mount, uuid = "N/A", "N/A"
                
                for extra in parts[4:]:
                    if extra.startswith('/'): mount = extra
                    elif len(extra) > 10: uuid = extra
                
                rows.append({
                    "IP": ip, "HOSTNAME": hostname, "NAME": name,
                    "MAJ:MIN": majmin, "SIZE": size, "TYPE": dtype,
                    "MOUNTPOINTS": mount, "UUID": uuid
                })

    writer = csv.DictWriter(sys.stdout, fieldnames=["IP", "HOSTNAME", "NAME", "MAJ:MIN", "SIZE", "TYPE", "MOUNTPOINTS", "UUID"])
    writer.writeheader()
    writer.writerows(rows)

if __name__ == "__main__":
    if len(sys.argv) > 1: 
        parse_ansible_output(sys.argv[1])  # Added [1] here
    else: 
        print("Usage: python3 script.py [filename]")

