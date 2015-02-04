function findMatchesUsers(q, cb) {
    $.ajax('https://backdoor.yatekii.ch/to_json/users', {q: q}).done(function (json) {
        var substrRegex = new RegExp(q, 'i');
        var matches = [];
        $.each($.parseJSON(json).users, function (i, entry) {
            if (substrRegex.test(entry.name)) {
                matches.push(entry);
            }
        });
        cb(matches);
    });
}

function findMatchesDevices(q, cb) {
    $.ajax('https://backdoor.yatekii.ch/to_json/devices', {q: q}).done(function (json) {
        var substrRegex = new RegExp(q, 'i');
        var matches = [];
        $.each($.parseJSON(json).devices, function (i, entry) {
            if (substrRegex.test(entry.name)) {
                matches.push(entry);
            }
        });
        cb(matches);
    });
}

function user_typeahead() {
    $.each($('.user_typeahead'), function (i, entry){
        var input = $(entry).find('.user_typeahead_name');
        input.typeahead({
                minLength: 1,
                highlight: false,
                hint: false
            },
            {
                name: 'owners',
                source: findMatchesUsers,
                displayKey: 'name'
            }
        );

        var input_id = $(entry).find('.user_typeahead_id');

        input.bind('typeahead:selected', function (obj, datum, name) {
            input_id.val(datum.id);
        });

        input.bind('typeahead:opened', function (obj, datum, name) {
            input_id.val('');
        });
    });
}

function device_typeahead() {
    $.each($('.device_typeahead'), function (i, entry){
        var input = $(entry).find('.device_typeahead_name');
        input.typeahead({
                minLength: 1,
                highlight: false,
                hint: false
            },
            {
                name: 'devices',
                source: findMatchesDevices,
                displayKey: 'name'
            }
        );

        var input_id = $(entry).siblings().filter('.device_typeahead_id');

        input.bind('typeahead:selected', function (obj, datum, name) {
            input_id.val(datum.id);
        });

        input.bind('typeahead:opened', function (obj, datum, name) {
            input_id.val('');
        });
    });
}

function remove_init(){
    $.each($(".remove_form"), function (i, entry){
        $(entry).submit(function () {
            var button = $(entry).find("input[type='submit']");
            if (button.val() == "Remove") {
                button.val("Confirm");
                return false;
            }
        });
    });
}

function init_edit_field(name) {
    $('form').on('click', name, function (event) {
        var icon = $(this).find('.glyphicon-pencil');
        if (icon.hasClass('glyphicon-pencil')) {
            event.preventDefault();
            icon.removeClass('glyphicon-pencil')
                .addClass('glyphicon-ok');
            $(this).parent().siblings().prop("readonly", false);
        }
    });
}

function check_flashed_status(entry, id) {
    $.ajax({
        type: 'POST',
        url: 'https://backdoor.yatekii.ch/token_flashed',
        data: {token_id: id}
    }).done(function (data) {
        if (data == 'True') {
            alert("got flashed");
        }
    });
}

function flashed_init() {
    $.each($(".flash_form"), function (i, entry) {
        setInterval(function () {
            check_flashed_status(entry, $(entry).find("input[name='token_id']"));
        }, 2000)
    });
}