var server_url = '';
var server_info = null;
var server_result = null;
var selectedService = null;

$(document).on("click","#submit_btn",function(e) {
     e.preventDefault();
     var formData = $("#form1").submit(function (e) {
         return;
     })
 var formData = new FormData(formData[0]);
 $.ajax({
     url: $('#form1').attr('action'),
     type: 'POST',
     data: formData,
     success: function (response) {
         server_result = JSON.parse(response);
         showData();
         console.log(response);
     },
     contentType: false,
     processData: false,
     cache: false
 }, false)
 });

function setForm() {


     var formData = $("#form1").submit(function (e) {
         return;
     })

 var formData = new FormData(formData[0]);
 $.ajax({
     url: $('#form1').attr('action'),
     type: 'POST',
     data: formData,
     success: function (response) {
         server_result = JSON.parse(response);
         showData();
         console.log(response);
     },
     contentType: false,
     processData: false,
     cache: false
 }, false)
 };

$.urlParam = function(name){
    var results = new RegExp('[\?&]' +
                             name +
                             '=([^&#]*)').exec(window.location.href);
    if (results==null){
        return null;
    } else {
        return results[1] || 0;
    }
}

$(document).ready(function() {
    server_param = $.urlParam('server');

    if (server_param){
        server_url = decodeURIComponent(server_param);
        $('#server_text').val(server_url);
        connect_to_server();
    }

})

function setServer() {

    server_url = $('#server_text').val();

    if (server_url.length == 0) {
        return
    }

    connect_to_server();
}


function connect_to_server() {

    var get_server_info_promise = get_server_info(server_url + '/info').then(function(data) {
        server_info = data
    });

    Promise.all([get_server_info_promise]).then(
        function(values) {
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


    service_param = $.urlParam('service');

    if (service_param) {
        if ( service_param in server_info) {
            selectedService = decodeURIComponent(service_param);
            $("#set-service").val(selectedService).change();
            load_service();
        }
    }

}

function setService() {

    $('#input').empty();
    $('#output').empty();

    var serviceSelect = document.getElementById('service-select');
    selectedService = serviceSelect.options[serviceSelect.selectedIndex].value;

    load_service();
}


function load_service() {
    var file_upload= false;
    var all_vals = true;
    for (var i = 0; i < server_info[selectedService].inputs.length; ++i){
        if(server_info[selectedService].inputs[i].name == "file"){
            file_upload=true;
        }
    }
    if(file_upload){
        var action = "/f";
         var form_str = '<form id="form1" method="post" action='+action+' enctype="multipart/form-data">';
         $('#input').append(form_str);
         for (var i = 0; i < server_info[selectedService].inputs.length; ++i){
        //console.log(server_info[selectedService].inputs[i]);
        if(server_info[selectedService].inputs[i].name == "file"){
            var input_str = '<input type="file" name="file" id="' +
                server_info[selectedService].inputs[i].name + '"' +
                ' placeholder="' +
                server_info[selectedService].inputs[i].name + '">';
        }
        else{
            var input_str = '<input type="text" id="' +
                server_info[selectedService].inputs[i].name + '"' +
                ' placeholder="' +
                server_info[selectedService].inputs[i].name + '">';
        }


        $('#form1').append(input_str);

        var this_input = $.urlParam(server_info[selectedService].inputs[i].name);
        if (this_input) {
            var this_val = decodeURIComponent(this_input);
            $('#' + server_info[selectedService].inputs[i].name ).val(this_val);
        } else {
            all_vals = false;
        }
    }

    $('#form1').append('<button id="submit_btn2" type="button" onclick="getData()" >Get</button>');
    $('#form1').append('<button id="submit_btn" type="button" style="display: none;" >Get</button>');
    $('#input').append('</form>');
    }
    else{
         for (var i = 0; i < server_info[selectedService].inputs.length; ++i){
        //console.log(server_info[selectedService].inputs[i]);

            input_str = '<input type="text" id="' +
                server_info[selectedService].inputs[i].name + '"' +
                ' placeholder="' +
                server_info[selectedService].inputs[i].name + '">';

        $('#input').append(input_str);

        var this_input = $.urlParam(server_info[selectedService].inputs[i].name);
        if (this_input) {
            var this_val = decodeURIComponent(this_input);
            $('#' + server_info[selectedService].inputs[i].name ).val(this_val);
        } else {
            all_vals = false;
        }
    }
     token_str = '<input type="text" id="token"' +
                ' placeholder="token">';
     if(file_upload){
         if(server_info[selectedService].group){
        $('#form1').append(token_str);
         }
     }
     else{
         if(server_info[selectedService].group){
        $('#input').append(token_str);
         }
     }

    $('#input').append('<button id="get_data" onclick="getData()">Get</button>');

    }



    if (all_vals) {
        getData();
    }
}

function getData() {
    var file_upload= false;
    var serviceSelect = document.getElementById('service-select');
    var selectedService = serviceSelect.options[serviceSelect.selectedIndex].value;

    $('#loading').append('loading...');

    $('#output').empty();

    url_params = "?service=" + selectedService;

    console.log(server_info[selectedService]);

    for (var i = 0; i < server_info[selectedService].inputs.length; ++i){
        if(server_info[selectedService].inputs[i].name == "file"){
            file_upload=true;
        }
    }
    for (var i = 0; i < server_info[selectedService].inputs.length; ++i){
        if(server_info[selectedService].inputs[i].name != "file"){
            var inputName = server_info[selectedService].inputs[i].name;
            var inputValue = document.getElementById(inputName).value;
            url_params += '&' + inputName + '=' + inputValue
        }
    }
    if(server_info[selectedService].group){
        //It has group so token needs to be passed
        //check if token present
        var tokenVal = document.getElementById("token").value;
        url_params += '&' + "token" + '=' + tokenVal
    }
    if(file_upload){
        var form_elem = document.getElementById('form1');
        form_elem.action = form_elem.action+url_params;
        // var submit_elem = document.getElementById('submit_btn');
        // submit_elem.click();
        setForm();
    }
    else{
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


// request('GET', 'http://google.com')
//     .then(function (e) {
//         console.log(e.target.response);
//     }, function (e) {
//         // handle errors
//     });
function showData() {
    if (server_result.success != 1) {
        $('#loading').empty();
        $('#output').append('Command did not complete successfully');
        $('#exception').append(server_result.exception);
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
