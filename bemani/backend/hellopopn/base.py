from typing import Optional
from typing_extensions import Final
from bemani.backend.base import Base
from bemani.backend.core import CoreHandler, CardManagerHandler, PASELIHandler
from bemani.common import GameConstants, ValidatedDict
from bemani.protocol import Node


class HelloPopnBase(CoreHandler, CardManagerHandler, PASELIHandler, Base):
    """
    Base game class for all Hello Pop'n Music versions. Handles common functionality for
    getting profiles based on refid, creating new profiles, looking up and saving
    scores.
    """

    game = GameConstants.HELLO_POPN

    # Chart type, as saved into/loaded from the DB, and returned to game
    CHART_TYPE_EASY: Final[int] = 0
    CHART_TYPE_NORMAL: Final[int] = 1
    CHART_TYPE_HARD: Final[int] = 2
