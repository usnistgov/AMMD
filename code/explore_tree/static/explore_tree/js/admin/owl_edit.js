
var displayEditOwlModal = function(event) {
    event.preventDefault();

    var owlId = $(this).parents("tr:first").attr("id");
    var owlName = $(this).parents("tr:first").children(":first").text();
    var owlNameNoExt = owlName.slice(0, -4);

    console.log("Editing ontology " + owlId + "...");

    $("#edit-owl-id").val(owlId);
    $("#edit-owl-name").val(owlNameNoExt);
    $("#edit-owl-modal").modal('show');
};

var editOwl = function(event) {
    event.preventDefault();

    console.log("Applying changes for ontology " + $("#edit-owl-id").val() + "...");

    $.ajax({
        url: "/admin/explore_tree/query_ontology",
        method: "POST",
        data: {
            "id": $("#edit-owl-id").val(),
            "name": $("#edit-owl-name").val()
        },
        success: function(data) {
            console.log("success")
            location.href = "";
        },
        error: function() {
            console.log("error");
        }
    })

};

$(document).on("click", ".edit-owl", displayEditOwlModal);
$(document).on("click", "#confirm-edit-owl", editOwl);