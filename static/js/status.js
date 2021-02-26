var is_updating = true;

function updateText() {
    if (!is_updating) return;
    if (!rows_to_update.length){
        is_updating = false;
        return;
    }
    $.ajax({
        url: "/update",
        type: "GET",
        data: {"rows_to_update": JSON.stringify(rows_to_update)},
        success: function(response) {
            if (!response) {
                is_updating = false;
            }
            else {
                let json = JSON.parse(response);
                for (var k in json) {
                    var elem = $("#solution-row-" + k);
                    elem.html(json[k][0]);
                    if (json[k][1]){
                        var index = rows_to_update.indexOf(parseInt(k));
                        if (index > -1) {
                            rows_to_update.splice(index, 1);
                            console.log('end updating ' + k);
                        }
                    }
                }
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (textStatus == 'timeout') {
                console.log('timeout of getting update request')
            } else {
                is_updating = false;
            }
        },
        timeout: update_timeout
    });

};

updateText();
setInterval(updateText, update_timeout);
