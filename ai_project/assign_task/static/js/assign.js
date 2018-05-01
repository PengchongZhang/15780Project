var tasksNum;
var devsNum;
var inputForm;

function checkInputNotNull (formData) {
    for (var i=0; i<formData.length; i++) {
        if (formData[i].value === "")
            return false;
    }
    return true;
}

$(document).ready(function () {
    inputForm = $('#task-form');

    $('#numbers-btn').unbind('click').on('click', function (e) {
        e.preventDefault();
        var intro = $('#intro');
        tasksNum = $('#task-number').val();
        devsNum = $('#developer-number').val();
        if (tasksNum === "" || devsNum === "") {
            return alert('Invalid input!');
        }
        $('#numbers').hide();
        var estDiv = $('#estimate-input');
        var voteDiv = $('#vote-input');
        for (var i = 0; i < devsNum; i++) {  // append text input for estimation
            var estId = 'est-dev' + i;
            var estLabel = $('<label>').attr({for: estId}).text('estimation of developer' + (i + 1));
            var estInput = $('<input required>').attr({type: 'text', name: estId, id: estId});
            estDiv.append(estLabel);
            estDiv.append(estInput);
            estDiv.append($('<br>'));
        }
        estDiv.show();
        for (var j = 0; j < devsNum; j++) {  // append text input for vote order
            var voteId = 'vote-dev' + j;
            var voteLabel = $('<label>').attr({for: voteId}).text('expert order of developer' + (j + 1));
            var voteInput = $('<input required>').attr({type: 'text', name: voteId, id: voteId});
            voteDiv.append(voteLabel);
            voteDiv.append(voteInput);
            voteDiv.append($('<br>'));
        }
        voteDiv.show();
        $('#submit-btn').show();
        intro.text("Esitame the work load of " + tasksNum + " tasks for " + devsNum + " developers.");
        intro.show();
    });

    $('#submit-btn').unbind('click').on('click', function (e) {  // solve assign task problem
        e.preventDefault();
        var formData = inputForm.serializeArray();
        if (formData === undefined || !checkInputNotNull(formData))  return alert('Invalid input!');
        var url = inputForm.attr("action");
        $.post(url, formData).done(function (data) {
            console.log(data);
        });
    });
});