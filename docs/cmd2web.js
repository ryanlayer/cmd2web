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

    $('#services').empty();

    $('#services').append('<select onchange="setService()" id="service-select"></select>');
    var serviceSelect = document.getElementById('service-select');


    for (var service in server_info) {
        serviceSelect.options[serviceSelect.options.length] = new Option(service, service);
    }

    $('#services').append('<button id="set-service" onclick="setService()">Set Service</button>');
}

function setService() {

    $('#input').empty();
    $('#output').empty();

    var serviceSelect = document.getElementById('service-select');
    var selectedService = serviceSelect.options[serviceSelect.selectedIndex].value;

    console.log(selectedService);
    for (var i = 0; i < server_info[selectedService].inputs.length; ++i){
        console.log(server_info[selectedService].inputs[i]);
        input_str = '<input type="text" id="' + 
                server_info[selectedService].inputs[i].name + '"' + 
                ' placeholder="' +  
                server_info[selectedService].inputs[i].name + '">';
        $('#input').append(input_str);
    }

    $('#input').append('<button id="get_data" onclick="getData()">Get</button>');
}

function getData() {

    var serviceSelect = document.getElementById('service-select');
    var selectedService = serviceSelect.options[serviceSelect.selectedIndex].value;

    $('#loading').append('loading...');

    $('#output').empty();

    url_params = "?service=" + selectedService;

    console.log(server_info[selectedService]);
    for (var i = 0; i < server_info[selectedService].inputs.length; ++i){
        var inputName = server_info[selectedService].inputs[i].name;
        var inputValue = document.getElementById(inputName).value;
        url_params += '&' + inputName + '=' + inputValue
    }  

    var get_data_promise = get_data(server_url + url_params).then(function(data) {
        server_result = data;
    });

    Promise.all([get_data_promise]).then(
        function(values) {
            showData();
            console.log('DONE 1');
        }
    );
}

function get_data(url) {
    return new Promise( function(resolve, reject) {
        $.get(url,
            function (data) {
                console.log(data);
                resolve( JSON.parse(data) );
                console.log('DONE');
            }
        );
    });
}

function showData() {
    console.log('showData');
    if (server_result.success != 1) {
        $('#output').append('Command did not complete successfully');
    } else {
        console.log('0');
        $('#loading').empty();
        var result = server_result.result;
       $('#output').append('<table id="output_table">');
       for (var i = 0; i < result.length; ++i){
           row = '<tr>';
           for (var j = 0; j < result[i].length; ++j){
               row += '<td>' + result[i][j] + '</td>';
           }
           row += '</tr>';
           $('#output_table').append(row);
       }
       $('#output').append('</table>');
    }
}
