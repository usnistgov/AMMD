var removeHighlight = function() {
    var highlightClass = "highlight";

    $.each($("." + highlightClass), function(index, value) {
        $(value).removeClass(highlightClass);
    });
}

$('#explorer-panel-transparent-bgd').css({
                  'position':'fixed',
                  'top':'0px',
                  'left':'0px',
                  'width':'100%',
                  'height':'100%',
                  'display':'block',
                  'background-color':'#000',
                  'z-index':'2147483645',
                  'opacity': '0.8',
                  'filter':'alpha(opacity=80)',
                  'display':'none'
            });
$('#explore-panel-loading').css({
                  'position':'fixed',
                  'top':'50%',
                  'left':'45%',
                  'display':'block',
                  'background-color':'#000',
                  'color':'#337ab7',
                  'z-index':'2147483647',
                  'display':'none',
                  'border-style':'solid',
                  'border-color':'#337ab7'
            });

var displayLeafView = function(event) {
    event.preventDefault();
    removeHighlight();

    var nodeClasses = $(this).attr("class").split(" ");
    var documentId = nodeClasses[1];
    var nodeId = nodeClasses[2];
    var navigationId = $.urlParam("nav_id");

    console.log("Loading leaf view for " + documentId + "...");
    $(this).parents("span:first").addClass("highlight");

    $('#explorer-panel-transparent-bgd').show();
    $('#explore-panel-loading').show();

    $.ajax({
        url: "load_view",
        method: "POST",
        data: {
            nav_id: navigationId,
            doc_id: documentId,
            node_id: nodeId
        },
        success: function(data) {
            $('#explorer-panel-transparent-bgd').hide();
            $('#explore-panel-loading').hide();
            $("#explore-view-error").hide();
            $("#explore-view").html(data);

            console.log("View successfully loaded");
        },
        error: function() {
            $('#explorer-panel-transparent-bgd').hide();
            $('#explore-panel-loading').hide();
            $("#explore-view").hide();
            $("#explore-view-error").show();

            console.error("An error occured while executing load_view");
        }
    })
};

var displayBranchView = function(event) {
    event.preventDefault();
    removeHighlight();

    var nodeClasses = $(this).attr("class").split(" ");
    var nodeId = nodeClasses[1];
    var navigationId = $.urlParam("nav_id");

    console.log("Loading branch view for " + nodeId + "...");
    $(this).parents("span:first").addClass("highlight");

    $('#explorer-panel-transparent-bgd').show();
    $('#explore-panel-loading').show();
    $.ajax({
        url: "load_view",
        method: "POST",
        data: {
            nav_id: navigationId,
            node_id: nodeId
        },
        success: function(data) {
            $('#explorer-panel-transparent-bgd').hide();
            $('#explore-panel-loading').hide();
            $("#explore-view-error").hide();
            $("#explore-view").html(data);

            console.log("View successfully loaded");
        },
        error: function() {
            $('#explorer-panel-transparent-bgd').hide();
            $('#explore-panel-loading').hide();
            $("#explore-view").hide();
            $("#explore-view-error").show();

            console.error("An error occured while executing load_view");
        }
    })
};

var displayLinkView = function(event) {
    event.preventDefault();
    removeHighlight();

    var nodeClasses = $(this).attr("class").split(" ");
    var nodeId = nodeClasses[1];
    var documentId = nodeClasses[2];
    var navigationId = $.urlParam("nav_id");

    console.log("Loading link view for " + documentId + "...");

    $('#explorer-panel-transparent-bgd').show();
    $('#explore-panel-loading').show();

    $.ajax({
        url: "load_view",
        method: "POST",
        dataType: "json",
        data: {
            nav_id: navigationId,
            doc_id: documentId,
            ref_node_id: nodeId
        },
        success: function(data) {
            $("span>."+data.doc_id).parents("span:first").addClass("highlight");
            $('#explorer-panel-transparent-bgd').hide();
            $('#explore-panel-loading').hide();
            $("#explore-view-error").hide();
            $("#explore-view").html(data.html);

            console.log("View successfully loaded");
        },
        error: function() {
            $('#explorer-panel-transparent-bgd').hide();
            $('#explore-panel-loading').hide();
            $("#explore-view").hide();
            $("#explore-view-error").show();

            console.error("An error occured while executing load_view...");
        }
    })
};

$("#explore-view-error").hide();
$('#explorer-panel-transparent-bgd').hide();
$('#explore-panel-loading').hide();

$(document).on("click", ".projection", displayLeafView);
$(document).on("click", ".branch", displayBranchView);
$(document).on("click", ".link", displayLinkView);