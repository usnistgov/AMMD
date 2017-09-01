
var displayActivateOwlModal = function(event) {
    event.preventDefault();

    var owlId = $(this).parents("tr:first").attr("id");

    $("#activate-owl-id").val(owlId);
    $("#activate-owl-modal").modal('show');
};

var activateOwl = function(event) {
    event.preventDefault();
    console.log("Activating ontology " + $("#activate-owl-id").val() + "...");

    $.ajax({
        url: "/admin/explore_tree/query_ontology",
        method: "POST",
        data: {
            id: $("#activate-owl-id").val(),
            status: 1
        },
        success: function(data) {
            location.href = "";
        },
        error: function(data) {
            console.error("Impossible to activate ontology");
        }
    });
};


$(document).on("click", ".activate-owl", displayActivateOwlModal);
$(document).on("click", "#confirm-activate-owl", activateOwl);