var server_url = '';
var server_info = null;
var server_result = null;

$(document).ready(function() {
})

function setServer() {
    server_url = $('#server_text').val();

    if (server_url.length == 0) {
        return
    }

    var get_server_info_promise = get_server_info(server_url + '/info').then(function(data) {
        server_info = data
    });

    Promise.all([get_server_info_promise]).then(
        function(values) {
            //unset_loading();
            setInputForm();
        }
    );
}

function get_server_info(url) {
    return new Promise( function(resolve, reject) {
        $.get(url,
            function (data) {
                resolve( JSON.parse(data) );
            }
        );
    });
}

function setInputForm(){
    for (var i = 0; i < server_info.inputs.length; ++i){
        input_str = '<input type="text" id="' + 
                server_info.inputs[i] + '"' + 
                ' placeholder="' +  
                server_info.inputs[i] + '">';
        $('#input').append(input_str);
    }

    $('#input').append('<button id="get_data" onclick="getData()">Get</button>');
}

function getData() {

    $('#output').empty();

    url_params = "?";

    for (var i = 0; i < server_info.inputs.length; ++i){
        url_params += server_info.inputs[i] + '=' + $('#' + server_info.inputs[i]).val();
    }  

    var get_data_promise = get_data(server_url + url_params).then(function(data) {
        server_result = data;
    });

    Promise.all([get_data_promise]).then(
        function(values) {
            showData();
        }
    );
}

function get_data(url) {
    return new Promise( function(resolve, reject) {
        $.get(url,
            function (data) {
                resolve( JSON.parse(data) );
            }
        );
    });
}

function showData() {
    $('#output').append('<table id="output_table">');
    for (var i = 0; i < server_result.length; ++i){
        $('#output_table').append('<tr>');
        for (var j = 0; j < server_result[i].length; ++j){
            $('#output_table').append('<td>');
            $('#output_table').append(server_result[i][j]);
            $('#output_table').append('<td>');
        }
        $('#output_table').append('</tr>');
    }
    $('#output').append('</table>');
}
