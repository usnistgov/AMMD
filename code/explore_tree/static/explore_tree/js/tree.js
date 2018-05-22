var $tree = $('#tree');

// Hide initially every nodes of the exploration tree
function hideNodes(){
    var $treeElement = $('#tree');
    var $treeElement1 = ($treeElement).children()
    var $a = $('#tree').find('li');

    for (i = 0; i < $a.length; i++) {
      var $myQuery = new jQuery.fn.init($a[i], "i.fa.fa-chevron-down" );

      if(isFolder($myQuery)) {
        var $icon = $myQuery.find("i.fa:first");
        var $subtree = $myQuery.find('ul:first');

        $icon.removeClass();
        $icon.addClass("fa fa-chevron-right");
        $subtree.hide();
        }
      }
};

var isFolder = function($treeElement) {
    return $treeElement.find('ul').size() !== 0;
};

var operateTree = function($treeElement) {
    var $icon = $treeElement.find("i.fa:first");
    var $subtree = $treeElement.find('ul:first');
    $icon.removeClass();

    if($subtree.is(':hidden')) {
        $icon.addClass("fa fa-chevron-down");
        $subtree.show();
      //  console.log($subtree)
    } else {
        $icon.addClass("fa fa-chevron-right");
        $subtree.hide();
  //      console.log($subtree)
    }
};

$tree.on('click', 'li>span>i.fa', function(event) {
    event.preventDefault();
    event.stopPropagation();

    var $treeElement = $(this).parents("li:first");

    if(isFolder($treeElement)) {
        operateTree($treeElement);
    } else {

    }
});

$(window).on("scroll", function() {
    var navOffset = $("#navbar").offset();
    var navHeight = $("#navbar").height() + 1;
    var scroll = $(document).scrollTop();

    var diffX = navOffset.top + navHeight - scroll;
    console.log(diffX);

    if(diffX > 0) {
        console.log(diffX);
        $("#tree-panel").css({top: navHeight - scroll});
    } else {
        $("#tree-panel").css({top: -89});
    }

});

hideNodes();
