
//var displayDeleteOwlModal = function(event) {
//    event.preventDefault();
//
//    var owlId = $(this).parents("tr:first").attr("id");
//    var owlName = $(this).parents("tr:first").children(":first").text();
//
//    $("#delete-owl-id").val(owlId);
//    $("#delete-owl-name").text(owlName);
//    $("#delete-owl-modal").modal("show");
//};

var deleteOwl = function(event) {
    event.preventDefault();

    var owlId = $(this).parents("tr:first").attr("id");

    console.log("Deleting ontology " + owlId + "...");

    $.ajax({
        url: "/admin/explore_tree/query_ontology",
        method: "POST",
        data: {
            id: owlId,
            status: -1
        },
        success: function(data) {
            location.href = "";
        },
        error: function(data) {
            console.error("Impossible to delete ontology");
        }
    });

};

$(document).on("click", ".delete-owl", deleteOwl);
//$(document).on("click", "#confirm-delete-owl", deleteOwl);