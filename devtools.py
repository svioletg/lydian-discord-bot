"""Various tools for developer usage."""

import sys
from typing import Callable

# Most modules aren't imported until needed, to save time

def yamlmd():
    """Helps to see what's missing in `config.md`"""
    import re

    import marko
    from bs4 import BeautifulSoup

    import utils.configuration as cfg

    with open('docs/config.md', 'r', encoding='utf-8') as f:
        md = BeautifulSoup(marko.convert(f.read()), 'html.parser')

    md_keys: list[str] = ['.'.join(re.findall(r"<code>(.*?)</code>", str(h))) for h in md.find_all('h3')]
    yaml_keys = cfg.CONFIG_DEFAULT_DICT.keypaths()
    difference: set[str] = set(yaml_keys) - set(md_keys)

    if not difference:
        print('No difference.')
    else:
        print('Difference:\n')
        print('\n'.join(sorted(difference)))

    print('\n')

    while True:
        match input('md = Show keys found in config.md | d = Show keys found in YAML that are NOT in config.md | e = Exit\n> ').strip().lower():
            case 'md':
                print('\n'.join(sorted(md_keys)))
                print()
            case 'd':
                print('Difference:\n')
                print('\n'.join(sorted(difference)))
                print()
            case 'e':
                raise SystemExit
            case _:
                print('Invalid option.')

TOOLS: dict[str, Callable] = {
    'yamlmd': yamlmd
}

available_tools_msg: str = '\n'.join(f'- {k}: {v.__doc__}' for k, v in TOOLS.items())

def main():
    if len(sys.argv) == 1:
        print('Need to provide a tool name. Available tools:\n')
        print(available_tools_msg)
        print('\nExiting...')
        return

    tool_name: str = sys.argv[1]

    if tool := TOOLS.get(tool_name):
        tool()
        return
    else:
        print(f'No tool named "{tool_name}". Available tools:\n')
        print(available_tools_msg)
        print('\nExiting...')
        return

if __name__ == '__main__':
    main()
