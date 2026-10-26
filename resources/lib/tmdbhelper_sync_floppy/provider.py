from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.providers.base import SyncProvider
from tmdbhelper_sync_floppy.sync import synctype, datasync
from tmdbhelper_sync_floppy.actions import basic
from tmdbhelper_sync_floppy.actions.progress import ItemProgress
from tmdbhelper_sync_floppy.scrobbler import ProviderScrobbler


class Provider(SyncProvider):
    interface_version = 3
    provider_id = 'floppy'
    display_name = 'Floppy'
    sync_classes = {
        'SyncWatched': synctype.SyncWatched,
        'SyncPlayback': synctype.SyncPlayback,
        'SyncNextEpisodes': synctype.SyncNextEpisodes,
        'SyncAllNextEpisodes': synctype.SyncAllNextEpisodes,
        'SyncWatchlist': synctype.SyncWatchlist,
        'SyncHiddenDropped': synctype.SyncHiddenDropped,
        'SyncAiredEpisodes': synctype.SyncWatched,  # Aired and watched counts come with watched shows
    }
    action_classes = {
        'watched': basic.ItemWatched,
        'unwatched': basic.ItemUnwatched,
        'watchlist': basic.ItemWatchlist,
        'dropped': basic.ItemDropped,
        'progress': ItemProgress,
    }
    getter_classes = {
        'movies_to_watch': datasync.FloppySyncDataGetterAllUnHiddenMoviesToWatch,
        'shows_to_watch': datasync.FloppySyncDataGetterAllUnHiddenShowsToWatch,
        'shows_in_progress': datasync.FloppySyncDataGetterAllUnHiddenShowsInProgress,
    }
    scrobbler_class = ProviderScrobbler

    @cached_property
    def api(self):
        return self.get_api()

    def get_api(self):
        from tmdbhelper_sync_floppy.api import FloppyAPI
        return FloppyAPI()

    def is_authorized(self):
        return self.api is not None

    def get_last_activities(self):
        from tmdbhelper_sync_floppy.sync.activity import FloppyLastActivities
        data = FloppyLastActivities(self.api).data
        if not data:
            return
        return {
            item_type: {
                'watchlisted_at': data['watchlisted_at'],
                'paused_at': data['episode_paused_at' if item_type == 'episodes' else 'paused_at'],
                'watched_at': data['watched_at' if item_type == 'movies' else 'episode_watched_at'],
                'dropped_at': data['dropped_at'],
            } for item_type in ('movies', 'shows', 'seasons', 'episodes')
        }
