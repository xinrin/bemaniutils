/*** @jsx React.DOM */


var network_scores = createReactClass({

    getInitialState: function (props) {

        return {
            songs: window.songs,
            attempts: window.attempts,
            players: window.players,
            loading: true,
            offset: 0,
            limit: 10,
            open: false,
        };
    },

    componentDidMount: function () {
        this.refreshScores();
    },

    refreshScores: function () {
        AJAX.get(
            Link.get('refresh'),
            function (response) {
                this.setState({
                    attempts: response.attempts,
                    players: response.players,
                    loading: false,
                });
                // Refresh every 15 seconds
                setTimeout(this.refreshScores, 15000);
            }.bind(this)
        );
    },

    convertChart: function (chart) {
        switch (chart) {
            case 0:
                return 'Easy';
            case 1:
                return 'Normal';
            case 2:
                return 'Hard';
            default:
                return 'u broke it';

        }
    },

    convertClearType: function (chart) {
        switch (chart) {
            case 1:
                return 'Failed...';
            case 2:
                return 'Clear!!';
            case 3:
                return 'Full Combo!!';
            case 4:
                return 'Perfect!';
            default:
                return 'unknown';

        }
    },


    

    render: function () {

        return (
            <div>
                <table className="list attempts">
                    <thead>
                        <tr>
                            {window.shownames ? <th>Name</th> : null}
                            <th>Timestamp</th>
                            <th>Song / Artist</th>
                            <th>Difficulty</th>
                            <th>Result</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.state.attempts.map(function (attempt, index) {
                            if (index < this.state.offset || index >= this.state.offset + this.state.limit) {
                                return null;
                            }

                            return (
                                <tr>
                                    {window.shownames ? <td><a href={Link.get('player', attempt.userid)}>{
                                        this.state.players[attempt.userid].name
                                    }</a></td> : null}
                                    <td>
                                        <div>
                                            <Timestamp timestamp={attempt.timestamp} />
                                            {window.shownewrecords && attempt.raised ?
                                                <span className="raised">new high score!</span> :
                                                null
                                            }
                                        </div>
                                    </td>
                                    <td className="center">
                                        <a href={Link.get('individual_score', attempt.songid)}>
                                            <div className="songname">{this.state.songs[attempt.songid].name}</div>
                                            <div className="songartist">{this.state.songs[attempt.songid].artist}</div>
                                        </a>
                                    </td>
                                    <td className="center">
                                        <div>
                                            {this.convertChart(attempt.chart)}
                                        </div>
                                        
                                    </td>
                                    <td className="center">{this.convertClearType(attempt.clear_type)}</td>
                                    <td className="center">{attempt.points}</td>
                                </tr>
                            );
                        }.bind(this))}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan={7}>
                                {this.state.offset > 0 ?
                                    <Prev onClick={function (event) {
                                        var page = this.state.offset - this.state.limit;
                                        if (page < 0) { page = 0; }
                                        this.setState({ offset: page });
                                    }.bind(this)} /> : null
                                }
                                {(this.state.offset + this.state.limit) < this.state.attempts.length ?
                                    <Next style={{ float: 'right' }} onClick={function (event) {
                                        var page = this.state.offset + this.state.limit;
                                        if (page >= this.state.attempts.length) { return }
                                        this.setState({ offset: page });
                                    }.bind(this)} /> :
                                    this.state.loading ?
                                        <span className="loading" style={{ float: 'right' }}>
                                            <img
                                                className="loading"
                                                src={Link.get('static', window.assets + 'loading-16.gif')}
                                            /> loading more scores...
                                        </span> : null
                                }
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    },
});

ReactDOM.render(
    React.createElement(network_scores, null),
    document.getElementById('content')
);