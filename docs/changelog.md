# Lydian / Changelog

## 2.0.0

> *2024.mm.dd / dev.34*

Developer
- Docstrings have been added to most functions, classes, and modules
- Any instances of `import regex as re` have been replaced with `import re`
- `customlog.py` has been removed entirely, logging is now handled using the [`colorlog`](https://pypi.org/project/colorlog/) library ([vMB #73](https://github.com/svioletg/viMusBot/issues/73))
    - Therefore, logs are no longer marked as `verbose` with a keyword argument, and instead use standard logging levels. Most logs that used `verbose` have been moved to `DEBUG`-level logs, but some have been deemed `INFO`-level instead
- Changes in `bot.py`:
    - `on_error` client event added to handle non-command-related errors, finally
    - No longer have to use `try/except` blocks for 404 errors resulting from editing/deleting messages, the issue was that the reference variables weren't getting properly set to `None` when `some_message.delete()` was called, so the reference pointed to nothing
    - `duration_from_url()` and `title_from_url()` removed, any functions related to URL caching removed, now irrelevant
    - `-test` debug command added
    - `-reload` debug command removed
    - `-analyze` command removed
    - `debugctx` variable and `-dctx` command removed, test commands will grab a `Context` object automatically
    - `console()` renamed to `console_thread()` for consistency with `bot_thread()`
    - Many `global` statements have been removed, various variables moved into separate cogs or classes where relevant
    - Cogs have been moved into separate files, located in `cogs/` ([vMB #72](https://github.com/svioletg/viMusBot/issues/72))
        - `common.py` created in this directory to house methods and configuration options shared between cogs
            - Functions moved into this module include: `is_command_enabled()`, `command_aliases()`, `embedq()`, `timestamp_from_seconds()`, `prompt_for_choice()`
                - `embedq()` no longer uses `*args`, now has proper keyword arguments — `title` (`str`; main, largest text), `subtext` (`str`; shown below `title` in smaller font), and `color` (`int`)
        - `General` cog moved into `cog_general.py`
        - `Voice` cog moved into `cog_voice.py`, along with most functions and classes related to voice connection and audio playback ([vMB #76](https://github.com/svioletg/viMusBot/issues/76)); other changes have been made within this file, such as...
            - `INACTIVITY_TIMEOUT` renamed to `INACTIVITY_TIMEOUT_MINS`
            - `play_item()` moved here and renamed to `make_and_start_player()`
            - `advance_queue()` moved here
            - `QueueItem`'s class method `generate_from_list()` renamed to `from_list()`
            - `MediaQueue` no longer keeps track of multiple queues per Discord server and instead represents just a single queue (part of [vMB #52](https://github.com/svioletg/viMusBot/issues/52))
                - It also now contains things like `now_playing`, `last_played`, `is_looping` (formerly `loop_this`), etc.
- `utils/` directory added to contain helper modules
    - `updater.py` moved to this directory
        - `Release` class created to organize response information and easily check versions
        - `get_latest_tag()` renamed to `get_latest_release()`
    - `miscutil.py` created in this directory to house general-purpose utility methods that should be shared between modules
    - `configuration.py` created in this directory to reduce the amount of duplicated code regarding configuration across this project
        - This module has a `get()` function that automatically retrieves the default value if none is set in the custom configuration, this removes the need for every single file to have the key typed out twice, e.g. `config.get('allow-spotify-playlists', config_default['allow-spotify-playlists'])`, and can now just be `config.get('allow-spotify-playlists')`
        - Now contains variables set and typed from every relevant configuration key, which other modules should use by importing the entire module
    - `spoofy.py` renamed to `media.py`, moved to this directory ([vMB #42](https://github.com/svioletg/viMusBot/issues/42))
    - Changes in `media.py`:
        - The `client_id` and `client_secret` supplied to the Spotify API are now just the string literals `'none'`, turns out it doesn't actually need to be valid to access what the bot was accessing
        - `FORCE_NO_MATCH` renamed to `FORCE_MATCH_PROMPT`
        - `DURATION_LIMIT` renamed to `DURATION_LIMIT_SECONDS`
        - Removed `get_uri()`, normal URLs work in all `Spotipy` functions being used so there was no need for this
        - `MediaInfo` class added to standardize expected results and improve typing ([vMB #67](https://github.com/svioletg/viMusBot/issues/67))
            - This class largely just acts as a category for three sub-classes: `TrackInfo`, `AlbumInfo`, and `PlaylistInfo`
        - `pytube_track_data()` and `trim_track_data()` removed, made unnecessary by the addition of `MediaInfo`
        - `MediaError` class extending from `Exception` added as a container for media-specific errors; it contains the following sub-classes:
            - `MediaFormattingError` - an exception used for incorrect or unexpected `MediaInfo` formatting
            - `LocalFileError` - raised when attempting to instance `TrackInfo` with a local / user-uploaded file on a service like Spotify
        - `search_ytmusic()` renamed to `match_ytmusic_track()`
            - All arguments have been replaced with a single `src_info` argument, which takes a `TrackInfo` object
        - `search_ytmusic_album()` renamed to `match_ytmusic_album()`
            - Arguments also replaced with `src_info` argument, which takes an `AlbumInfo` object
        - `spotify_track()`, `spotify_album()`, and `spotify_playlist()` all removed, replaced by a `from_spotify_url()` class method for each applicable MediaInfo sub-class
        - `spyt()` removed, now unnecessary
    - `palette.py` moved to this directory
        - `file` attribute removed from `Palette` as individual modules no longer get their own color (see below at Other -> Config changes)
        - `module` attribute added to `Palette`, represents the color of any module filenames in logs

Features
- A "roulette mode" has been added, which if enabled with the `-roulette` command (which will flip the switch by default, or you can explicitly use `-roulette on` or `-roulette off`) will choose a random song to play from the current queue each time a song finishes, rather than going in order like normal
- "Now playing" messages will now show the track's thumbnail in its embed ([vMB #70](https://github.com/svioletg/viMusBot/issues/70))
- Multiple messages are prefixed with relevant emoji to act as status icons
- `-faq` command added to get the bot's FAQ page
- `-issues` command added to the get the bot's issues page
- User configuration will now be checked and validation on startup, to catch surface-level issues and warn of them or exit the script if it would not be able to continue

Fixes
- Using the `stop` console command will now suppress the resulting `CancelledError`
- Properly fixed an issue with 404 errors when trying to edit or delete bot messages

Other
- `-analyze` command removed
- `spotify_config.json` no longer needed
- Config changes:
    - Default value of `use-top-match` set to `no`
    - Default value of `command-blacklist` now set to `test` alone
    - Default aliases for `join`, `loop`, and `move` removed
    - `force-no-match` renamed to `force-match-prompt` for clarity
    - `spotify-playlist-limit` removed, `playlist-track-limit` and `album-track-limit` added in its place (limit applies to any source now)
    - `use-url-cache` removed
    - `clearcache` entry in `aliases` removed
    - `play-history-max` (int) has been added
    - In `logging-options`:
        - `show-console-logs`, `show-verbose-logs`, and `ignore-logs-from` have all been removed
        - `console-log-level` (boolean) has been added
        - `log-full-tracebacks` (boolean) has been added
        - `colors`:
            - The color entries for filenames like `bot-py` have been removed, `module` added in their place, all files/modules will be shown as the same color if colored console logs are enabled
- Changes in `requirements.txt`:

```diff
+   ADDED: colorlog        == 6.8.2*
+ UPDATED: aioconsole      == 0.7.1
+ UPDATED: discord.py      == 2.4.0
+ UPDATED: python-benedict == 0.33.2
+ UPDATED: requests        == 2.32.2
+ UPDATED: spotipy         == 2.24.0
+ UPDATED: yt_dlp          == 2024.7.2
+ UPDATED: ytmusicapi      == 1.7.4
- REMOVED: regex
```

\**The version requirement for `colorlog` is actually [my fork](https://github.com/svioletg/python-colorlog) of the module, which just allows for directly using escape codes and not only relying on color name strings, so that how colors were handled previously in logs can be compatible.*

- `envsetup.bat` now runs `py -3` instead of `py`, to make sure the latest version of Python is being used

---

> *Pre-2.0.0 version history can be found at the original [viMusBot](https://github.com/svioletg/viMusBot/blob/master/docs/changelog.md) repository page.*

---

## Versioning Info

### Public Release Versions
Versions are numbered as X.Y.Z, where:
- X is reserved for big, fundamental structural changes to the code, and is almost never increased; these changes will always be, as far as developers are concerned, **almost completely** backwards-incompatible
- Y represents a "major version", typically coinciding with new features, or a very large number of bugfixes / internal improvements
- Z is the "minor version", usually just representing handfuls of bugfixes or small improvements/additions

### Hotfix Versions
Hotfixes are different from normal releases in that they *replace* their respective version's release instead of simply adding onto the list. This is normally done for security vulnerabilities, or for any issues in the original version that completely prevent usage of the bot. Hotfixes simply add a letter to the end of their version number, e.g 1.8.3's first hotfix was 1.8.3a, its second hotfix became 1.8.3b, and so on. If a hotfix is released, it is usually recommended to update right away.

### Development Versions
The `dev` branch is used for tracking work on new versions, and its code is never considered stable or suitable for general usage. When new versions are being worked on, a separate version system is used — in this case, a single incrementing number is used for each new version being worked on. Public release version numbers are usually decided right upon their release, and the scope of an update may change drastically, so one number is used instead of trying to predict the next public version number. `1.0.0` would have been `dev.1` although this system wasn't in place at that time, and `1.8.3` was `dev.32`, as an example.

## Release Note Categories
Each release will contain categories for its changes, which are:

### Developer
Changes that are generally only relevant to developers; internal changes, performance improvements, renamed or moved symbols, etc.

### Features
All-new functionality not previously present in the project.

### Fixes
Bugs or other unintended behavior that have been fixed.

### Other
Any changes that do not directly fit into any other category.

### Notes
Usually unused, any additional notes regarding the release. Listed last, out of alphabetical order.
