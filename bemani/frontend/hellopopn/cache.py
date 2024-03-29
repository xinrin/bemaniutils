from bemani.data import Config, Data
from flask_caching import Cache
from bemani.frontend.app import app

from bemani.frontend.hellopopn.hellopopn import HelloPopnMusicFrontend

class HelloPopnMusicCache:

    @classmethod
    def preload(cls, data: Data, config: Config) -> None:
        cache = Cache(
                    app,
                    config={
                        "CACHE_TYPE": "filesystem",
                        "CACHE_DIR": config.cache_dir,
                    },
                )
        frontend = HelloPopnMusicFrontend(data, config, cache)
        frontend.get_all_songs(force_db_load=True)