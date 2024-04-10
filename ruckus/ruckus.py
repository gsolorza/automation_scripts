#!/usr/bin/python3
# Jimmy Taylor
# https://www.consentfactory.com/python-threading-queuing-netmiko/

# This method will spin up threads and process IP addresses in a queue

# Importing Netmiko modules
import paramiko

# Additional modules imported for getting password, pretty print
from getpass import getpass
import os,sys,time

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
password = "gX9qO!2h9!9b"
print("\r")

# Set up thread count for number of threads to spin up
num_threads_str = input( '\nNumber of threads (8): ' ) or '8'
num_threads     = int( num_threads_str )

commands_send = ["show version"]

#Log File TimeStampt
with open("failed.txt", "w+") as data1:
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

        try:

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Connect to the AP
            ssh_client.connect(ip, username=username, password=password)
            print(f"Connected to AP {ip}")

            # Start an interactive shell session
            shell = ssh_client.invoke_shell()
            while "login" not in shell.recv(9999).decode("utf-8"):
                pass
            shell.send(username+"\r")
            while "password" not in shell.recv(9999).decode("utf-8"):
                pass
            shell.send(password+"\r")

            # Send commands to change the SmartZone Director controller IP
            commands = [
                "set scg 172.20.1.11,10.91.252.3\r",
                "get scg\r"
            ]

            for command in commands:
                output = ""
                shell.send(command)
                while "rkscli:" not in output:
                    output = shell.recv(9999).decode("utf-8")

            # Wait for the commands to be executed
            while not shell.recv_ready():
                time.sleep(1)

            # Print the output of the commands
            output = shell.recv(9999).decode("utf-8")
            with open("output.txt", "a+") as data:
                data.write(ip+"\n")
                data.write(output+"\n")
                data.write(100*"#")
                data.write("\n")

        except Exception as error:
            with open("failed.txt", "a+") as data:
                data.write(f"ERROR --> {ip} - {error}\n")
        finally:
            # Close the SSH connection
            ssh_client.close()
            print("Disconnected from the AP.")

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