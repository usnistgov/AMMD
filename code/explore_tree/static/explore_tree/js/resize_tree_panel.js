var $exploreViewPanel = $("#explore-view").parent();

var screenSizeCut = function(percentage) {
    return $('body').width() * percentage;
};

$("#tree-panel").resizable({
    handles: "e",  // Resizable only on the x axis
    minWidth: screenSizeCut(0.15),
    maxWidth: screenSizeCut(0.70),
    resize: function(event,ui) {
    	var x = ui.element.outerWidth();
    	var $treePanel = $(ui.element);

    	$exploreViewPanel.css("margin-left", x);
    	$exploreViewPanel.css("width", screenSizeCut(1) - x);
    }
});
