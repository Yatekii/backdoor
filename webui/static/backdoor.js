/*

    NFC controlled door access.
    Copyright (C) 2015  Yatekii yatekii(at)yatekii.ch

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

 */


function findMatchesUsers(q, cb) {
    $.ajax('/to_json/users', {q: q}).done(function (json) {
        var substrRegex = new RegExp(q, 'i');
        var matches = [];
        $.each($.parseJSON(json).users, function (i, entry) {

            if (substrRegex.test(entry.name) || substrRegex.test(entry.username)) {
                matches.push(entry);
            }
        });
        cb(matches);
    });
}

function findMatchesDevices(q, cb) {
    $.ajax('/to_json/devices', {q: q}).done(function (json) {
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

function search_typeahead() {
    $.each($('.search_typeahead'), function (i, entry){
        var input = $(entry);

        input.typeahead({
                minLength: 1,
                highlight: true,
                hint: false
            },
            {
                name: 'users',
                source: findMatchesUsers,
                displayKey: 'name',
                templates: {
                    header: '<h3 class="search_name_title">Users</h3>',
                    suggestion: function(data){
                        return '<p><strong>' + data.name + '</strong> (' + data.username + ')</p>';
                    }
                }
            },
            {
                name: 'devices',
                source: findMatchesDevices,
                displayKey: 'name',
                templates: {
                    header: '<h3 class="search_name_title">Devices</h3>'
                }
            }
        );

        input.bind('typeahead:selected', function (obj, datum, name) {
            if(name == 'users') {
                window.location.href='/user/view/' + datum.id;
            }
            else if(name == 'devices'){
                window.location.href='/device/view/' + datum.id;
            }
        });

        input.bind('typeahead:opened', function (obj, datum, name) {

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
        url: '/token/flashed',
        data: {token_id: id}
    }).done(function (data) {
        if (data == 'True') {
            alert('Token was successfully flashed!')
            location.reload();
        }
    })
}

function flashed_init() {
    $.each($(".flash_form"), function (i, entry) {
        setInterval(function () {
            check_flashed_status(entry, $(entry).find("input[name='token_id']").val());
        }, 5000)
    });
}
