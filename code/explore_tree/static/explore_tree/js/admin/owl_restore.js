var restoreOwl = function(event) {
    event.preventDefault();

    var owlId = $(this).parents("tr:first").attr("id");

    console.log("Restoring ontology " + owlId + "...");

    $.ajax({
        url: "/admin/explore_tree/query_ontology",
        method: "POST",
        data: {
            id: owlId,
            status: 0
        },
        success: function(data) {
            location.href = "";
        },
        error: function(data) {
            console.error("Impossible to restore ontology");
        }
    });

};

$(document).on("click", ".restore-owl", restoreOwl);