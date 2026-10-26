from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.script.sync.provider import ItemSync as ProviderItemSync


class FloppyResponses:
    """ Combine the responses of several Floppy requests made for one sync action """

    def __init__(self, responses):
        self.responses = responses

    @cached_property
    def failed(self):
        return [i for i in self.responses if not i]

    @cached_property
    def status_code(self):
        try:
            return self.failed[0].status_code
        except AttributeError:  # No response
            return 0
        except IndexError:  # All succeeded
            return self.responses[-1].status_code

    def __bool__(self):
        return bool(self.responses) and not self.failed


class ItemSync(ProviderItemSync):
    floppy_media_types = {'movie': 'movie', 'show': 'tv', 'season': 'tv', 'episode': 'tv'}

    @cached_property
    def floppy_api(self):
        return self.sync_provider.api

    @cached_property
    def is_available(self):
        return self.get_is_available()

    def get_is_available(self):
        return bool(self.floppy_api)

    def get_self(self):
        if not self.is_available:
            return
        return super().get_self()

    @cached_property
    def floppy_media_type(self):
        return self.floppy_media_types[self.item_type]

    @cached_property
    def media_path(self):
        return ('media', self.floppy_media_type, 'tmdb', self.tmdb_id, )

    def get_episode_path(self, season, episode):
        return (*self.media_path, season, 'episodes', episode, )

    @cached_property
    def library_media_type(self):
        return self.get_library_media_type()

    def get_library_media_type(self):
        """ Shows tracked in the Floppy anime library must name it or Floppy tracks a second TV copy """
        if self.floppy_media_type != 'tv':
            return
        if self.floppy_api.get_response_json(*self.media_path).get('tracked'):
            return
        if self.floppy_api.get_response_json(*self.media_path, library_media_type='anime').get('tracked'):
            return 'anime'

    def get_floppy_send(self, *args, postdata=None, method='json'):
        """ Send to Floppy within the library tracking this item """
        if self.library_media_type and postdata is not None:
            postdata = {**postdata, 'library_media_type': self.library_media_type}
        return self.floppy_api.get_response_send(
            *args, postdata=postdata, method=method,
            library_media_type=self.library_media_type)

    def get_floppy_json(self, *args):
        return self.floppy_api.get_response_json(*args, library_media_type=self.library_media_type)

    def get_floppy_response(self):
        raise NotImplementedError

    @busy_decorator
    def get_sync_response(self):
        if not self.is_available:
            return
        return self.get_floppy_response()

    def reset_lastactivities(self):
        super().reset_lastactivities()
        if not self.is_successful_sync:
            return
        from tmdbhelper_sync_floppy.api import set_floppy_reload
        set_floppy_reload()
