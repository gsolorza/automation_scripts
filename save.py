from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from pprint import pprint
import signal,os
from datetime import datetime


message = " Getting SSH credentials "


date_time_ini = datetime.now()
d = date_time_ini.strftime("%m/%d/%Y, %H:%M:%S")
date_start = "Script Start: " + d
script_start_time = date_start.center(os.get_terminal_size().columns)

welcome = message.center((os.get_terminal_size().columns))


print("\n")
print(script_start_time,"\r")
print(welcome,"\n")

# Get the username password
# username = input("Username: ")
password = getpass("Password: ")
print("\r")

# Switch IP addresses from text file that has one IP per line
ip_addrs_file = open('host.txt')
ip_addrs = ip_addrs_file.read().splitlines()


#Log File TimeStampt
with open("failed.txt", "a+") as data1:
    data1.write(script_start_time + "\n")

for devices in ip_addrs:
    print ('Connecting to device" ' + devices)
    ip_address_of_device = devices
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': ip_address_of_device, 
        'username': "lairdadmin",
        'password': password
    }

    try:
        net_connect = ConnectHandler(**ios_device)
        print(net_connect.host)
        print("\r")
        print("Hostname: " + net_connect.find_prompt())
        print("\r")
        # Disconnect from device
        net_connect.save_config()
        net_connect.disconnect
    except (AuthenticationException):
        print ('Authentication failure: ' + ip_address_of_device)
        with open("failed.txt", "a+") as data:
              data.write("Authentication_Error: " + ip_address_of_device + "\r")
        continue
    except (NetMikoTimeoutException):
        print ('Timeout to device: ' + ip_address_of_device)
        with open("failed.txt", "a+") as data:
              data.write("Authentication_Timeout: " + ip_address_of_device + "\r")
        continue
    except (EOFError):
        print ('End of file while attempting device ' + ip_address_of_device)
        with open("failed.txt", "a+") as data:
              data.write("EOFError: " + ip_address_of_device + "\r")
        continue
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + ip_address_of_device)
        with open("failed.txt", "a+") as data:
              data.write("SSHException: " + ip_address_of_device+"\n")
        continue
    except Exception as unknown_error:
        print ('Some other error: ' + str(unknown_error))
        continue
print("\n")
   
    
date_time_end = datetime.now()

d_end = date_time_end.strftime("%m/%d/%Y, %H:%M:%S")

date_end = "Script End: " + d_end

script_end_time = date_end.center(os.get_terminal_size().columns)


# with open("failed.txt", "a+") as data1:
                # data1.write(script_end_time + "\n")
                
print(script_end_time,"\n")
    
        
        