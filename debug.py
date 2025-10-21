import data

print("\n=== Current Products ===")
print(f"Total: {len(data.PRODUCTS)}")
print("Products:", data.PRODUCTS)

print("\n=== Product Skills Structure ===")
for product_name, workers in data.PRODUCT_SKILLS.items():
    print(f"\n{product_name}:")
    for worker, skill in list(workers.items())[:3]:  # Show first 3 workers
        print(f"  - {worker}: {skill}")