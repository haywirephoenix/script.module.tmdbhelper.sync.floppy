# TMDbHelper Sync - Floppy

A [TMDbHelper](https://github.com/jurialmunkey/plugin.video.themoviedb.helper) sync provider (interface version 3) for [Floppy](https://github.com/dannyvfilms/Floppy), the self-hosted media tracker.

TMDbHelper finds it automatically once installed, because the add-on ID starts with `script.module.tmdbhelper.sync.`. Floppy is not in TMDbHelper's catalogue of trusted providers, so TMDbHelper shows a third-party warning the first time you select it.

## Requirements

- TMDbHelper 6.19.0 or newer (the release with modular sync providers)
- A running Floppy instance and its API token: Floppy → Settings → Integrations → API Token

## Install

1. Install the add-on zip in Kodi: Add-ons → Install from zip file.
2. Give it your Floppy address and token, either:
   - in this add-on's settings (Add-ons → My add-ons → All → TMDbHelper Sync - Floppy → Configure), or
   - by leaving those empty and setting them in the [Floppy add-on](https://github.com/haywirephoenix/plugin.video.floppy) (`plugin.video.floppy`), whose settings are used as a fallback.
3. In TMDbHelper's settings, choose **Floppy** for history/progress, watchlist and, if you want, scrobbling.

## What it syncs

| TMDbHelper feature | From Floppy |
|---|---|
| Watched movies | Completed entries; each entry is one play |
| Watched episodes and show progress | Completed episode entries. A show's aired count is watched episodes plus Floppy's episodes left |
| Resume points | `/playback/progress` positions that are not complete |
| Next episodes | Floppy's next episode for shows in progress, paused or completed, skipping unaired ones |
| Up next (all unwatched episodes) | TMDb episodes compared against synced watched episodes |
| Watchlist | Entries with the Planning status |
| Dropped shows | Entries with the Dropped status |

Shows tracked in Floppy's separate anime library are included.

Collection is not supported yet, so TMDbHelper does not offer Floppy for it.

## Actions

- **Mark watched / unwatched**: one play per request. Seasons and shows are marked one aired episode at a time; unwatching removes every synced play.
- **Watchlist add / remove**: removing deletes only the Planning entries, so earlier watch history is kept.
- **Dropped**: sets the show's status to Dropped, or back to In progress.
- **Remove resume point**: clears the saved Floppy position.

Actions on anime-library shows pass `library_media_type=anime` so Floppy does not start tracking a second TV copy.

## Scrobbling

Start and stop are sent to Floppy's `/scrobble` endpoint with the position and duration. Floppy only infers completion near the end of a file, so the add-on sends `completed` at 80%, matching TMDbHelper's Trakt behaviour.

If the Floppy add-on (`plugin.video.floppy`) has its own scrobbling on, this provider stands down so plays are not logged twice. Turn off **Let the Floppy add-on scrobble when its scrobbling is on** in this add-on's settings to always scrobble from TMDbHelper.

## Keeping in step with other Floppy add-ons

Floppy has no last-activities endpoint, so changes are detected from each list's total and newest entry. A change that adds no new entry, such as a removal, still resyncs.

The add-on also shares the `floppy.widget_reload` Home window property with `plugin.video.floppy`:

- It sets the property after its own actions and stops, so that add-on refreshes its lists.
- It resyncs when the other add-on changes Floppy data.

## Licence

GPL-3.0-or-later. Structure adapted from [script.module.tmdbhelper.sync.mdblist](https://github.com/jurialmunkey/script.module.tmdbhelper.sync.mdblist).
