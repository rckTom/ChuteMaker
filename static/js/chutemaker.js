$("#svg").on("change", function() {
    var svg = $("#svg")
    var tiling = $("#tiling")
    tiling.prop("disabled", true);
    if (!svg.prop("checked")) {
        return;
    }

    if (tiling.prop("checked")){
        tiling.prop("checked", false);
        var collapse = $("#coltil")[0];
        var col = new bootstrap.Collapse(collapse, {toggle: false});
        col.hide()
    }
});

$("#pdf").on("change", function() {
    $("#tiling").prop("disabled", false);
});