/**
 * Created by anb22 on 1/19/17.
 */

var get_position_value = function(element) {
    var attr_id =  element.attr("id");                  // "id_form-0-is_default_1"
    attr_id = attr_id.replace("id_form-","");           // "0-is_default_1"
    attr_id = attr_id.replace("-is_default_","_");      // "0_1"
    return attr_id.split("_");                          // ['0','1']
};

var set_default = function(position) {
//    If an other default exist, set the other to not default, and, unblock the associate visible
//    Else set the associate visible to True and deactivate visible choices
    $( '.class_default' ).each( function() {
        if($(this).attr("value") == 'True' && $(this).prop("checked") == true)
        {
            var position_to_check_false = get_position_value($(this))[0];
            if(position!=position_to_check_false){
                $('input[name=form-' + position_to_check_false + '-is_default][value=False]').prop('checked', true);
                $('input[name=form-' + position_to_check_false + '-is_visible]').prop('disabled', false);
            }
        }
    });
    $('input[name=form-' + position + '-is_default][value=True]').prop('checked', true);
    $('input[name=form-' + position + '-is_visible]').prop('disabled', true);
    $('input[name=form-' + position + '-is_visible][value=True]').prop('checked', true);
};

var set_not_default = function(position) {
//    Unblock the associate visible
    $('input[name=form-' + position + '-is_default][value=False]').prop('checked', true);
    $('input[name=form-' + position + "-is_visible").prop('disabled', false);
};

var handle_default = function() {
//    Launch the appropriate action if the schema is set to default or not
    var tab_position_value = get_position_value($(this));
    var position = tab_position_value[0];
    var is_not_default = tab_position_value[1];
    if (is_not_default == 1){
        set_not_default(position);
    }
    else {
        set_default(position);
    }
};

var launch_default = function () {
//    If one of the schema is already at default, deactivate the visible option
    $( '.class_default' ).each( function() {
        if($(this).attr("value") == 'True')
        {
            if($(this).is(':checked'))
            {
                var position = get_position_value($(this))[0];
                $('input[name=form-' + position + '-is_visible]').prop('disabled', true);
                $('input[name=form-' + position + '-is_visible][value=True]').prop('checked', true);
            }
        }
    });
};

$(document).on('change', '.class_default', handle_default);

// Initialization at loading
$(document).ready(function() {
    launch_default();
});
