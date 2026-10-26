from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.sync.datatype import DataType, DataTypeEpisodesInShows, DataTypeShowsToEpisodes


class FloppyDataType(DataType):
    # Floppy tracks some shows in a separate anime library so shows are read from both
    floppy_media_types = {'movie': ('movie', ), 'show': ('tv', 'anime', ), 'season': ('season', ), 'episode': ('episode', )}
    record_list_class = None

    @property
    def floppy_api(self):
        return self.provider.api

    @property
    def tracking_status_param(self):
        """ Server side filter matching the client side statuses of the record list """
        try:
            return ','.join(str(i) for i in self.record_list_class.tracking_statuses)
        except TypeError:  # No status filter
            return

    @property
    def sync_args(self):
        """ Request paths for the item type """
        return tuple(('media', i, ) for i in self.floppy_media_types[self.item_type])

    @property
    def sync_kwgs(self):
        return {'source': 'tmdb', 'status': self.tracking_status_param}

    @cached_property
    def is_expired(self):
        return super().is_expired or self.is_changed_elsewhere

    @cached_property
    def is_changed_elsewhere(self):
        return self.get_is_changed_elsewhere()

    def get_is_changed_elsewhere(self):
        """ Floppy data changed by another add-on (e.g. plugin.video.floppy) since this type last synced """
        from datetime import datetime
        from tmdbhelper.lib.addon.tmdate import get_timestring_zulu
        from tmdbhelper_sync_floppy.api import get_floppy_reload
        reload_time = try_int(get_floppy_reload())
        if not reload_time or not self.timestamp:
            return False
        return get_timestring_zulu(datetime.utcfromtimestamp(reload_time)) > self.timestamp

    def get_syncitem(self, meta):
        from tmdbhelper_sync_floppy.sync.itemdata import FloppySyncItem
        return FloppySyncItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

    def get_response_sync_data(self, *args, **kwargs):
        if not self.floppy_api:
            return
        return self.floppy_api.get_paginated_results(*args, **kwargs)

    def get_response_sync_entries(self, *paths, **kwargs):
        """ Entries from every path or None if any path failed """
        results = [self.get_response_sync_data(*path, **kwargs) for path in paths]
        if None in results:
            return
        return [j for i in results for j in i]

    def get_response_sync(self, *paths, **kwargs):
        entries = self.get_response_sync_entries(*paths, **kwargs)
        if entries is None:
            return
        return self.record_list_class(entries, self.item_type).data


class FloppyDataTypeEpisodesInShows(DataTypeEpisodesInShows, FloppyDataType):
    pass


class FloppyDataTypeShowsToEpisodes(DataTypeShowsToEpisodes, FloppyDataType):
    pass
