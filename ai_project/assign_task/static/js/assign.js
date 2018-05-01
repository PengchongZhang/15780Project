var tasksNum;
var devsNum;

$(document).ready(function () {
    $('#numbers-btn').unbind('click').on('click', function (e) {
        e.preventDefault();
        tasksNum = $('#task-number').val();
        devsNum = $('#developer-number').val();
        if (tasksNum === "" || devsNum === "") {
            return alert('Invalid input!');
        }
        $('#numbers').hide();
        var estDiv = $('#estimate-input');
        var voteDiv = $('#vote-input');
        for (var i = 0; i < devsNum; i++) {
            var estId = 'est-dev' + i;
            var estLabel = $('<label>').attr({for: estId}).text('estimation of developer' + (i + 1));
            var estInput = $('<input>').attr({type: 'text', name: estId, id: estId, required: true});
            estDiv.append(estLabel);
            estDiv.append(estInput);
            estDiv.append($('<br>'));
        }
        estDiv.show();
        for (var j = 0; j < devsNum; j++) {
            var voteId = 'vote-dev' + j;
            var voteLabel = $('<label>').attr({for: voteId}).text('expert order of developer' + (j + 1));
            var voteInput = $('<input>').attr({type: 'text', name: voteId, id: voteId, required: true});
            voteDiv.append(voteLabel);
            voteDiv.append(voteInput);
            voteDiv.append($('<br>'));
        }
        voteDiv.show();
        $('#submit-btn').show();
    });

    $('#submit-btn').unbind('click').on('click', function (e) {
        e.preventDefault();
    })
});