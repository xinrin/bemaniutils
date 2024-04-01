import re
from bemani.frontend.templates import templates_location
from bemani.frontend.static import static_location
from bemani.data import UserID
from typing import Any, Dict
from flask import Blueprint, request, Response, url_for, abort
from bemani.frontend.app import loginrequired, jsonify, render_react
from bemani.frontend.hellopopn.hellopopn import HelloPopnMusicFrontend
from bemani.frontend.types import g
from bemani.common import GameConstants

hpnm_pages = Blueprint(
    'hpnm_pages',
    __name__,
    url_prefix='/hpnm',
    template_folder=templates_location,
    static_folder=static_location,
)


@hpnm_pages.route("/scores")
@loginrequired
def viewnetworkscores() -> Response:
    # Only load the last 100 results for the initial fetch, so we can render faster
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    network_scores = frontend.get_network_scores(limit=100)

    if len(network_scores["attempts"]) > 10:
        network_scores["attempts"] = frontend.round_to_ten(network_scores["attempts"])

    return render_react(
        "Global Hello Pop'n Music Scores",
        "hpnm/scores.react.js",
        {
            "attempts": network_scores["attempts"],
            "songs": frontend.get_all_songs(),
            "players": network_scores["players"],
            "shownames": True,
            "shownewrecords": False,
        },
        {
            "refresh": url_for("hpnm_pages.listnetworkscores"),
            "player": url_for("hpnm_pages.viewplayer", userid=-1),
            "individual_score": url_for("hpnm_pages.viewtopscores", musicid=-1),
        },
    )


@hpnm_pages.route("/scores/list")
@jsonify
@loginrequired
def listnetworkscores() -> Dict[str, Any]:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    return frontend.get_network_scores()


@hpnm_pages.route('/scores/<int:userid>')
@loginrequired
def viewscores(userid: UserID) -> Response:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    info = frontend.get_latest_player_info([userid]).get(userid)
    if info is None:
        abort(404)
    scores = frontend.get_scores(userid, limit=100)

    if len(scores) > 10:
        scores = frontend.round_to_ten(scores)

    return render_react(
        "Global Hello Pop'n Music Scores",
        "hpnm/scores.react.js",
        {
            "attempts": scores,
            "songs": frontend.get_all_songs(),
            "players": {},
            "shownames": False,
            "shownewrecords": True,
        },
        {
            "refresh": url_for("hpnm_pages.listscores", userid=userid),
            "player": url_for("hpnm_pages.viewplayer", userid=-1),
            "individual_score": url_for("hpnm_pages.viewtopscores", musicid=-1),
        },
    )


@hpnm_pages.route("/scores/<int:userid>/list")
@jsonify
@loginrequired
def listscores(userid: UserID) -> Dict[str, Any]:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    return {
        "attempts": frontend.get_scores(userid),
        "players": {},
    }


@hpnm_pages.route("/topscores/<int:musicid>")
@loginrequired
def viewtopscores(musicid: int) -> Response:
    # We just want to find the latest mix that this song exists in
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    versions = sorted(
        [version for (game, version, name) in frontend.all_games()],
        reverse=True,
    )
    name = None
    artist = None

    for version in versions:
        for chart in [0, 1, 2]:
            details = g.data.local.music.get_song(GameConstants.HELLO_POPN, version, musicid, chart)
            if details is not None:
                if name is None:
                    name = details.name
                if artist is None:
                    artist = details.artist

    if name is None:
        # Not a real song!
        abort(404)

    top_scores = frontend.get_top_scores(musicid)

    return render_react(
        f"Top Hello Pop'n Music Scores for {artist} - {name}",
        "hpnm/topscores.react.js",
        {
            "name": name,
            "artist": artist,
            "players": top_scores["players"],
            "topscores": top_scores["topscores"],
        },
        {
            "refresh": url_for("hpnm_pages.listtopscores", musicid=musicid),
            "player": url_for("hpnm_pages.viewplayer", userid=-1),
        },
    )


@hpnm_pages.route("/topscores/<int:musicid>/list")
@jsonify
@loginrequired
def listtopscores(musicid: int) -> Dict[str, Any]:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    return frontend.get_top_scores(musicid)


@hpnm_pages.route('/players')
@loginrequired
def viewplayers() -> Response:

    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    return render_react(
        "All Hello Pop'n Music Players",
        'hpnm/allplayers.react.js',
        {
            'players': frontend.get_all_players()
        },
        {
            'refresh': url_for('hpnm_pages.listplayers'),
            'player': url_for('hpnm_pages.viewplayer', userid=-1),
        },
    )


@hpnm_pages.route('/players/list')
@jsonify
@loginrequired
def listplayers() -> Dict[str, Any]:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    return {
        'players': frontend.get_all_players(),
    }


@hpnm_pages.route("/players/<int:userid>")
@loginrequired
def viewplayer(userid: UserID) -> Response:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    info = frontend.get_all_player_info([userid])[userid]
    if not info:
        abort(404)
    latest_version = sorted(info.keys(), reverse=True)[0]

    return render_react(
        f'{info[latest_version]["name"]}\'s Hello Pop\'n Music Profile',
        "hpnm/player.react.js",
        {
            "playerid": userid,
            "own_profile": userid == g.userID,
            "player": info,
            "versions": {version: name for (game, version, name) in frontend.all_games()},
        },
        {
            "refresh": url_for("hpnm_pages.listplayer", userid=userid),
            "records": url_for("hpnm_pages.viewrecords", userid=userid),
            "scores": url_for("hpnm_pages.viewscores", userid=userid),
        },
    )


@hpnm_pages.route("/players/<int:userid>/list")
@jsonify
@loginrequired
def listplayer(userid: UserID) -> Dict[str, Any]:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    info = frontend.get_all_player_info([userid])[userid]

    return {
        "player": info,
    }


@hpnm_pages.route("/options")
@loginrequired
def viewsettings() -> Response:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    userid = g.userID
    info = frontend.get_all_player_info([userid])[userid]
    if not info:
        abort(404)

    return render_react(
        "Hello Pop'n Music Game Settings",
        "hpnm/settings.react.js",
        {
            "player": info,
            "versions": {version: name for (game, version, name) in frontend.all_games()},
        },
        {
            "updatename": url_for("hpnm_pages.updatename"),
        },
    )


@hpnm_pages.route("/options/name/update", methods=["POST"])
@jsonify
@loginrequired
def updatename() -> Dict[str, Any]:
    version = int(request.get_json()["version"])
    name = request.get_json()["name"]
    user = g.data.local.user.get_user(g.userID)
    if user is None:
        raise Exception("Unable to find user to update!")

    # Grab profile and update name
    profile = g.data.local.user.get_profile(GameConstants.HELLO_POPN, version, user.id)
    if profile is None:
        raise Exception("Unable to find profile to update!")
    if len(name) == 0 or len(name) > 6:
        raise Exception("Invalid profile name!")
    if (
        re.match(
            "^["
            + "\uFF20-\uFF3A"
            + "\uFF41-\uFF5A"  # widetext A-Z and @
            + "\uFF10-\uFF19"  # widetext a-z
            + "\uFF0C\uFF0E\uFF3F"  # widetext 0-9
            + "\u3041-\u308D\u308F\u3092\u3093"  # widetext ,._
            + "\u30A1-\u30ED\u30EF\u30F2\u30F3\u30FC"  # hiragana
            + "]*$",  # katakana
            name,
        )
        is None
    ):
        raise Exception("Invalid profile name!")
    profile.replace_str("name", name)
    g.data.local.user.put_profile(GameConstants.HELLO_POPN, version, user.id, profile)

    # Return that we updated
    return {
        "version": version,
        "name": name,
    }


@hpnm_pages.route("/records")
@loginrequired
def viewnetworkrecords() -> Response:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    network_records = frontend.get_network_records()
    versions = {version: name for (game, version, name) in frontend.all_games()}

    return render_react(
        "Global Hello Pop'n Music Records",
        "hpnm/records.react.js",
        {
            "records": network_records["records"],
            "songs": frontend.get_all_songs(),
            "players": network_records["players"],
            "versions": versions,
            "shownames": True,
            "showpersonalsort": False,
            "filterempty": False,
        },
        {
            "refresh": url_for("hpnm_pages.listnetworkrecords"),
            "player": url_for("hpnm_pages.viewplayer", userid=-1),
            "individual_score": url_for("hpnm_pages.viewtopscores", musicid=-1),
        },
    )


@hpnm_pages.route("/records/list")
@jsonify
@loginrequired
def listnetworkrecords() -> Dict[str, Any]:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    return frontend.get_network_records()


@hpnm_pages.route("/records/<int:userid>")
@loginrequired
def viewrecords(userid: UserID) -> Response:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    info = frontend.get_latest_player_info([userid]).get(userid)
    if info is None:
        abort(404)
    versions = {version: name for (game, version, name) in frontend.all_games()}

    return render_react(
        f'{info["name"]}\'s Hello Pop\'n Music Records',
        "hpnm/records.react.js",
        {
            "records": frontend.get_records(userid),
            "songs": frontend.get_all_songs(),
            "players": {},
            "versions": versions,
            "shownames": False,
            "showpersonalsort": True,
            "filterempty": True,
        },
        {
            "refresh": url_for("hpnm_pages.listrecords", userid=userid),
            "player": url_for("hpnm_pages.viewplayer", userid=-1),
            "individual_score": url_for("hpnm_pages.viewtopscores", musicid=-1),
        },
    )


@hpnm_pages.route("/records/<int:userid>/list")
@jsonify
@loginrequired
def listrecords(userid: UserID) -> Dict[str, Any]:
    frontend = HelloPopnMusicFrontend(g.data, g.config, g.cache)
    return {
        "records": frontend.get_records(userid),
        "players": {},
    }
