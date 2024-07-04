# Lydian <!-- omit in toc -->

## You are on the `dev` branch. Switch to the `master` branch here: https://github.com/svioletg/lydian-discord-bot/tree/master <!-- omit in toc -->

Full changelog: [changelog.md](https://github.com/svioletg/lydian-discord-bot/blob/main/docs/changelog.md)

See progress on bug fixes and new features here: [Lydian Taskboard](https://github.com/users/svioletg/projects/3/views/1)

---

Lydian is a Discord music bot with support for Spotify links, written in Python. This project is licensed under GNU GPLv3 — in essence, you are free to use, modify, and distribute this source code on the conditions that your modified version is then also fully open-source, and licensed under the same terms.

If you're having problems, have a suggestion, or just have a general question, feel free to [open an issue](https://github.com/svioletg/lydian-discord-bot/issues) — you will need a GitHub account to do this. Code contributions are also welcome.

Start by downloading the `Source code (zip)` file under **Assets** from the bottom of the [latest stable release](https://github.com/svioletg/lydian-discord-bot/releases/latest) page. Extract the contents into a folder anywhere, then follow the instructions below.

---
> *Lydian was formerly [viMusBot](https://github.com/svioletg/viMusBot); its first release is what was intended to be viMusBot 2.0.0, but I decided it would be less complicated to just make a new repository since the update was practically a rewrite in many aspects. As I consider it simply a continuation of the same project, however, Lydian's first release was still marked as 2.0.0.*
>
> *If you're coming over from viMusBot, you can copy over your `spotify_config.json`, `config.yml`, and `token.txt` files and they will function the same.*

## Contents <!-- omit in toc -->

- [Setup: Python](#setup-python)
- [Setup: Required software](#setup-required-software)
- [Setup: Discord](#setup-discord)
- [Setup: Spotify API](#setup-spotify-api)
- [Running \& Updating](#running--updating)
- [Reading Logs](#reading-logs)
- [Documentation \& Guides](#documentation--guides)

## Setup: Python

Lydian needs Python in order to run. The [Python homepage](https://www.python.org/downloads) can point you to installers for Windows or MacOS, while most Linux distros should have it available in your package manager. As of writing this, the most recent major version is Python 3.12, which Lydian is being written and tested in, and thus this version is recommended.

If you're using the Windows installer, ***make sure to tick the "Add Python 3.12 to PATH" checkbox***. It may say "Add Python to enviornment variables" instead, still check the box regardless.

Next, you need to install Lydian's required packages. For a quick and automatic setup on Windows, the `create_env.bat` script is included which will automatically create a Python virtual enviornment (venv) in your Lydian folder, and install any requirements within it. `start.bat` is also included which will run the main script using the newly created venv, as well as `update.bat` which will attempt to automatically update Lydian itself and its Python dependencies. `.bat` files are run like any other program - just by double-clicking them.

Otherwise, you can install any requirements by running the command `pip install -r requirements.txt` from within your Lydian directory. Using a venv isn't required, but is recommended to keep everything self-contained.

## Setup: Required software

Lydian requires [FFmpeg and FFprobe](https://www.ffmpeg.org/) to function properly.

For **Windows**, go to [this page](https://github.com/BtbN/FFmpeg-Builds/releases) and download `ffmpeg-master-latest-win64-gpl.zip` ([direct link](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip)), attached to the top release on the page. Extract this anywhere you'd like, and move or copy `ffmpeg.exe` and `ffprobe.exe` from within the `bin` folder over to the same folder as `bot.py`.

For **Mac**, go to [this page](https://evermeet.cx/ffmpeg/) and download the archives for both `FFmpeg` and `FFprobe`. They should each have a single file within named `ffmpeg` and `ffprobe` respectively, drop them inside the same folder as `bot.py`.

For **Linux**, you can likely install it via your distro's package manger. e.g for Ubuntu, you can run `apt install ffmpeg`. This should also install `ffprobe`, try running both the `ffmpeg` and `ffprobe` commands in a terminal to ensure you have them.

If you already have FFmpeg and FFprobe added to your system's enviornment variables or PATH, then the bot will run just fine without them present in its folder.

## Setup: Discord

Go to the [Discord Developer Portal](https://discord.com/developers/applications/) and login with your Discord account. You should land on your "Applications" page — click the blue "**New Application**" button near the top right of the screen, enter a name, and hit "**Create**". The application does *not* have to be named "Lydian".

You should now be at the "General Information" page for your app. Using the left-hand sidebar, go to the "**Bot**" page. Here, you can change the username and profile picture that your bot will appear as in your server.

You should see a blue button labelled "**Reset Token**" — click it, and after confirming you'll get a new long string of random letters and numbers. Copy this string, create a new file called `token.txt` within your Lydian folder, paste your copied string into it, then save and close the file.

The last thing you'll need to do on the Discord side of things is give the bot its required permissions and "intents". Under the "Privileged Gateway Intents" section, turn **on** the switches next to "**Server Members Intent**" and "**Message Content Intent**". Below this section, you'll see a "Bot Permissions" box with many checkboxes. Lydian currently only requires the following to function:

*General Permissions*

- Read Messages/View Channels

*Text Permissions*

- Send Messages
- Send Messages in Threads
- Add Reactions

*Voice Permissions*

- Connect
- Speak

Tick the boxes next to these permissions, and then save your changes.

**To create an invite link** for the bot, click "OAuth2" on the left sidebar, then "URL Generator". Under "Scopes", tick only the "bot" checkbox. Under "Bot Permission", select the same permissions shown above. Your link will be at the bottom of this page.

## Setup: Spotify API

> *NOTE: If you want to skip setting up the Spotify API, you can skip this section. If the bot doesn't see a `spotify_config.json` file, all Spotify functionality will be safely disabled and the bot can still do everything else as usual.*

You'll need to supply an API "client ID" and "client secret" in order for Spotify-related functions to work. You will need a Spotify account, but you will **not** need a Spotify Premium subscription.

1. Start by going to your [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard). Once you're logged in and at this page, you should see a blue "**Create app**" button, which you should click.
2. Fill in the Name and Description fields with whatever you want; the "Website" field can be left blank. The Redirect URI field is required, although it will not actually be used by the bot, so you can just enter `localhost`.
3. Under "Which API/SDKs are you planning to use?", select "Web API", then hit "Save".
![Spotify app setup page](https://i.imgur.com/hoPjBKE.png)
1. You should now be sent to your app's dashboard with some graphs displayed. On the right side of the screen, click "Settings".
2. Click "View client secret" to reveal the string.
![Client ID and client secret fields](https://i.imgur.com/4AoWjWj.png)

The `spotifysetup.bat` script has been included with Lydian to set up your config automatically — if you're on Windows, you can run it, and then paste in the requested information.

Alternatively, you can manually create the required `spotify_config.json` file, and then paste in the following...

```json
{
    "spotify":
    {
        "client_id": "YOUR_ID",
        "client_secret": "YOUR_SECRET"
    }
}
```

...where `YOUR_ID` and `YOUR_SECRET` are your app's client ID and client secret respectively — make sure to keep them surrounded by quotation marks.

## Running & Updating

Lydian should now be fully equipped to run — `bot.py` is the main Python script. If you used `create_venv.bat` earlier to set up a virtual enviornment, you can use `start.bat` to run the bot within said enviornment. You can stop the bot at any time by typing `stop` into the command prompt or terminal window and hitting enter, by pressing `Ctrl` and `C` at the same time, or by closing the window.

Lydian will automatically check for new releases each time it starts. To update, run the `update.py` script, or open `update.bat`. The latter will also update the required Python packages — `update.py` will only update the bot's files, so it is recommended to manually update your packages afterwards by using `pip install -r requirements.txt`. Any changes to the required packages will be written into the changelog.

If you experience any issues with the bot, or you want a new feature added, you're free to [open a new issue](https://github.com/svioletg/lydian-discord-bot/issues) so I can look into it when possible.

## Reading Logs

Lydian stores its logs in `lydian.log`, as well as printing them out to the console window — `stdout`, to be more specific. A log will look something like this:

`[24-05-17 23:31:30] [bot.py/INFO] <module>: Logging for bot.py is now active.`

First is the current date (YY-MM-DD) and time (HH:MM:SS), followed by the file that created the log, the log's levels, and the function the log originated from. There are five levels that a log can have, depending on the importance and severity, and are largely used as such:

- `DEBUG`
  - Debug-level logs only show up in the console if they've been enabled in `config.yml`, but are still written to `lydian.log`. These usually contain more verbose and frequent information that isn't very important for most users to know in normal usage, but is very useful for diagnosing issues when things go wrong.
- `INFO`
  - Nothing of concern, usually a standard status update.
- `WARNING`
  - Used when something has occurred that isn't of immediate concern, but could *potentially* cause issues or unwanted side effects. For example, this is used when certain debugging options are enabled in your configuration that you probably don't want unless you're trying to diagnose an issue.
- `ERROR`
  - An error has occurred that has prevented the bot from completing a task, but the bot can continue running as usual afterwards. Most commonly, this can happen if media retrieval has failed in a way that was unprepared for — you should [report this error](https://github.com/svioletg/lydian-discord-bot/issues) if it keeps happening.
- `CRITICAL`
  - Only used when something of major concern has happened, and therefore should be extremely rare, ideally non-existent. If *any* logs like this appear, it should be reported right away to this repository.

## Documentation & Guides

Extra pages of information are stored inside this repository's `docs` directory. It currently contains the following:

[Changelog](https://github.com/svioletg/lydian-discord-bot/blob/main/docs/changelog.md)

[FAQ](https://github.com/svioletg/lydian-discord-bot/blob/main/docs/faq.md)

[Using `config.yml` for configuration & customization](https://github.com/svioletg/lydian-discord-bot/blob/main/docs/config.md)

[Using the Console](https://github.com/svioletg/lydian-discord-bot/blob/main/docs/console.md)
