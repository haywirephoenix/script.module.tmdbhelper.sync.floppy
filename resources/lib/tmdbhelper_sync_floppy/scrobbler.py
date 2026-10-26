from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.monitor.scrobble import ScrobbleRequest


class ProviderScrobbler(ScrobbleRequest):
    """
    Scrobble to Floppy's /scrobble endpoint
    Floppy only infers completion near the end of a file so completion is sent explicitly at 80% to match Trakt
    """

    @cached_property
    def is_floppy_plugin_scrobbling(self):
        """ plugin.video.floppy scrobbles all playback itself so defer to it rather than log plays twice """
        from tmdbhelper_sync_floppy.api import get_setting, get_floppy_plugin_setting
        return bool(get_setting('defer_scrobbling')) and get_floppy_plugin_setting('scrobble') == 'true'

    def get_scrobbler_item(self):
        if self.is_floppy_plugin_scrobbling:
            return
        player = self.player
        item = {
            'ids': {'tmdb': f'{player.tmdb_id}'},
            'position_seconds': int(player.current_time),
            'duration_seconds': int(player.total_time),
        }
        if player.tmdb_type == 'movie':
            return {**item, 'media_type': 'movie'}
        if player.tmdb_type == 'tv' and player.season >= 0 and player.episode > 0:
            return {**item, 'media_type': 'episode', 'season_number': player.season, 'episode_number': player.episode}

    def send_request(self, method, payload):
        api = self.provider.api
        postdata = {**payload, 'action': method, 'completed': self.player.progress >= 80 if method == 'stop' else None}
        return api.get_simple_api_request(
            api.get_request_url('scrobble'),
            postdata=postdata,
            headers=api.headers,
            method='json')

    def get_result(self, method, response):
        result = super().get_result(method, response)
        if result.successful and method == 'stop':
            from tmdbhelper_sync_floppy.api import set_floppy_reload
            set_floppy_reload()
        return result
