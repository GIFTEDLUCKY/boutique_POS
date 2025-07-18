import os

filename = "sales_cart.js"
root_dir = os.getcwd()  # current directory, your Django project root

matches = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    if filename in filenames:
        full_path = os.path.join(dirpath, filename)
        matches.append(full_path)

if matches:
    print("Found sales_cart.js at:")
    for path in matches:
        print(path)
else:
    print("sales_cart.js not found in the project directory.")
