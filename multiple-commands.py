#!/usr/bin/python3
# Jimmy Taylor
# https://www.consentfactory.com/python-threading-queuing-netmiko/

# This method will spin up threads and process IP addresses in a queue

# Importing Netmiko modules
from netmiko import Netmiko
from paramiko.ssh_exception import SSHException

# Additional modules imported for getting password, pretty print
from getpass import getpass
import os,sys

# Queuing and threading libraries
from queue import Queue
import threading

#Datetime
from datetime import datetime

# These capture errors relating to hitting ctrl+C (I forget the source)
#signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # IOError: Broken pipe
#signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C

#print(os.get_terminal_size())
#message1 = " Script complete "
#end_message = message1.center((os.get_terminal_size().columns), "#")
#welcome = message.center((os.get_terminal_size().columns), "#")


message = " Getting SSH credentials "
cwd = os.getcwd()

date_time_ini = datetime.now()
d = date_time_ini.strftime("%m/%d/%Y, %H:%M:%S")
date_start = "Script Start: " + d
script_start_time = date_start.center(os.get_terminal_size().columns)

welcome = message.center((os.get_terminal_size().columns))

print("\n")
print(script_start_time,"\r")
print(welcome,"\n")

# Get the username password
username = sys.argv[1]
password = getpass("Password: ")
print("\r")

# Set up thread count for number of threads to spin up
num_threads_str = input( '\nNumber of threads (8): ' ) or '8'
num_threads     = int( num_threads_str )

commands_send = ["show run | sec DNS"]

#Log File TimeStampt
with open("failed.txt", "a+") as data1:
    data1.write(script_start_time + "\n")
#print (datetime.now())

# Switch IP addresses from text file that has one IP per line
ip_addrs_file = open('host.txt')
ip_addrs = ip_addrs_file.read().splitlines()



# Set up thread count for number of threads to spin up



#num_threads = 8
# This sets up the queue
enclosure_queue = Queue()
# Set up thread lock so that only one thread prints at a time
print_lock = threading.Lock()
# CLI command being sent. This could be anywhere (and even be a passed paramenter) 
# but I put at the top for code readability
#command = "show runn | include username"
with open("output.txt", "w+") as data2:
    data2.write("")
# Function used in threads to connect to devices, passing in the thread # and queue
def deviceconnector(i,q):

   
    # This while loop runs indefinitely and grabs IP addresses from the queue and processes them
    # Loop will stop and restart if "ip = q.get()" is empty
    while True:
        
        
        # These print statements are largely for the user indicating where the process is at
        # and aren't required
        print("{}: Waiting for IP address...".format(i))
        ip = q.get()
        print("{}: Acquired IP: {}".format(i,ip))
        
        # k,v passed to net_connect
        device_dict =  {
            'host': ip,
            'username': username,
            'password': password,
            'device_type': 'cisco_ios'
        }

        #input_commands = commands
       # print(input_commands)
        # Connect to the device, and print out auth or timeout errors
        try:
            net_connect = Netmiko(**device_dict)
        except Exception:
            with print_lock:
                with open("failed.txt", "a+") as data:
                     data.write("{}:ERROR:SSHException: {}\r".format(i,ip))
            q.task_done()
            continue

        # Capture the output, and use TextFSM (in this case) to parse data
        out = ""
        hostname = net_connect.find_prompt().rstrip("#")
        ip = net_connect.host
        os.chdir(cwd)
        print(hostname)
        for command in commands_send:
            out = net_connect.send_command(command)         # Disconnect from device

        if out:
            with open(f"outputDevices/{hostname}.txt", "w+") as commandOutput:
                commandOutput.write(out)
        net_connect.disconnect()

            # Set the queue task as complete, thereby removing it from the queue indefinitely
        q.task_done()

# Mail function that compiles the thread launcher and manages the queue
def main():
 
    # Setting up threads based on number set above
    for i in range(num_threads):
        # Create the thread using 'deviceconnector' as the function, passing in
        # the thread number and queue object as parameters 
        thread = threading.Thread(target=deviceconnector, args=(i,enclosure_queue,))
        # Set the thread as a background daemon/job
        thread.setDaemon(True)
        # Start the thread
        thread.start()

    # For each ip address in "ip_addrs", add that IP address to the queue
    for ip_addr in ip_addrs:
        enclosure_queue.put(ip_addr)

    # Wait for all tasks in the queue to be marked as completed (task_done)
    enclosure_queue.join()
    #print("*** Script complete")
    print("\n")
    #print(end_message)
    
    date_time_end = datetime.now()
    
    d_end = date_time_end.strftime("%m/%d/%Y, %H:%M:%S")
    
    date_end = "Script End: " + d_end
    
    script_end_time = date_end.center(os.get_terminal_size().columns)
    
    print(script_end_time,"\n")
    with open("failed.txt", "a+") as data1:
        data1.write(script_end_time + "\n")
    data1.closed
  
    
if __name__ == '__main__':
    
    # Calling the main function
    main()
