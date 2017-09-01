var downloadSchema = function(event) {
    event.preventDefault();

    // var xsd_id = $("#schema-selector").val();
    var xsd_id = $("#id_schema").val();
    location.href = "download_schema?schema_id=" + xsd_id;
};

$(document).on("click", "#download-schema", downloadSchema);