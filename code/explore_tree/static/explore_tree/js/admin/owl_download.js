var downloadOwl = function(event) {
    event.preventDefault();

    var owlId = $(this).parents("tr:first").attr("id");
    location.href = "/admin/explore_tree/download_owl?owl_id=" + owlId;
};

var downloadBlankOwl = function(event) {
    event.preventDefault();
    location.href = "/admin/explore_tree/download_owl";
};

$(document).on("click", ".download-owl", downloadOwl);
$(document).on("click", "#download-blank", downloadBlankOwl);