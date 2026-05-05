import os

"""
Script to generate a list of file names to be used in the frontend.
"""

files = []
folders = os.listdir("./")
folders.sort()
for folder in folders:
    if not os.path.isdir(folder):
        continue
    print(folder)
    folder_files = []
    for file in os.listdir(folder):
        folder_files.append(file)
    files.append(folder_files)

print(files)
