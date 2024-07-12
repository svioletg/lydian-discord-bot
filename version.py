"""Project version for Lydian. 
The version text file should always be either a dev.X version number, or the name of a release tag.
"""
with open('version.txt', 'r', encoding='utf-8') as f:
    VERSION = f.read().strip()
