// based in part on http://www.nomadjourney.com/2009/01/using-django-templates-with-jquery-ajax/

function onSelectionLoad(data, xmlRequest, textStatus) {
	if (!multiUser)
		$('.selected-user').remove();
	$( '#usi_add_' + data.field ).before(xmlRequest.responseText);
	
    $( '.su-remove' ).click( function(event) {
        $(this).parent().remove()
        return false; 
    })
}

function onSearchResultSelect(event) {
    event.preventDefault();
    id_tokens = event.currentTarget.id.split('-')
    theField = id_tokens[1]
    theUsername = id_tokens[2]
    data = ({field: theField, username: theUsername});
    
    if($( '#usi_' + data.field ).children( '#su_' + data.field + '_' + data.username ).length == 0) {
        $.ajax({
            url: getUserSelectionUrl(),
            type: "POST",
            data: data,
            complete: function(xmlRequest, textStatus) {
                onSelectionLoad(data, xmlRequest, textStatus);
            }                    
        });
    }    
}

function onSearchResultsLoad(responseText, textStatus, xmlRequest) {
    $( 'a.userSearchChoice' ).unbind();     // in case click() was set previously
    $( 'a.userSearchChoice' ).click( function(event) { onSearchResultSelect(event) });
}

function onSearchSubmit(event) {
    form = $(event.target).closest('.usi-form')[0]    
    field = $(form).find('.usi-field')[0].value;
    
    //event.preventDefault();
	first_name = $( '#id_' + field + '-usi_first_name' ).val();
	last_name = $( '#id_' + field + '-usi_last_name' ).val();
    chapter = $( '#id_' + field + '-usi_chapter' ).val();
    
    //results_div = $(form).children('.usi-search-results' )[0];
    results_div = $('div.usi-search-results');
	$(results_div).html( '&nbsp;' );
	$(results_div).load(
        getUserSearchUrl(), {
            'usi_first_name': first_name, 
            'usi_last_name': last_name,
            'usi_chapter': chapter,
            'usi_field': field
        },
        onSearchResultsLoad
    );
}

function onAddSelection(event) {
    //$('.usi-add-link').html('Search for users' ? 'Close search' : 'Search for users');
    form = $(event.target).closest('.usi')[0];
    $(form).find('.usi-search').slideToggle();
    return false;
}

$(document).ready(function() {
    $( '.usi-search' ).hide();
    $( '.usi-submit' ).click( function(event) { onSearchSubmit(event); return false; } );
    $( '.usi-add-link' ).click( function(event) { onAddSelection(event); return false; } );      
});
