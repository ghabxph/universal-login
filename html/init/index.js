$(() => {
    $('.panel.controller li').click((el) => {

        // Remove all 'selected' class to li element
        $('.panel.controller li').removeClass('selected');

        // Add 'selected' class to clicked item (to perceive that we switched panel)
        $(el.target).addClass('selected');

        // Hide all panel.body
        $('div.panel.body').attr('hidden', '');

        // Show target panel.body
        $('div[data-panel-name="' + $(el.target).attr('data-for') + '"].panel.body').removeAttr('hidden');
    });

    $('.panel.body a').click((el) => {

        // Prevent showing '#'
        el.preventDefault();

        // Run function based on link's text
        switch($(el.target).text()) {
            case 'Generate new token':
                generate_new_token();
                break;
        }
    });

    $('.panel.body[data-panel-name="manage-other-instance"] form').submit((el) => {

        // Prevent form from submitting.
        el.preventDefault();

        // Attempts to login
        $.post('/api/v1/admin/manage', {
            'url': $(el.target).find('input[name="url"]').val(),
            'key': $(el.target).find('input[name="key"]').val()
        }, (res) => {

            console.log(res)
//
//            // Redirect to what route server instructs.
//            location.href = res.redirect;
        }).fail((xhr) => {

            // Alerts the error
            alert(xhr.responseJSON.msg);
        })
    });

    function generate_new_token() {
        $.ajax({
            url: '/api/v1/admin/token',
            type: 'POST',
            success: (res) => {
                $('.panel.body .admin-token').text(res);
                $('.panel.body .server-msg').text(res.msg);
            }
        }).fail((xhr) => {
            $('.panel.body .admin-token').text(xhr.responseText);
            $('.panel.body .server-msg').text(xhr.msg);
        });
    }
});