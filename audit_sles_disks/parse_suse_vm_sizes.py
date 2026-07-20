# Azure VM SUSE/SLES for SAP Costing
# Parses the Azure VM inventory CSV, filters for running VMs with SUSE/SLES for SAP,
# counts each VM size, and outputs a summary table for cost calculation.

import csv
from collections import Counter

# Path to your CSV file
csv_path = "AzureVirtualMachines.csv"

# Azure standard vCPU mapping for common VM sizes (add more as needed)
vcpu_map = {
    'Standard_B2s': 2,
    'Standard_D2s_v5': 2,
    'Standard_D2ds_v5': 2,
    'Standard_D4ds_v5': 4,
    'Standard_D4s_v5': 4,
    'Standard_D8ds_v5': 8,
    'Standard_E4ds_v5': 4,
    'Standard_E8ds_v5': 8,
    'Standard_E16ds_v5': 16,
    'Standard_E48ds_v5': 48,
    'Standard_M32ls': 32,
    'Standard_M64ls': 64,
    'Standard_M64s': 64,
    'Standard_DS2_v2': 2,
    # Add more as needed
}

vm_size_counter = Counter()
vcpu_counter = Counter()

with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if 'suse' in row['OS LICENSING BENEFIT'].lower():
            vm_size = row['SIZE'].strip()
            vm_size_counter[vm_size] += 1
            vcpus = vcpu_map.get(vm_size, 0)
            vcpu_counter[vm_size] += vcpus

print("VM Size,Count,vCPUs")
for size in vm_size_counter:
    print(f"{size},{vm_size_counter[size]},{vcpu_counter[size]}")

# User input for pricing
print("\nEnter per-VM and per-vCPU price for each VM size (leave blank if not applicable):")
per_vm_price = {}
per_vcpu_price = {}
for size in vm_size_counter:
    try:
        vm_price = input(f"Per-VM price for {size}: ")
        vcpu_price = input(f"Per-vCPU price for {size}: ")
        per_vm_price[size] = float(vm_price) if vm_price else 0.0
        per_vcpu_price[size] = float(vcpu_price) if vcpu_price else 0.0
    except Exception:
        per_vm_price[size] = 0.0
        per_vcpu_price[size] = 0.0

# Calculate totals
total_vm_cost = sum(vm_size_counter[size] * per_vm_price[size] for size in vm_size_counter)
total_vcpu_cost = sum(vcpu_counter[size] * per_vcpu_price[size] for size in vcpu_counter)

print("\nSummary:")
print("VM Size,Count,vCPUs,Per-VM Price,Per-vCPU Price,Total VM Cost,Total vCPU Cost")
for size in vm_size_counter:
    print(f"{size},{vm_size_counter[size]},{vcpu_counter[size]},{per_vm_price[size]},{per_vcpu_price[size]},{vm_size_counter[size]*per_vm_price[size]},{vcpu_counter[size]*per_vcpu_price[size]}")

print(f"\nTotal cost (per-VM model): {total_vm_cost}")
print(f"Total cost (per-vCPU model): {total_vcpu_cost}")