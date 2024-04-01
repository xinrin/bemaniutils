from bemani.data import Config, Data
from bemani.common import cache

from bemani.frontend.hellopopn.hellopopn import HelloPopnMusicFrontend


class HelloPopnMusicCache:

    @classmethod
    def preload(cls, data: Data, config: Config) -> None:
        frontend = HelloPopnMusicFrontend(data, config, cache)
        frontend.get_all_songs(force_db_load=True)
