#!/bin/bash
#curl -s http://127.0.0.1:8080/info > test.json
#
#services=` curl -s http://127.0.0.1:8080/info | jq -r 'keys | join(" ")' `
#
#
#for service in services; do
    #echo $service
#done
#curl -s http://127.0.0.1:8080/?service=chainSelf

test -e ssshtest || wget -q https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest
. ssshtest

server=../../src/server.py
test_config=../data/test_config.json
bad_config=../data/bad.json
test_port=8569

run test_no_config_given \
    $server
assert_exit_code 2

run test_on_reserve_port \
    $server --config $test_config --port 80
assert_exit_code 1
assert_in_stderr "ERROR starting the server"
assert_in_stderr "[Errno 13] Permission denied"

run bad_json_config \
    $server --config $bad_config
assert_exit_code 1
assert_in_stderr "ERROR loading config file."

BGREEN='\033[1;32m'
NC='\033[0m' # No Color
echo
echo -e "${BGREEN}Starting test server${NC}"
echo
$server --config $test_config --port $test_port 1> /dev/null 2> /dev/null &

sleep 5

export server_pid=$!
server_ret=$?

if [ "$server_ret" -ne "0" ]; then
    BRED='\033[1;31m'
    echo -e "${BRED}***************************************************${NC}"
    echo -e "${BRED}*                                                 ${NC}"
    echo -e "${BRED}* Could not start the server, with command        ${NC}"
    echo -e "${BRED}* $server --config $test_config --port $test_port ${NC}"
    echo -e "${BRED}* Exiting tests                                   ${NC}"
    echo -e "${BRED}*                                                 ${NC}"
    echo -e "${BRED}***************************************************${NC}"
    exit
fi

function tear_down {
    echo 
    echo -e "${BGREEN}Shutting down test server${NC}"
    echo 
    kill $server_pid
}

run test_running_server_exception \
    curl "http://127.0.0.1:$test_port"
assert_exit_code 0
assert_in_stdout '{"exception": "No service specified", "success": 0}'

run test_get_info \
    curl "http://127.0.0.1:$test_port/info"
assert_exit_code 0
assert_in_stdout '{"tabs": {"name": "tabs", "output": {"type": "text_stream"}, "inputs": []}, "commas": {"name": "commas", "output": {"type": "text_stream"}, "inputs": []}}'

run test_get_info \
    curl "http://127.0.0.1:$test_port/?service=tabs"
assert_exit_code 0
assert_in_stdout '{"success": 1, "result": [["A", "B", "C", "D"], ["E", "F", "G", "H"]]}'

run test_get_info \
    curl "http://127.0.0.1:$test_port/?service=commas"
assert_exit_code 0
assert_in_stdout '{"success": 1, "result": [["A", "B", "C", "D"], ["E", "F", "G", "H"]]}'

