$(document).ready(function(){
    $(document).on("click", ".edit-owl", displayEditOwlModal);
    $(document).on("click", "#confirm-edit-owl", editOwl);
});


var displayEditOwlModal = function(event) {
    var template_version_id = $(this).parents("tr:first").children(".template").attr("id");
    $("#edit-select-template select").val(template_version_id).change();
    $("#edit_error_div").hide();

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
            "action": "edit",
            "id": $("#edit-owl-id").val(),
            "name": $("#edit-owl-name").val(),
            "template_version_id": $("#edit-select-template select").val()
        },
        success: function(data) {
            console.log("success");
            location.href = "";
        },
        error: function(data) {
            var message = data.responseText;
            $("#edit_error_message").text(message);
            $("#edit_error_div").show();
            console.log("error");
        }
    })

};

