from typing import Any, Dict, Iterator, List, Tuple
from flask_caching import Cache  # type: ignore
from bemani.backend.hellopopn import HelloPopnFactory, HelloPopnBase
from bemani.common import Profile, ValidatedDict, GameConstants
from bemani.data import Data, UserID, Attempt, Song
from bemani.frontend.base import FrontendBase


class HelloPopnMusicFrontend(FrontendBase):

    game = GameConstants.HELLO_POPN

    valid_charts: List[int] = [
        HelloPopnBase.CHART_TYPE_EASY,
        HelloPopnBase.CHART_TYPE_NORMAL,
        HelloPopnBase.CHART_TYPE_HARD,
    ]

    def __init__(self, data: Data, config: Dict[str, Any], cache: Cache) -> None:
        super().__init__(data, config, cache)
        self.machines: Dict[int, str] = {}

    def all_games(self) -> Iterator[Tuple[GameConstants, int, str]]:
        yield from HelloPopnFactory.all_games()

    def format_profile(
        self, profile: Profile, playstats: ValidatedDict
    ) -> Dict[str, Any]:
        formatted_profile = super().format_profile(profile, playstats)
        formatted_profile["plays"] = playstats.get_int("total_plays")
        formatted_profile["love"] = profile.get_str("love")
        formatted_profile["level"] = profile.get_str("level")
        return formatted_profile

    def format_attempt(self, userid: UserID, attempt: Attempt) -> Dict[str, Any]:
        formatted_attempt = super().format_attempt(userid, attempt)
        formatted_attempt["clear_type"] = attempt.data.get_int("clear_type")
        return formatted_attempt

    def format_score(self, userid: UserID, attempt: Attempt) -> Dict[str, Any]:
        formatted_score = super().format_score(userid, attempt)
        formatted_score["clear_type"] = attempt.data.get_int("clear_type")
        return formatted_score

    def format_song(self, song: Song) -> Dict[str, Any]:
        difficulties = [0, 0, 0]
        difficulties[song.chart] = song.data.get_int("difficulty", 1)

        formatted_song = super().format_song(song)
        formatted_song["category"] = song.data.get_int("category", 1)
        formatted_song["difficulties"] = difficulties
        return formatted_song

    def merge_song(self, existing: Dict[str, Any], new: Song) -> Dict[str, Any]:
        new_song = super().merge_song(existing, new)
        if existing["difficulties"][new.chart] == 0:
            new_song["difficulties"][new.chart] = new.data.get_int("difficulty", 1)
        return new_song
