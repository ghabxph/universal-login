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

        // Dddd
        $.post('/api/v1/manage_other_instance', {
            'server_url': $(el.target).find('input[name="server_url"]').val(),
            'secret_admin_key': $(el.target).find('input[name="secret_admin_key"]').val()
        }, (res) => {

            // Shows server response to console (temporary)
            console.log(res)
        }).fail((xhr) => {

            // Prints error to console
            console.log(xhr.responseText);
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