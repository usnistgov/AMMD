var render_schema = function(xsd_id, xsd_name) {
    $("#schema-viewer").html("");
    $("#oxygen-viewer").attr("href", "#");
    $("#schema_view").attr("href", "#");

    $("#oxygen-viewer").attr("disabled", true);
    $("#oxygen-viewer").on("click", false);
    $("#download-schema").attr("disabled", true);
    $("#download-schema").on("click", false);

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

                $("#oxygen-viewer").attr("disabled", false);
                $("#oxygen-viewer").off("click", false);
                $("#download-schema").attr("disabled", false);
                $("#download-schema").off("click", false);

                $("#schema-viewer").html(data);
                $("#oxygen-viewer").attr("href", "/static/schema_viewer/oxygen/"+xsd_name+".html");
                $("#schema_view").attr("href", "tabbed?sname="+xsd_name+"&sid="+xsd_id);
            },
            error: function(data) {
                $("#no-schema").hide();
                $("#loading-schema").hide();
                $("#error-schema").show();
            }
        });
    }
}

var load_schema = function(event) {
    var xsd_id = $(this).val();
    var xsd_name = $("#schema-selector option:selected").text();

    return render_schema(xsd_id, xsd_name);
};

var switchToLastSchema = function() {
    $("#schema-selector").val($("#schema-selector").find("option:last").val());
};

$(document).on("change", "#schema-selector", load_schema);

// Initialization at loading
$(document).ready(function() {
    switchToLastSchema();
    render_schema($("#schema-selector").val(), $("#schema-selector option:selected").text());
});
