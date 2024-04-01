from typing import Dict, Optional, Any

from bemani.backend.base import Base, Factory
from bemani.backend.hellopopn.hellopopn import HelloPopnMusic
from bemani.common import Model
from bemani.data import Data


class HelloPopnFactory(Factory):

    MANAGED_CLASSES = [
        HelloPopnMusic,
    ]

    @classmethod
    def register_all(cls) -> None:
        for game in ['JMP']:
            Base.register(game, HelloPopnFactory)

    @classmethod
    def create(cls, data: Data, config: Dict[str, Any], model: Model, parentmodel: Optional[Model]=None) -> Optional[Base]:

        if model.gamecode == 'JMP':
            return HelloPopnMusic(data, config, model)

        # Unknown game version
        return None
