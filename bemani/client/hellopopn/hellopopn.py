import random
import time
from typing import Any, Dict, Optional

from bemani.client.base import BaseClient
from bemani.protocol import Node


class HelloPopnMuiscClient(BaseClient):

    def verify_game_shop(self) -> None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("accuracy", "0")
        game.set_attribute("area", "13")
        game.set_attribute("boot", "51")
        game.set_attribute("coin", "01.01.--.--.01")
        game.set_attribute("country", "JP")
        game.set_attribute("diff", "3")
        game.set_attribute("first", "1")
        game.set_attribute("ip", "127.0.0.1")
        game.set_attribute("is_paseli", "0")
        game.set_attribute("latitude", "0")
        game.set_attribute("lineid", ".")
        game.set_attribute("locid", "JP-7")
        game.set_attribute("loctype", "0")
        game.set_attribute("longitude", "0")
        game.set_attribute("mac", "1:2:3:4:5")
        game.set_attribute("method", "shop")
        game.set_attribute("name", ".")
        game.set_attribute("open_flag", "1")
        game.set_attribute("pay", "0")
        game.set_attribute("region", "JP-13")
        game.set_attribute("soft", "JMP:J:A:A:2014122500")
        game.set_attribute("softid", "1000")
        game.set_attribute("stage", "1")
        game.set_attribute("time", "90")
        game.set_attribute("ver", "0")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/game/@status")

    def verify_game_common(self) -> None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("method", "common")
        game.set_attribute("ver", "0")
        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/game/@status")
        self.assert_path(resp, "response/game/flag/@id")
        self.assert_path(resp, "response/game/flag/@s1")
        self.assert_path(resp, "response/game/flag/@s2")
        self.assert_path(resp, "response/game/flag/@t")
        self.assert_path(resp, "response/game/cnt_music")

    def verify_game_new(self, loc: str, refid: str) -> None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("locid", loc)
        game.set_attribute("method", "new")
        game.set_attribute("refid", refid)
        game.set_attribute("ver", "0")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/game/@status")

    def verify_game_load(self, refid: str) -> None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("method", "load")
        game.set_attribute("refid", refid)
        game.set_attribute("ver", "0")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/game/last/@chara")
        self.assert_path(resp, "response/game/last/@level")
        self.assert_path(resp, "response/game/last/@music_id")
        self.assert_path(resp, "response/game/last/@style")

    def verify_game_load_m(self, refid: str) -> None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("method", "load_m")
        game.set_attribute("refid", refid)
        game.set_attribute("ver", "0")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/game/@status")

        # Grab scores
        scores: Dict[int, Dict[int, int]] = {}
        clears: Dict[int, Dict[int, int]] = {}
        for child in resp.child("game").children:
            if child.name != "music":
                continue
            score_data = child.child("style").child("level")
            musicid = child.attribute("music_id")
            chart = score_data.attribute("id")
            score = score_data.attribute("score")
            clear_type = score_data.attribute("clear_type")

            if musicid not in scores:
                scores[musicid] = {}
            if musicid not in clears:
                clears[musicid] = {}

            scores[musicid][chart] = score
            clears[musicid][chart] = clear_type

        return {
            "scores": scores,
            "clears": clears,
        }

    def verify_game_save_m(self, refid: str, score: Dict[str, Any]) -> None:
        call = self.call_node()

        # Construct node
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("clear_type", score["clear_type"])
        game.set_attribute("level", score["chart"])
        game.set_attribute("method", "save_m")
        game.set_attribute("music_id", score["id"])
        game.set_attribute("refid", refid)
        game.set_attribute("score", score["score"])
        game.set_attribute("style", "0")
        game.set_attribute("ver", "0")

        # Swap with server
        resp = self.exchange("", call)
        self.assert_path(resp, "response/game/@status")

    def verify_game_save(self, loc: str , refid: str) -> None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("locid", loc)
        game.set_attribute("method", "save")
        game.set_attribute("refid", refid)
        game.set_attribute("ver", "0")
        last = Node.void("last")
        game.add_child(last)
        last.set_attribute("chara", "1")
        last.set_attribute("level", "1")
        last.set_attribute("love", "1")
        last.set_attribute("music_id", "1")
        last.set_attribute("style", "0")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/game/@status")

    def verify(self, cardid: Optional[str]) -> None:
        # Verify boot sequence is okay
        self.verify_services_get(
            expected_services=[
                "cardmng",
                "dlstatus",
                "eacoin",
                "facility",
                "lobby",
                "local",
                "message",
                "package",
                "pcbevent",
                "pcbtracker",
                "pkglist",
                "posevent",
                "ntp",
                "keepalive",
            ]
        )
        paseli_enabled = self.verify_pcbtracker_alive()
        self.verify_package_list()
        self.verify_message_get()
        location = self.verify_facility_get()
        self.verify_pcbevent_put()
        self.verify_game_shop()
        self.verify_game_common()

        # Verify card registration and profile lookup
        if cardid is not None:
            card = cardid
        else:
            card = self.random_card()
            print(f"Generated random card ID {card} for use.")

        if cardid is None:
            self.verify_cardmng_inquire(card, msg_type='unregistered', paseli_enabled=paseli_enabled)
            self.verify_pcbevent_put()
            ref_id = self.verify_cardmng_getrefid(card)
            if len(ref_id) != 16:
                raise Exception(f'Invalid refid \'{ref_id}\' returned when registering card')
            if ref_id != self.verify_cardmng_inquire(card, msg_type='new', paseli_enabled=paseli_enabled):
                raise Exception(f'Invalid refid \'{ref_id}\' returned when querying card')
            # New profile creation
            self.verify_game_new(location, ref_id)
        else:
            print("Skipping new card checks for existing card")
            ref_id = self.verify_cardmng_inquire(card, msg_type='query', paseli_enabled=paseli_enabled)

        # Verify pin handling and return card handling
        self.verify_cardmng_authpass(ref_id, correct=True)
        self.verify_cardmng_authpass(ref_id, correct=False)

        if ref_id != self.verify_cardmng_inquire(card, msg_type='query', paseli_enabled=paseli_enabled):
            raise Exception(f'Invalid refid \'{ref_id}\' returned when querying card')
        self.verify_game_load(ref_id)
        self.verify_game_load_m(ref_id)
        if cardid is None:
            # verify score saving
            for phase in [1, 2]:
                if phase == 1:
                    dummyscores = [
                        # An okay score on a chart
                        {
                            "id": "1",
                            "chart": "1",
                            "clear_type": "1",
                            "score": "813144",
                        },
                        # A good score on an easier chart of the same song
                        {
                            "id": "1",
                            "chart": "0",
                            "clear_type": "4",
                            "score": "1000000",
                        },
                        # A bad score on a hard chart
                        {
                            "id": "35",
                            "chart": "2",
                            "clear_type": "1",
                            "score": "590523",
                        },
                        # A terrible score on an easy chart
                        {
                            "id": "28",
                            "chart": "0",
                            "clear_type": "1",
                            "score": "1",
                        },
                    ]
                    # Random score to add in
                    songid = str(random.randint(1, 35))
                    chartid = str(random.randint(0, 2))
                    clear_type = str(random.randint(1, 4))
                    score = str(random.randint(0, 1000000))
                    dummyscores.append(
                        {
                            "id": songid,
                            "chart": chartid,
                            "clear_type": clear_type,
                            "score": score,
                        }
                    )
                if phase == 2:
                    dummyscores = [
                        # A better score on the same chart
                        {
                            "id": "1",
                            "chart": "1",
                            "clear_type": "3",
                            "score": "950144",
                        },
                        # A worse score on another same chart
                        {
                            "id": "1",
                            "chart": "0",
                            "clear_type": "1",
                            "score": "672381",
                            "expected_score": "1000000",
                            "expected_clear": "4",
                        },
                    ]

                for dummyscore in dummyscores:
                    self.verify_game_save_m(ref_id, dummyscore)
                    # Sleep so we don't end up putting in score history on the same second
                    time.sleep(1)
            scores = self.verify_game_load_m(ref_id)
            for expected in dummyscores:
                newscore = scores["scores"][expected["id"]][expected["chart"]]
                newclear = scores["clears"][expected["id"]][expected["chart"]]
                if "expected_score" in expected:
                    expected_score = expected["expected_score"]
                else:
                    expected_score = expected["score"]
                if "expected_clear" in expected:
                    expected_clear = expected["expected_clear"]
                else:
                    expected_clear = expected["clear_type"]
                if newscore != expected_score:
                    raise Exception(
                        f'Expected a score of \'{expected_score}\' for song \'{expected["id"]}\' chart \'{expected["chart"]}\' but got score \'{newscore}\''
                    )
                if newclear != expected_clear:
                    raise Exception(
                        f'Expected a medal of \'{expected_clear}\' for song \'{expected["id"]}\' chart \'{expected["chart"]}\' but got medal \'{newclear}\''
                    )

        else:
            print("Skipping score checks for existing card")

        self.verify_game_save(location, ref_id)
