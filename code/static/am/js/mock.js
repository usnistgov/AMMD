console.log('Mock successfully loaded!');

$(document).ready( function() {
    var waitingTime = Math.random() * 1700 + 300;
//    var waitingTime = 10;

    setTimeout(function() {
        $('#tree-details').removeClass('hide');
        $('#tree-loading').hide();

        console.log('Tree displayed');
    }, waitingTime);
});