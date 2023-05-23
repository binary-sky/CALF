import re
import os

# Set the path to your directory containing Python files
path = "./"

# Regular expression to match Chinese characters
re_cn = re.compile(u'[\u4e00-\u9fa5]+')

# Loop through each Python file in the directory
for filename in os.listdir(path):
    if filename.endswith(".py"):
        # Read the file contents
        with open(path + filename, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        # Loop through each line and remove any Chinese comments
        with open(path + filename, 'w', encoding="utf-8") as f:
            for line in lines:
                if not re_cn.search(line):
                    f.write(line)