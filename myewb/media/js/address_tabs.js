function onAddressUpdateSuccess(data, ui, prevLabel) {
    if(data.valid == true) {
        // Assume that the label has changed - replace the tab
        // (technically we add the "new" one first the remove the old)
        var atabs = $("#addresses").tabs();
        var index = ui.index;
        
        // Hardcoding due to possible issues if we simply try to replace an arbitrary string
        // in the auto-generated URL
        var viewUrl = getBaseAddressUrl() + data.label + "/"
        atabs.tabs('add', viewUrl, data.label, index + 1);
        
        atabs.tabs('remove', index)
    } else {
        errorList = $('#edit-address-errors-' + prevLabel);
        errorList.empty();
        if(data.label_error) {
            errorList.append('<li>Error: Label is already used</li>')
        }
        $.each(data.errors, function(i, error) {
            errorList.append('<li>' + error + '</li>')
        })
    }
}

function onAddressDeleteSuccess(data, ui) {
    if(data.valid == true) {
        var atabs = $("#addresses").tabs();
        var index = ui.index;
        atabs.tabs('remove', index)
    }
}

function onAddressTabEditPageSubmit(ui) {
    var prevLabel = $('input[name=prevLabel]', ui.panel).val();
    
    // Hardcoding due to possible issues if we simply try to replace an arbitrary string
    // in the auto-generated URL
    var editUrl = getBaseAddressUrl() + prevLabel + "/edit/"
    $.ajax({
      type: 'POST',
      url: editUrl,
      data: $('#edit-address-' + prevLabel).serialize(),
      success: function(data) {
          onAddressUpdateSuccess(data, ui, prevLabel);
      },
      dataType: "json"
    });
}

function onDeleteAddressSubmit(ui) {
    var prevLabel = $('input[name=prevLabel]', ui.panel).val();
    var deleteUrl = getBaseAddressUrl() + prevLabel + "/delete/"
    
    $.ajax({
      type: 'POST',
      url: deleteUrl,
      success: function(data) {
          onAddressDeleteSuccess(data, ui);
      },
      dataType: "json"
    });
}

function onAddressTabEditPageLoad(ui) {
    $('.editAddressSubmit').click(function() {
        onAddressTabEditPageSubmit(ui);
        return false;
    });
    
    $('.deleteAddressSubmit').click(function() {
        onDeleteAddressSubmit(ui);
        return false;
    });
}

function onAddressTabLinkClick(event, ui) {
    $(ui.panel).load(event.target.href, function() {
        onAddressTabEditPageLoad(ui);
    });
}

function onNewAddressSuccess(data, ui) {
    if(data.valid == true) {
        var atabs = $("#addresses").tabs();
        var length = atabs.tabs('length');
        
        // Hardcoding due to possible issues if we simply try to replace an arbitrary string
        // in the auto-generated URL
        var viewUrl = getBaseAddressUrl() + data.label + "/"
        
        atabs.tabs('add', viewUrl, data.label, length - 1);
    } else {
        errorList = $('#newAddressErrors');
        errorList.empty();
        if(data.label_error) {
            errorList.append('<li>' + getLabelDuplicationError() + '</li>')
        }
        $.each(data.errors, function(i, error) {
            errorList.append('<li>' + error + '</li>')
        })
    }
}

function onNewAddressSubmit(ui) {
    $.ajax({
      type: 'POST',
      url: getNewAddressUrl(),
      data: $('#new-address').serialize(),
      success: function(data) {
         onNewAddressSuccess(data, ui);
      },
      dataType: "json"
    });
}

function onAddressTabLoad(ui) {
    $('a', ui.panel).click(function(event) {
        onAddressTabLinkClick(event, ui);
        return false;
    });
    $('.newAddressSubmit').click(function() {
        onNewAddressSubmit(ui);
        return false;
    });
}

$(document).ready(function(){
    var $addressTabs = $("#addresses").tabs({
        load: function(event, ui) {
            onAddressTabLoad(ui);
        },            
        add: function(event, ui) {
            $addressTabs.tabs('select', '#' + ui.panel.id);
        },
        ajaxOptions: {success: function(r,s){}}
    });
});