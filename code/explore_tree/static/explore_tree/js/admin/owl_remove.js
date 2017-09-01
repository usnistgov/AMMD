
var displayRemoveOwlModal = function(event) {
    event.preventDefault();

    var owlId = $(this).parents("tr:first").attr("id");
    var owlName = $(this).parents("tr:first").children(":first").text();

    $("#remove-owl-id").val(owlId);
    $("#remove-owl-name").text(owlName);
    $("#remove-owl-modal").modal("show");
};

var removeOwl = function(event) {
    event.preventDefault();
    console.log("Deleting ontology " + $("#delete-owl-id").val() + "...");

    $.ajax({
        url: "/admin/explore_tree/query_ontology",
        method: "DELETE",
        data: {
            id: $("#remove-owl-id").val()
        },
        success: function(data) {
            location.href = "";
        },
        error: function(data) {
            console.error("Impossible to remove ontology");
        }
    });

};

$(document).on("click", ".remove-owl", displayRemoveOwlModal);
$(document).on("click", "#confirm-remove-owl", removeOwl);