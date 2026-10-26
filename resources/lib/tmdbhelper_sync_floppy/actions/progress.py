from jurialmunkey.parser import try_int
from tmdbhelper_sync_floppy.actions.item import ItemSync
from tmdbhelper.lib.script.sync.progress import ItemProgress as BasicItemProgress


class ItemProgress(ItemSync, BasicItemProgress):

    def get_floppy_response(self):
        postdata = {'media_type': self.item_type, 'ids': {'tmdb': f'{self.tmdb_id}'}}
        if self.item_type == 'episode':
            postdata.update({'season_number': try_int(self.season), 'episode_number': try_int(self.episode)})
        return self.floppy_api.get_response_send('playback', 'progress', postdata=postdata, method='json_delete')
