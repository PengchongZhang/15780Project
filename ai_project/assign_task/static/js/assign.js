var tasksNum;
var devsNum;
var inputForm;
var estDiv = $('#estimate-input');
var voteDiv = $('#vote-input');
var introEst = $('#intro-est');
var introVote = $('#intro-vote');
var weightInput = $('#weight-input');

/**
 * check the input estimation and vote order are not empty
 * @param formData
 * @returns {boolean}
 */
function checkInputNotNull(formData) {
    for (var i = 0; i < formData.length; i++) {
        if (formData[i].value === "")
            return false;
    }
    return true;
}

/**
 * remove all text input and show the input for numbers again
 */
function cleanUpForm() {
    estDiv.empty();
    estDiv.hide();
    introEst.hide();
    voteDiv.empty();
    voteDiv.hide();
    introVote.hide();
    $('#task-number').val("");
    $('#developer-number').val("");
    $('#numbers').show();
    $('#expert-weight').val("");
    weightInput.hide();
}

function showEstRes (estimate) {
    for(var i=0; i<estimate.length; i++) {
        var task_id = i+1;
        var task_est = $('<li>').text('task ' + task_id + ": " + estimate[i]);
        $('#res-est').append(task_est);
    }
}

function showAssignRes (assignment) {
    for(var i=0; i<assignment.length; i++) {
        var dev_assign = $('<li>').text('developer ' + assignment[i]['dev_id']);
        var dev_tasks = $('<ul>');
        var tasks = assignment[i]['tasks'];
        for(var j=0; j<tasks.length; j++) {
            var task_assign = $('<li>').text('task: ' + tasks[j]['task_id'] + ' proportion: ' + tasks[j]['proportion']);
            dev_tasks.append(task_assign);
        }
        dev_assign.append(dev_tasks);
        $('#res-assign').append(dev_assign);
    }
}

function handleSolveRes (data) {
    console.log(data);
    if(!data.valid)
        return window.alert('Unable to assign task because your input is invalid!');
    // basic information
    $('#res-task-number').text(data['task_number']);
    $('#res-dev-number').text(data['developer_number']);
    $('#res-expert-weight').text(data['expert_weight']);
    $('#res-expert').text(data['expert']);
    showEstRes(data['estimate']);
    showAssignRes(data['assignment']);
    // show result
    $('#res').show();
    $('#task-form').hide();
}

$(document).ready(function () {
    inputForm = $('#task-form');

    $('#numbers-btn').unbind('click').on('click', function (e) {
        e.preventDefault();
        console.log(estDiv.children().length);
        console.log(voteDiv.children().length);
        if(estDiv.children().length !== 0 || voteDiv.children().length !== 0)
            return;
        var intro = $('#intro');
        tasksNum = $('#task-number').val();
        devsNum = $('#developer-number').val();
        if (tasksNum === "" || devsNum === "") {
            return alert('Invalid input!');
        }
        $('#numbers').hide();

        for (var i = 0; i < devsNum; i++) {  // append text input for estimation
            var estId = 'est-dev' + i;
            var estLabel = $('<label>').attr({for: estId}).text('estimation of developer' + (i + 1));
            var estInput = $('<input required>').attr({type: 'text', name: estId, id: estId});
            estDiv.append(estLabel);
            estDiv.append(estInput);
            estDiv.append($('<br>'));
        }
        estDiv.show();
        introEst.show();
        for (var j = 0; j < devsNum; j++) {  // append text input for vote order
            var voteId = 'vote-dev' + j;
            var voteLabel = $('<label>').attr({for: voteId}).text('expert order of developer' + (j + 1));
            var voteInput = $('<input required>').attr({type: 'text', name: voteId, id: voteId});
            voteDiv.append(voteLabel);
            voteDiv.append(voteInput);
            voteDiv.append($('<br>'));
        }
        voteDiv.show();
        introVote.show();
        $('#submit-btn').show();
        intro.text("Esitame the work load of " + tasksNum + " tasks for " + devsNum + " developers.");
        intro.show();
        weightInput.show();
    });

    $('#submit-btn').unbind('click').on('click', function (e) {  // solve assign task problem
        e.preventDefault();
        var formData = inputForm.serializeArray();
        if (formData === undefined || !checkInputNotNull(formData)) return alert('Invalid input!');
        var url = inputForm.attr("action");
        $.post(url, formData).done(handleSolveRes);
    });
});