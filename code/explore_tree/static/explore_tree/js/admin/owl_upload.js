$(function () {
    'use strict';

    var initUploadForm = function() {
        $('#progress').show();
        $('#progress .progress-bar').css("width", "0%");

        $("#progress-complete").hide();
        $("#progress-error").hide();
        $("#error_div").hide();

        $("#ontology-name").val("");
        $("#ontology-id").val("");

        $("#save-owl").prop("disabled", true);
    };

    $('#fileupload')
        .fileupload({
            url: "/admin/explore_tree/upload_owl",
            dataType: 'json',
            done: function (e, data) {
                setTimeout(function() {
                     $('#progress').hide();
                     $('#progress-complete').show();
                }, 1000);

                $("#ontology-name").val(data.result.name);
                $("#ontology-id").val(data.result._id);

                $("#save-owl").prop("disabled", false);

            },
            fail: function (e, data) {
                var message = data.jqXHR.responseJSON.message;
                $("#progress-error-msg").text(message)

                setTimeout(function() {
                     $('#progress').hide();
                     $('#progress-error').show();
                }, 1000);
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $('#progress .progress-bar').css(
                    'width',
                    progress + '%'
                );
            }
        })
        .prop('disabled', !$.support.fileInput)
        .parent().addClass($.support.fileInput ? undefined : 'disabled');

    /*
     * EVENTS
     **/

    // Upload button
    $(document).on("click", ".btn#upload-owl", function(event) {
        event.preventDefault();

        initUploadForm();
        $("#upload-owl-modal").modal("show");
    });

    // Save button
    $(document).on("click", ".btn#save-owl", function(event) {
        $.ajax({
            url: "/admin/explore_tree/query_ontology",
            method: "POST",
            data: {
                "action": "create",
                "id": $("#ontology-id").val(),
                "name": $("#ontology-name").val(),
                "template_version_id": $("#id_values").val()
            },
            success: function(data) {
                console.log("success")
                location.href = "";
            },
            error: function(data) {
                var message = data.responseText;
                $("#error_message").text(message);
                $("#error_div").show();
                console.log("error");
            }
        })
    });

    // Dismiss modal
    $(document).on("hide.bs.modal", "#upload-owl-modal", function(event) {
        var owlId = $("#ontology-id").val();

        if( owlId !== "" ) {
            $.ajax({
                url: "/admin/explore_tree/query_ontology",
                method: "DELETE",
                data: {
                    "id": $("#ontology-id").val()
                },
                success: function(data) {},
                error: function() {
                    console.log("An error occured while deleting the ontology");
                }
            });
        }
    });
});
