# Azure VM SUSE/SLES for SAP Costing with Live Pricing
# This script parses the Azure VM inventory CSV, fetches per-vCPU SUSE/SLES for SAP pricing from Azure Retail Prices API,
# and calculates the total monthly cost for all SUSE VMs (running or deallocated) in Canada Central.

import csv
import json
import requests
from collections import Counter
import os

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

# Step 1: Parse CSV and collect VM details
vm_list = []  # Each entry: {'name': ..., 'size': ..., 'vcpus': ...}
with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    # Normalize fieldnames: strip whitespace and quotes
    reader.fieldnames = [f.strip().replace('"', '') for f in reader.fieldnames]
    for row in reader:
        # Normalize keys for each row as well
        row = {k.strip().replace('"', ''): v for k, v in row.items()}
        # Handle BOM in 'NAME' field
        name_key = 'NAME'
        if name_key not in row:
            for k in row:
                if k.strip().replace('"', '').replace('\ufeff', '') == 'NAME':
                    name_key = k
                    break
        if 'suse' in row.get('OS LICENSING BENEFIT', '').lower():
            vm_name = row.get(name_key, '').strip().replace('"', '')
            vm_size = row.get('SIZE', '').strip().replace('"', '')
            vcpus = vcpu_map.get(vm_size, 0)
            vm_list.append({'name': vm_name, 'size': vm_size, 'vcpus': vcpus})

# Step 2: Fetch per-vCPU SUSE/SLES price for each VM size from Azure Retail Prices API
region = 'canadacentral'
PUBLIC_REFERENCE_PRICE = 0.15  # CAD per vCPU per hour (public reference)
per_vcpu_price = {}
sizes_needed = set(vm['size'] for vm in vm_list)

# Query Azure Retail Prices API for per-vCPU SLES for SAP pricing
for i, size in enumerate(sizes_needed):
    sku_name = size.replace('Standard_', '').replace('_', ' ')
    url = f"https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and contains(meterName, 'SLES') and contains(skuName, '{sku_name}')"
    response = requests.get(url)
    data = response.json()
    price = None
    for item in data.get('Items', []):
        if item.get('unitOfMeasure', '').lower() == '1 hour' and float(item.get('unitPrice', 0)) > 0:
            price = float(item['unitPrice'])
            break
    if price is not None:
        per_vcpu_price[size] = price
    else:
        per_vcpu_price[size] = PUBLIC_REFERENCE_PRICE

total_vcpu_cost = 0.0
# Step 3: Output table with each VM name, size, vCPUs, and monthly SUSE/SLES cost
HOURS_PER_MONTH = 730
output_rows = []

# Track if price is from API or default
header = ["VM Name", "VM Size", "vCPUs", "Per-vCPU Price (CAD/hr)", "Monthly Cost (CAD)", "Price Source"]
print(",".join(header))
total_vcpu_cost = 0.0
for vm in vm_list:
    name = vm['name']
    size = vm['size']
    vcpus = vm['vcpus']
    price_per_hour = per_vcpu_price.get(size, PUBLIC_REFERENCE_PRICE)
    price_source = "API" if price_per_hour != PUBLIC_REFERENCE_PRICE else "Default Estimator"
    monthly_cost = vcpus * price_per_hour * HOURS_PER_MONTH
    total_vcpu_cost += monthly_cost
    row = [name, size, vcpus, f"{price_per_hour:.4f}", f"{monthly_cost:.2f}", price_source]
    print(",".join(str(x) for x in row))
    output_rows.append(row)

print(f"\nTotal SUSE/SLES for SAP cost (per-vCPU model, all VMs): CAD {total_vcpu_cost:.2f}")

# Write to CSV file in same directory as input CSV
output_csv = os.path.join(os.path.dirname(csv_path), "suse_vm_costs.csv")
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(output_rows)
print(f"\nResults also written to: {output_csv}")
