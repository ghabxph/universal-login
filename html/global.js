/**
 * Javascript for Universal Login front-end
 */
$(function() {

    // Elements
    let form = $('body > form');
    let mg_page = $('body > form > div:nth-child(2)');
    let mg_textbox = $('body > form > div:nth-child(2) > div.inputs > input[type="text"], body > form > div:nth-child(2) > div.inputs > input[type="password"]');
    let tp_page = $('body > form > div:nth-child(3)');
    let tp_checkbox = $('body > form > div:nth-child(3) > div.inputs > div.activator > label > input[type="checkbox"]');
    let tp_textbox = $('body > form > div:nth-child(3) > div.inputs > div.activator-toactivate > input[type="text"], body > form > div:nth-child(3) > div.inputs > div.activator-toactivate > textarea');
    let tp_textbox_method = $('body > form > div:nth-child(3) > div.inputs > div.activator-toactivate > input[type="text"]:nth-child(7)');
    let vr_page = $('body > form > div:nth-child(4)');
    let vr_status_item = $('body > form > div:nth-child(4) > ul > li');

    $('.setup > form > div:nth-child(2) > div.next-button > a').click(function() {
        mg_page.attr('hidden', '');
        tp_page.removeAttr('hidden');
    });

    tp_checkbox.change(function() {

        // Check if checkbox is checked
        if (tp_checkbox.prop('checked')) {

            // Enable textbox / textarea on "Third Party" page
            tp_textbox.removeAttr('disabled');

            // Retain "disabled" attribute to "METHOD" field..
            tp_textbox_method.attr('disabled', '');

        } else {

            // Enable textbox / textarea on "Third Party" page
            tp_textbox.attr('disabled', '');
        }

    });

    form.submit(function(e) {

        // Initial test states (boolean)
        let successful_mongodb_test = false;
        let successful_third_party_auth_test = false;

        // Prevents form submission
        e.preventDefault();

        // Displays the third page
        tp_page.attr('hidden', '');
        vr_page.removeAttr('hidden');

        setTimeout(function() {

            // Sets status to in-progress (mongodb)
            $(vr_status_item[0]).removeClass('pending');
            $(vr_status_item[0]).addClass('in-progress');

            // Test MongoDB
            $.post('/setup/verify/mongodb', {
                'UL_DB_HOST': $(mg_textbox[0]).val(),
                'UL_DB_USER': $(mg_textbox[1]).val(),
                'UL_DB_PASS': $(mg_textbox[2]).val(),
                'UL_DB_NAME': $(mg_textbox[3]).val()
            }, function() {

                // Implies successful request
                $(vr_status_item[0]).addClass('in-progress');
                $(vr_status_item[0]).addClass('success');
            }).fail(function() {

                // Implies failed request
                $(vr_status_item[0]).addClass('in-progress');
                $(vr_status_item[0]).addClass('fail');
            });

            // Check if third party auth option is checked
            if (tp_checkbox.prop('checked')) {

                // Sets status to in-progress (third-party auth)
                $(vr_status_item[1]).removeClass('pending');
                $(vr_status_item[1]).addClass('in-progress');
                // Tests third party auth
                $.post('/setup/verify/third-party-auth', {
                    'UL_TP_CHECK': tp_checkbox.value(),
                    'UL_TP_URL': $(mg_textbox[0]).val(),
                    'UL_TP_METHOD': $(mg_textbox[1]).val(),
                    'UL_TP_USER_FIELD': $(mg_textbox[2]).val(),
                    'UL_TP_PASS_FIELD': $(mg_textbox[3]).val(),
                    'UL_TP_OTHER_FIELDS': $(mg_textbox[4]).val()
                }, function() {

                    // Implies successful request
                    $(vr_status_item[1]).addClass('in-progress');
                    $(vr_status_item[1]).addClass('success');

                }).fail(function() {

                    // Implies failed request
                    $(vr_status_item[1]).addClass('in-progress');
                    $(vr_status_item[1]).addClass('fail');
                });
            } else {

                // Implies no action (because disabled)
                $(vr_status_item[1]).removeClass('pending');
                $(vr_status_item[1]).addClass('wont-do');
            }
        }, 500);
    });
});
