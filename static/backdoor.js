function findMatches(q, cb) {
    $.ajax('https://backdoor.yatekii.ch/json/users', {q: q}).done(function (json) {
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
                source: findMatches,
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