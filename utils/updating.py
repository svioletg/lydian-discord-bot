"""Automatic updater for the bot. Checks the locally stored version number against the latest release up on GitHub,
and replaces local files if a new version exists.
"""

# Standard imports
import os
import re
import shutil
import urllib.request
from pathlib import Path
from string import ascii_lowercase
from typing import NamedTuple, Self
from zipfile import ZipFile

# External imports
import arrow
import colorama
import requests

# Local imports
from utils.palette import Palette
from version import VERSION

colorama.init(autoreset=True)
plt = Palette(load_config=False)

class Release:
    """Organizes useful information from a GitHub API reponse of a release."""
    def __init__(self, response_json: dict):
        """
        @response_json: Dictionary retrieved from using `.json()` on a `Response`.
        """
        self.name: str = response_json['name']
        self.tag: str = response_json['tag_name']

        self.url: str = response_json['html_url']
        self.zip: str = response_json['zipball_url']
        self.tarball: str = response_json['tarball_url']

        self.is_prerelease: bool = response_json['prerelease']
        self.is_draft: bool = response_json['draft']

        self.text: str = response_json['body']
        self.date: arrow.Arrow = arrow.get(response_json['published_at'])

    @classmethod
    def from_url(cls, github_url: str) -> Self | None:
        """Creates a `Release` from a GitHub API release URL."""
        response_json = requests.get(github_url, timeout=5).json()
        if response_json.get('message', '') == 'Not Found':
            return None
        return cls(response_json)

    @classmethod
    def from_tag(cls, tag: str) -> Self | None:
        """Creates a `Release` from a tag name."""
        return cls.from_url(f'https://api.github.com/repos/svioletg/lydian-discord-bot/releases/tags/{tag}')

    @classmethod
    def get_latest_release(cls) -> Self | None:
        """Retrieves the latest release on the Lydian repository and stores it along with the detected local version.
        If no release could be found, returns `None`.
        """
        response_json = requests.get('https://api.github.com/repos/svioletg/lydian-discord-bot/releases', timeout=5).json()
        if not response_json:
            return None
        return cls(response_json[0])

def is_outdated(tag_a: str | Release, tag_b: str | Release) -> bool:
    """Checks if the first tag's release date is more recent than the second. Returns `True` if either tag does not exist."""
    release_a = Release.from_tag(tag_a) if isinstance(tag_a, str) else tag_a
    release_b = Release.from_tag(tag_b) if isinstance(tag_b, str) else tag_b
    date_a = arrow.get(release_a.date) if release_a else None
    date_b = arrow.get(release_b.date) if release_b else None
    return (date_a > date_b) if date_a and date_b else True

def main():
    print('Checking...')

    latest = Release.get_latest_release()
    local_tag = VERSION

    if local_tag[0].startswith('dev.'):
        print('Development version detected; won\'t compare to latest.')
        print('Exiting.')
        return

    if local_tag == latest.tag:
        print('You are up to date.')
        print(f'Current: {plt.lime}{local_tag}{plt.reset} = Latest: {plt.lime}{latest.tag}')
        print('Exiting.')
        return

    if is_outdated(latest.tag, local_tag):
        print('A new update is available.')
        print(f'Current: {plt.gold}{local_tag}{plt.reset} < Latest: {plt.lime}{latest.tag}')

    if input('\nUpdate now? (y/n) ').strip().lower() != 'y':
        print('Exiting.')
        return

    latest_archive = Path(f'lydian-discord-bot-{latest.tag}.zip')

    print('Retrieving: ' + latest.zip)
    urllib.request.urlretrieve(latest.zip, latest_archive)

    print('Extracting...')
    with ZipFile(latest_archive, 'r') as zipf:
        extract_destination = Path(zipf.namelist()[0])
        zipf.extractall('newupdate')

    print('Copying...')
    cwd = str(Path.cwd())
    shutil.copytree(extract_destination, cwd, dirs_exist_ok=True)

    print('Cleaning up...')
    os.remove(latest_archive)
    shutil.rmtree(extract_destination)

    with open('version.txt', 'r', encoding='utf-8') as f:
        new_version = f.read()
        print('Done!')
        print(f'You are now on: {plt.lime}v{new_version}{plt.reset}')

if __name__ == '__main__':
    main()
