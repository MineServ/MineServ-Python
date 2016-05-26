#!/usr/bin/python2.7

import os
import sys
import socket
import getopt
import threading
import subprocess


# define some global variables
target             = ""
port               = 2048

# this runs a command and returns the output
def run_command(command):
    # trim the newline
    command = command.rstrip()
    # run the command and get the output back
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    # send the output back to the client
    return output

def uptime():
    output = "StartAt: "
    output += run_command("uptime -s")
    output += "Running: "
    tmp = run_command("uptime -p")
    output += tmp[3:]
    return output

# this handles incoming client connections
def client_handler(client_socket):
        # now we go into another loop if a command shell was requested
        response = ""
        while True:
                # now we receive until we see a linefeed (enter key)
                cmd_buffer = ""
                cmd_buffer += client_socket.recv(1024)
                cmd_buffer = cmd_buffer.strip()
                if "exit" in cmd_buffer or not len(cmd_buffer):
                        host,port = client_socket.getpeername()
                        client_socket.send("bye-bye\n")
                        print "%s:%s exited"%(host, port)
                        break
                if cmd_buffer == "UPTIME":
                    client_socket.send(uptime())
                else:
                    # we have a valid command so execute it and send back the results
                    response = run_command(cmd_buffer)
                # send back the response
                client_socket.send(response)
        client_socket.close()

# this is for incoming connections
def server_loop():
        global target
        global port

        # if no target is defined we listen on all interfaces
        if not len(target):
            target = "0.0.0.0"

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((target,port))
        server.listen(5)
        print "server running at [%s:%d]" %(target, port)
        while True:
            client_socket, addr = server.accept()
            # spin off a thread to handle our new client
            print "get connection from: ", addr
            client_thread = threading.Thread(target=client_handler,args=(client_socket,))
            client_thread.start()


if __name__ == '__main__':
    os.system('clear')
    try:
        server_loop()
    except KeyboardInterrupt as e:
        print "bye"
