        $(document).ready(function() {
            
            $('.group-subsection').hide();
            $('.group-subsection:first').show()
            
            $('#groupheader a[href*=#]').each(function() {
                $(this).click(function() {
                    $('.group-subsection').each(function() {
                        $(this).hide();
                    });
                    $('#groupheader li').each(function() {
                        $(this).removeClass('current');
                    });
                    
                    
                    console.log($(this).attr('href'));
                    $('#div-'+ $(this).attr('href').substring(1)).show();
                    $(this).parent().addClass('current');
                    
                    //document.location.hash = $(this).attr('href');
                    
                    //return false;
                    
                    
                });
            });
            
            //{# Pre-select one of the boxes if needed #}
            //{# thanks http://blog.rebeccamurphey.com/2007/12/04/anchor-based-url-navigation-with-jquery/ #}
            var url = document.location.toString();
            if (url.match('#'))
                $('#groupheader a[href$="' + url.split('#')[1] + '"]').click();

        });