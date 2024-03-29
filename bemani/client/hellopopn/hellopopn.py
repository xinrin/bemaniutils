import base64
import time
from typing import Optional

from bemani.client.base import BaseClient
from bemani.protocol import Node


class HelloPopnMuiscClient(BaseClient):

    NAME = "ＴＥＳＴ"

    def verify_game_shop(self)->None:
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


    def verify_game_common(self)->None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("method", "common")
        game.set_attribute("ver", "0")
        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        #self.__verify_profile(resp)

    def verify_game_new(self, loc: str, refid: str)->None:
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

    def verify_game_load(self, refid: str)->None:
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
    
    def verify_game_load_m(self, refid: str)->None:
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

    def verify_game_save_m(self, refid: str)->None:
        call = self.call_node()
        game = Node.void("game")
        call.add_child(game)
        game.set_attribute("clear_type", "2")
        game.set_attribute("level", "1")
        game.set_attribute("method", "save_m")  
        game.set_attribute("music_id", "1") 
        game.set_attribute("refid", refid) 
        game.set_attribute("score", "736000") 
        game.set_attribute("style", "0") 
        game.set_attribute("ver", "0")  

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/game/@status")

    def verify_game_save(self, loc: str , refid: str)->None:
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
            #New profile creation
            self.verify_game_new(location,ref_id)
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
        self.verify_game_save_m(ref_id)
        self.verify_game_save(location,ref_id)



