"""
Script to create products.csv from the provided data
Save this as create_products_csv.py and run it once to create the products.csv file
"""
import csv
import os

# Create Util directory if it doesn't exist
if not os.path.exists('utils'):
    os.makedirs('utils')

# Product data from your CSV
products_data = {
    'Product': ['Aladdin', 'Bhavana', 'Chathumi', 'Dilan', 'Eshan', 'Lahiru', 'Malith', 
                'Nishan', 'Oshadi', 'Pasindu', 'Ravindu', 'Sanduni', 'Tharuka', 'Udesh', 
                'Menaka', 'Kusuma', 'Amali', 'Kalpana', 'Nethmi', 'Sahan'],
    'Sitagliptin Tablets BP 50 mg': [3, 1, 5, 0, 3, 2, 3, 1, 2, 4, 2, 3, 0, 0, 2, 1, 0, 1, 0, 2],
    'Loratadine Tablets USP 10 mg': [3, 3, 4, 3, 2, 3, 0, 2, 0, 4, 3, 1, 1, 0, 4, 4, 4, 3, 3, 4],
    'Gabapentin Capsules USP 300 mg': [1, 3, 1, 1, 2, 1, 5, 1, 3, 4, 4, 5, 5, 2, 0, 3, 2, 1, 1, 3],
    'Bisoprolol Tablets BP 5 mg': [2, 3, 1, 4, 3, 5, 2, 0, 2, 0, 5, 5, 0, 4, 3, 0, 5, 1, 4, 1],
    'Nimodipine Tablets BP 30 mg': [4, 4, 2, 3, 0, 1, 5, 0, 3, 5, 4, 4, 3, 3, 4, 1, 3, 3, 4, 1],
    'Mefenamic Acid Tablets BP 500 mg': [5, 1, 1, 5, 5, 5, 5, 0, 3, 1, 2, 0, 1, 3, 1, 3, 1, 2, 2, 1],
    'Rosuvastatin Tablets IP 10 mg': [2, 0, 2, 1, 2, 3, 0, 1, 5, 3, 2, 0, 1, 0, 3, 1, 2, 2, 5, 2],
    'Tramadol Capsule IP 50 mg': [2, 2, 3, 2, 1, 2, 2, 1, 5, 2, 0, 5, 1, 4, 3, 3, 2, 3, 3, 2]
}

# Write to CSV
csv_path = 'utils/products.csv'

with open(csv_path, 'w', newline='', encoding='utf-8') as file:
    # Get all product names (column headers)
    product_names = list(products_data.keys())
    
    writer = csv.writer(file)
    
    # Write header row
    writer.writerow(product_names)
    
    # Write data rows
    num_workers = len(products_data['Product'])
    for i in range(num_workers):
        row = []
        for product_name in product_names:
            row.append(products_data[product_name][i])
        writer.writerow(row)

print(f"Created {csv_path} successfully!")
print(f"Workers: {len(products_data['Product'])}")
print(f"Products: {len(products_data) - 1}")  # -1 for 'Product' column