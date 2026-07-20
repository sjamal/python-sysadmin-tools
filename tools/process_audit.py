import json
import csv
import os

def process():
    data_dir = "./audit_data"
    output_file = "final_disk_audit.csv"
    headers = [
        "IP", "LUN", "DEVICE", "SIZE", "TYPE", 
        "MOUNT_STATUS", "FSTAB_ENTRY", "LVM_PV", 
        "SYSTEMD_UNIT", "LIKELY_ORPHANED", "NOTES"
    ]
    
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} directory not found.")
        return

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for filename in os.listdir(data_dir):
            if not filename.endswith(".json"): continue
            with open(os.path.join(data_dir, filename), 'r') as jf:
                try:
                    host_data = json.load(jf)
                    ip = filename.replace(".json", "")
                    if host_data.get('unreachable'):
                        writer.writerow({"IP": ip, "DEVICE": "OFFLINE"})
                        continue

                    raw_payload = json.loads(host_data['stdout'])
                    fstab = raw_payload.get('fstab', "")
                    lvm = raw_payload.get('lvm', "")
                    systemd = raw_payload.get('systemd', "")

                    def get_all_status(dev):
                        """Recursively check if device or any children are mounted."""
                        all_mounts = dev.get('mountpoints', [])
                        children = dev.get('children', [])
                        for child in children:
                            if get_all_status(child)['is_active']:
                                all_mounts.append("CHILD_ACTIVE")
                        
                        is_active = any(m and m != 'null' for m in all_mounts)
                        return {"is_active": is_active, "uuid": dev.get('uuid', "")}

                    for block in raw_payload['lsblk']['blockdevices']:
                        res = get_all_status(block)
                        lun = block.get('hctl', '?:?:?:?').split(':')[-1]
                        
                        is_active = res['is_active']
                        dev_name = block['name']
                        dev_uuid = res['uuid']

                        # Logic checks
                        in_fstab = "YES" if (dev_name in fstab or (dev_uuid and dev_uuid in fstab)) else "NO"
                        is_lvm = "YES" if dev_name in lvm else "NO"
                        in_systemd = "YES" if (dev_name + ".mount") in systemd else "NO"

                        # Orphan Logic:
                        # 1. NOT ACTIVE but exists in CONFIG (fstab/lvm/systemd) -> ORPHANED
                        # 2. NOT ACTIVE and NOT in CONFIG -> GHOST (Attached but unused)
                        likely_orphaned = "NO"
                        notes = ""
                        
                        if not is_active:
                            if in_fstab == "YES" or is_lvm == "YES" or in_systemd == "YES":
                                likely_orphaned = "YES"
                                notes = "Configured but not mounted (Check /xfr use case)"
                            else:
                                likely_orphaned = "MAYBE"
                                notes = "Ghost disk: Attached to Azure but no OS config found"
                        else:
                            notes = "In use"

                        writer.writerow({
                            "IP": ip,
                            "LUN": lun,
                            "DEVICE": dev_name,
                            "SIZE": block['size'],
                            "TYPE": block.get('type', 'disk'),
                            "MOUNT_STATUS": "ACTIVE" if is_active else "NOT MOUNTED",
                            "FSTAB_ENTRY": in_fstab,
                            "LVM_PV": is_lvm,
                            "SYSTEMD_UNIT": in_systemd,
                            "LIKELY_ORPHANED": likely_orphaned,
                            "NOTES": notes
                        })

                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    print(f"✅ Audit complete! Open {output_file} and filter LIKELY_ORPHANED = YES")

if __name__ == "__main__":
    process()

