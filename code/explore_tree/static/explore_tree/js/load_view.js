var removeHighlight = function() {
    var highlightClass = "highlight";

    $.each($("." + highlightClass), function(index, value) {
        $(value).removeClass(highlightClass);
    });
}

var displayLeafView = function(event) {
    event.preventDefault();
    removeHighlight();

    var nodeClasses = $(this).attr("class").split(" ");
    var documentId = nodeClasses[1];
    var nodeId = nodeClasses[2];
    var navigationId = $.urlParam("nav_id");

    console.log("Loading leaf view for " + documentId + "...");
    $(this).parents("span:first").addClass("highlight");

    $.ajax({
        url: "load_view",
        method: "POST",
        data: {
            nav_id: navigationId,
            doc_id: documentId,
            node_id: nodeId
        },
        success: function(data) {
            $("#explore-view-error").hide();
            $("#explore-view").html(data);

            console.log("View successfully loaded");
        },
        error: function() {
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

    $.ajax({
        url: "load_view",
        method: "POST",
        data: {
            nav_id: navigationId,
            node_id: nodeId
        },
        success: function(data) {
            $("#explore-view-error").hide();
            $("#explore-view").html(data);

            console.log("View successfully loaded");
        },
        error: function() {
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
            $("#explore-view-error").hide();
            $("#explore-view").html(data.html);

            console.log("View successfully loaded");
        },
        error: function() {
            $("#explore-view").hide();
            $("#explore-view-error").show();

            console.error("An error occured while executing load_view...");
        }
    })
};

$("#explore-view-error").hide();

$(document).on("click", ".projection", displayLeafView);
$(document).on("click", ".branch", displayBranchView);
$(document).on("click", ".link", displayLinkView);