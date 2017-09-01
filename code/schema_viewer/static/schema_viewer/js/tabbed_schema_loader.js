var render_schema = function(xsd_id, xsd_name) {
    $("#schema-viewer").html("");

    if (xsd_id === "0") {
        $("#no-schema").show();
        $("#loading-schema").hide();
        $("#error-schema").hide();
    } else {
        $("#no-schema").hide();
        $("#loading-schema").show();
        $("#error-schema").hide();

        $.ajax({
            url: "render_schema",
            method: "POST",
            data: {
                "xsd_id": xsd_id
            },
            success: function(data) {
                $("#no-schema").hide();
                $("#loading-schema").hide();
                $("#error-schema").hide();

                $("#schema-viewer").html(data);
            },
            error: function(data) {
                $("#no-schema").hide();
                $("#loading-schema").hide();
                $("#error-schema").show();
            }
        });
    }
};

// Initialization at loading
$(document).ready(function() {
    render_schema($("#schema-id").text(), $("#schema-name").text());
});
