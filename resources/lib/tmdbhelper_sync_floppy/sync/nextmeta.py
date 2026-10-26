from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.sync.nextmeta import SyncNextEpisodeItem, SyncAllNextEpisodesMetaItem, SyncAllNextEpisodesMeta
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory


class FloppySyncBaseView:
    """ Every TMDb episode of a show grouped by season in the layout read by SyncNextEpisodeItem """

    def __init__(self, tmdb):
        self.tmdb = tmdb

    @cached_property
    def baseview_factory(self):
        return BaseViewFactory('flatseasons', 'tv', self.tmdb)

    @cached_property
    def data(self):
        return {'seasons': self.seasons}

    @cached_property
    def seasons(self):
        seasons = {}
        for i in self.baseview_factory.data:
            number = i['params']['season']
            season = seasons.setdefault(number, {'number': number, 'episodes': []})
            season['episodes'].append({'number': i['params']['episode']})
        return list(seasons.values())


class FloppySyncNextEpisodeItem(SyncNextEpisodeItem):

    reset_at = None  # Floppy does not track rewatch resets

    def is_next_episode(self, season, episode):
        return self.get_next_episode_id(season['number'], episode['number']) not in self.watched_episode_ids

    @cached_property
    def response(self):
        if not self.tmdb_id:
            return {}
        return FloppySyncBaseView(self.tmdb_id).data


class FloppySyncAllNextEpisodesMetaItem(SyncAllNextEpisodesMetaItem):
    """ Compares TMDb episodes against synced watched episodes and returns flat Floppy sync records """

    sync_item_class = FloppySyncNextEpisodeItem

    def get_item(self, item_id):
        tmdb_type, tmdb_id, season_number, episode_number = item_id.split('.')
        return {
            'type': 'episode',
            'tmdb_id': try_int(tmdb_id),
            'season_number': try_int(season_number),
            'episode_number': try_int(episode_number),
            'upnext_episode_id': item_id,
        }


class FloppySyncAllNextEpisodesMeta(SyncAllNextEpisodesMeta):
    meta_item_getter = FloppySyncAllNextEpisodesMetaItem

    def get_watched_episode_ids(self):
        sd = self.main.instance_syncdata.get_all_episode_playcounts_getter()
        return frozenset(i['id'] for i in sd.items if i['plays'])

    def get_item_queue(self):
        self.watched_episode_ids = self.get_watched_episode_ids()
        return super().get_item_queue()

    def get_items(self, item):
        meta_item = self.meta_item_getter(self.main, item)
        meta_item.sync.watched_episode_ids = self.watched_episode_ids
        return meta_item.data
