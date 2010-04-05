// based in part on http://www.nomadjourney.com/2009/01/using-django-templates-with-jquery-ajax/

function onSelectionLoad(data, xmlRequest, textStatus) {
	if (!multiUser)
		$('.selected-user').remove();
	$( '#usi_add_' + data.field ).before(xmlRequest.responseText);
	
    $( '.su-remove' ).click( function(event) {
        $(this).parent().remove()
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
    
    event.preventDefault();
	first_name = $( '#id_' + field + '-first_name' ).val();
	last_name = $( '#id_' + field + '-last_name' ).val();
    chapter = $( '#id_' + field + '-chapter' ).val();
    
    results_div = $(form).children('.usi-search-results' )[0];
	$(results_div).html( '&nbsp;' ).load(
        getUserSearchUrl(), {
            'first_name': first_name, 
            'last_name': last_name,
            'chapter': chapter,
            'field': field
        },
        onSearchResultsLoad
    );
}

function onAddSelection(event) {
    $(event.target).html($(event.target).text() == '+' ? '&ndash;' : '+');
    form = $(event.target).closest('.usi')[0];
    $(form).find('.usi-search').slideToggle();
    return false;
}

$(document).ready(function() {
    $( '.usi-search' ).hide();
    $( '.usi-submit' ).click( function(event) { onSearchSubmit(event) } );
    $( '.usi-add-link' ).click( function(event) { onAddSelection(event) } );      
});
