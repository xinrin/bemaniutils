# vim: set fileencoding=utf-8
import copy
from typing import Any, Dict

from bemani.backend.hellopopn.base import HelloPopnBase
from bemani.backend.ess import EventLogHandler
from bemani.common import ValidatedDict, VersionConstants, Profile
from bemani.data import Score
from bemani.protocol import Node


class HelloPopnMusic(
    EventLogHandler,
    HelloPopnBase,
):
    name = "Hello! Pop'n Music"
    version = VersionConstants.HELLO_POPN_MUSIC

    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """
        Return all of our front-end modifiably settings.
        """
        return {
            'bools': [
                {
                    'name': 'Force Song Unlock',
                    'tip': 'Force unlock all songs.',
                    'category': 'game_config',
                    'setting': 'force_unlock_songs',
                },
            ],
        }

    def handle_game_common_request(self, request: Node) -> Node:
        root = Node.void('game')

        flag = Node.void('flag')
        root.add_child(flag)

        flag.set_attribute("id", '1')
        flag.set_attribute("s1", '1')
        flag.set_attribute("s2", '1')
        flag.set_attribute("t", '1')

        root.add_child(Node.u32("cnt_music", 36))

        return root

    def handle_game_shop_request(self, request: Node) -> Node:
        root = Node.void('game')

        return root

    def handle_game_new_request(self, request: Node) -> Node:
        # profile creation
        root = Node.void('game')

        userid = self.data.remote.user.from_refid(self.game, self.version, request.attribute('refid'))

        defaultprofile = Profile(
            self.game,
            self.version,
            request.attribute('refid'),
            0,
            {
                'name': "なし",
                'chara': "0",
                'music_id': "0",
                'level': "0",
                'style': "0",
                'love': "0"
            },
        )
        self.put_profile(userid, defaultprofile)

        return root

    def handle_game_load_request(self, request: Node) -> Node:
        # Load profile values
        root = Node.void('game')

        userid = self.data.remote.user.from_refid(self.game, self.version, request.attribute('refid'))
        profile = self.get_profile(userid)

        achievements = self.data.local.user.get_achievements(self.game, self.version, userid)

        game_config = self.get_game_config()
        force_unlock_songs = game_config.get_bool("force_unlock_songs")
        # if we send all chara love as max, all songs will be unlocked
        if force_unlock_songs:
            for n in range(12):
                chara = Node.void('chara')
                chara.set_attribute('id', str(n))
                chara.set_attribute('love', "5")
                root.add_child(chara)
        else:
            # load chara love progress
            for achievement in achievements:
                if achievement.type == 'toki_love':
                    chara = Node.void('chara')
                    chara.set_attribute('id', str(achievement.id))
                    chara.set_attribute('love', achievement.data.get_str('love'))
                    root.add_child(chara)

        last = Node.void('last')
        root.add_child(last)
        last.set_attribute('chara', profile.get_str('chara'))
        last.set_attribute('level', profile.get_str('level'))
        last.set_attribute('music_id', profile.get_str('music_id'))
        last.set_attribute('style', profile.get_str('style'))

        self.update_play_statistics(userid)

        return root

    def handle_game_load_m_request(self, request: Node) -> Node:
        # Load scores
        userid = self.data.remote.user.from_refid(self.game, self.version, request.attribute('refid'))
        scores = self.data.remote.music.get_scores(self.game, self.version, userid)

        root = Node.void('game')
        sortedscores: Dict[int, Dict[int, Score]] = {}
        for score in scores:
            if score.id not in sortedscores:
                sortedscores[score.id] = {}
            sortedscores[score.id][score.chart] = score

        for song in sortedscores:
            for chart in sortedscores[song]:
                score = sortedscores[song][chart]

                music = Node.void('music')
                root.add_child(music)
                music.set_attribute('music_id', str(score.id))

                style = Node.void('style')
                music.add_child(style)
                style.set_attribute('id', "0")

                level = Node.void('level')
                style.add_child(level)

                level.set_attribute('id', str(score.chart))
                level.set_attribute('score', str(score.points))
                level.set_attribute('clear_type', str(score.data.get_int('clear_type')))

        return root

    def handle_game_save_request(self, request: Node) -> Node:
        # Save profile data
        root = Node.void('game')

        userid = self.data.remote.user.from_refid(self.game, self.version, request.attribute('refid'))
        oldprofile = self.get_profile(userid)

        newprofile = copy.deepcopy(oldprofile)

        last = request.child('last')
        newprofile.replace_str('chara', last.attribute('chara'))
        newprofile.replace_str('level', last.attribute('level'))
        newprofile.replace_str('music_id', last.attribute('music_id'))
        newprofile.replace_str('style', last.attribute('style'))
        newprofile.replace_str('love', last.attribute('love'))

        self.put_profile(userid, newprofile)

        game_config = self.get_game_config()
        force_unlock_songs = game_config.get_bool("force_unlock_songs")
        # if we were on force unlock mode, achievements will not be modified
        if force_unlock_songs is False:
            achievements = self.data.local.user.get_achievements(self.game, self.version, userid)
            chara = int(last.attribute('chara'))
            for achievement in achievements:
                if achievement.type == 'toki_love' and achievement.id == chara:
                    love = int(achievement.data["love"])
                    if love < 5:
                        self.data.local.user.put_achievement(
                            self.game,
                            self.version,
                            userid,
                            chara,
                            'toki_love',
                            {
                                'love': str(love + 1),
                            },
                        )
                        break

        return root

    def handle_game_save_m_request(self, request: Node) -> Node:
        # Score saving

        clear_type = int(request.attribute('clear_type'))
        level = int(request.attribute('level'))
        songid = int(request.attribute('music_id'))
        refid = request.attribute('refid')
        points = int(request.attribute('score'))

        userid = self.data.remote.user.from_refid(self.game, self.version, refid)

        # Pull old score
        oldscore = self.data.local.music.get_score(
            self.game,
            self.version,
            userid,
            songid,
            level,
        )

        history = ValidatedDict({})

        if oldscore is None:
            # If it is a new score, create a new dictionary to add to
            scoredata = ValidatedDict({})
            highscore = True
        else:
            # Set the score to any new record achieved
            highscore = points >= oldscore.points
            points = max(oldscore.points, points)
            scoredata = oldscore.data

        # Clear type
        scoredata.replace_int('clear_type', max(scoredata.get_int('clear_type'), clear_type))
        history.replace_int('clear_type', clear_type)

        # Look up where this score was earned
        lid = self.get_machine_id()

        # Write the new score back
        self.data.local.music.put_score(
            self.game,
            self.version,
            userid,
            songid,
            level,
            lid,
            points,
            scoredata,
            highscore,
        )

        # Save score history
        self.data.local.music.put_attempt(
            self.game,
            self.version,
            userid,
            songid,
            level,
            lid,
            points,
            history,
            highscore,
        )

        root = Node.void('game')

        return root
