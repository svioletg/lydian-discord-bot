# Lydian / FAQ

Firstly, check the [issues page](https://github.com/svioletg/lydian-discord-bot/issues) to see if your problem has already been reported or solved. Most bugs are kept track of there — this page is only for issues that I cannot seem to fix, and require workarounds.

## How can Lydian support Spotify links if its audio is protected by DRM?

Lydian does not *directly* extract and play audio from a given Spotify link, there's no capability in the API to do so - instead, it gets the metadata from a Spotify track, and uses it to find the best possible match on YouTube Music (or standard YouTube, if the former fails).

## How can I change my bot's prefix, or set any other options?

Configuration is set using YAML: `config_default.yml` lists out every "key" you can change and their default values, this file is used as a fallback and should not be edited. To override any of these settings, create a `config.yml` file within your Lydian directory if it's not already present, and write in any key (using the same structure as seen in the default file) with the value you want. For more in-depth information on every key, see [config.md](https://github.com/svioletg/lydian-discord-bot/blob/main/docs/config.md).
