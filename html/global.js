/**
 * Javascript for Universal Login front-end
 */
$(function() {

    // Setup Page Code
    function init_setup_page() {
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

        let page = 1;

        form.submit(function(e) {

            // Increment page by 1
            page++;

            function page_2() {

                // Prevent form submission
                e.preventDefault();
                mg_page.attr('hidden', '');
                tp_page.removeAttr('hidden');
            }

            function page_3() {

                // Prevent form submission
                e.preventDefault();

                // Initial test states (boolean)
                let successful_mongodb_test = false;
                let successful_third_party_auth_test = false;

                // Displays the third page
                tp_page.attr('hidden', '');
                vr_page.removeAttr('hidden');

                setTimeout(function() {

                    let test_count = 0;
                    let test_success = 0;

                    // Step 1. Test mongo connection
                    test_mongo_connection();

                    // Step 2. Test mongo admin power
                    test_mongo_admin_user();

                    // Step 3. Test mongo admin power
                    test_mongo_admin_power();

                    // Step 4. Test third party auth
                    test_third_party_auth();

                    function test_mongo_connection() {

                        // Sets status to in-progress (mongodb)
                        $(vr_status_item[0]).removeClass('pending');
                        $(vr_status_item[0]).addClass('in-progress');

                        // Test MongoDB Connection
                        $.post('/setup/verify/mongodb', {
                            'UL_DB_HOST': $(mg_textbox[0]).val()
                        }, function() {

                            // Increment number of successful test
                            test_success++;

                            // Implies successful request
                            $(vr_status_item[0]).removeClass('in-progress');
                            $(vr_status_item[0]).addClass('success');
                        }).fail(function() {

                            // Implies failed request
                            $(vr_status_item[0]).removeClass('in-progress');
                            $(vr_status_item[0]).addClass('fail');
                        }).always(function() {

                            // Increment number of test
                            test_count++;

                            // Check if test is done
                            check_if_test_is_done();
                        });
                    }

                    function test_mongo_admin_user() {

                        // Sets status to in-progress (mongodb)
                        $(vr_status_item[1]).removeClass('pending');
                        $(vr_status_item[1]).addClass('in-progress');
                        // Test MongoDB Admin Powers
                        $.post('/setup/verify/mongodb_admin_user', {
                            'UL_DB_HOST': $(mg_textbox[0]).val(),
                            'UL_DB_ROOT_USER': $(mg_textbox[1]).val(),
                            'UL_DB_ROOT_PASS': $(mg_textbox[2]).val()
                        }, function() {

                            // Increment number of successful test
                            test_success++;

                            // Implies successful request
                            $(vr_status_item[1]).removeClass('in-progress');
                            $(vr_status_item[1]).addClass('success');
                        }).fail(function() {

                            // Implies failed request
                            $(vr_status_item[1]).removeClass('in-progress');
                            $(vr_status_item[1]).addClass('fail');
                        }).always(function() {

                            // Increment number of test
                            test_count++;

                            // Check if test is done
                            check_if_test_is_done();
                        });
                    }

                    function test_mongo_admin_power() {

                        // Sets status to in-progress (mongodb)
                        $(vr_status_item[2]).removeClass('pending');
                        $(vr_status_item[2]).addClass('in-progress');
                        // Test MongoDB Admin Powers
                        $.post('/setup/verify/mongodb_admin_power', {
                            'UL_DB_HOST': $(mg_textbox[0]).val(),
                            'UL_DB_ROOT_USER': $(mg_textbox[1]).val(),
                            'UL_DB_ROOT_PASS': $(mg_textbox[2]).val()
                        }, function() {

                            // Increment number of successful test
                            test_success++;

                            // Implies successful request
                            $(vr_status_item[2]).removeClass('in-progress');
                            $(vr_status_item[2]).addClass('success');
                        }).fail(function() {

                            // Implies failed request
                            $(vr_status_item[2]).removeClass('in-progress');
                            $(vr_status_item[2]).addClass('fail');
                        }).always(function() {

                            // Increment number of test
                            test_count++;

                            // Check if test is done
                            check_if_test_is_done();
                        });
                    }

                    function test_third_party_auth() {

                        // Check if third party auth option is checked
                        if (tp_checkbox.prop('checked')) {

                            // Sets status to in-progress (third-party auth)
                            $(vr_status_item[3]).removeClass('pending');
                            $(vr_status_item[3]).addClass('in-progress');

                            // Tests third party auth
                            $.post('/setup/verify/third_party_auth', {
                                'UL_TP_CHECK': tp_checkbox.val(),
                                'UL_TP_URL': $(tp_textbox[0]).val(),
                                'UL_TP_REQUEST_FORMAT': $(tp_textbox[1]).val()
                            }, function() {

                                // Increment number of successful test
                                test_success++;

                                // Implies successful request
                                $(vr_status_item[3]).removeClass('in-progress');
                                $(vr_status_item[3]).addClass('success');
                            }).fail(function() {

                                // Implies failed request
                                $(vr_status_item[3]).removeClass('in-progress');
                                $(vr_status_item[3]).addClass('fail');
                            }).always(function() {

                                // Increment number of test
                                test_count++;

                                // Check if test is done
                                check_if_test_is_done();
                            });

                        } else {

                            // Implies no action (because disabled)
                            $(vr_status_item[3]).removeClass('pending');
                            $(vr_status_item[3]).addClass('wont-do');
                        }
                    }

                    function check_if_test_is_done() {

                        // Get total number of test, decided by vr_status_item # 3
                        let total_test = ($(vr_status_item[3]).hasClass('wont-do')) ? 3 : 4;

                        if (test_count === total_test) {
                            if (test_count === test_success) {

                                // Timer counter
                                let time = 5;

                                // Show success message
                                $('body > form > div:nth-child(4) > div.message.success').removeAttr('hidden');

                                // Pauses the script for 5 seconds
                                setInterval(function() {

                                    // Submits the form once it reaches zero.
                                    if (--time === 0) form.submit();

                                    // Update the counter.
                                    else $('body > form > div:nth-child(4) > div.message.success > p > span:nth-child(1)').text(time);

                                    // Remove 's' when we reach the 1 second.
                                    if (time === 1) $('body > form > div:nth-child(4) > div.message.success > p > span:nth-child(2)').text('');
                                }, 1000);

                            } else {

                                // Show fail message
                                $('body > form > div:nth-child(4) > div.message.fail').removeAttr('hidden');
                            }
                        }
                    }
                }, 500);
            }

            if (page === 2) page_2();
            else if (page === 3) page_3();
        });
    }

    // Setup Page Done Code
    function init_setup_done_page() {
        let setup_page = $('body.setup-done > div > pre');
        $.get('/setup/get_environment', function(res) {
            env = '';
            console.log(res);
            Object.entries(res.env).forEach(([key, value]) => {
                env += key + '=' + value + '\n'
            });
            setup_page.text(env);
        }).fail(function() {
            // If page fails, it implies that we are not authorized to see the page.
            location.href = '/login'
        });
    }

    // Login Page Code
    function init_login_page() {

        // Initialize variables
        let username = $('#login > div > div.inputs > input[type="text"]:nth-child(1)');
        let password = $('#login > div > div.inputs > input[type="password"]:nth-child(2)');

        $('form#login').submit((e) => {

            // Prevents form submission
            e.preventDefault();

            // Performs login
            $.post('/api/v1/login', {
                'username': username.val(),
                'password': password.val()
            }, (res) => {

                // Opens an alert message box (temporary)
                alert(res.msg);

            }).fail((res) => {

                // Opens an alert message box
                alert(res.msg);
            });
        });
    }

    // Loads setup page if the page is "setup" page
    if ($('form#setup').length === 1) {
        init_setup_page()
    }

    // Loads setup_done page if the page is "setup_done" page
    if ($('body.setup-done > div > pre').length === 1) {
        init_setup_done_page();
    }

    // Loads login page if the page is "login" page
    if ($('form#login').length === 1) {
        init_login_page()
    }
});
