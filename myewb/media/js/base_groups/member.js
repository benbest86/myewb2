$(document).ready(function() {
    if (!$('#id_is_admin' ).val()) {
        $('#div_id_admin_title').hide();
        $('#div_id_replists').hide();
    }
    
    $('#id_is_admin' ).click(function() {
        if ($('#id_is_admin').val())
        {
            $('#div_id_admin_title').fadeIn();
            $('#div_id_replists').fadeIn();
        }
        else
        {
            $('#div_id_admin_title').fadeOut();
            $('#div_id_replists').fadeOut();
        }
    });
});
