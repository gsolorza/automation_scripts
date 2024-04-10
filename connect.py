from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

def ssh(deviceName, deviceIp, username, password):
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': deviceIp, 
        'username': username,
        'password': password
    }

    try:
        command = 'show ip interface brief'
        net_connect = ConnectHandler(**ios_device)
        output = net_connect.send_command(command, use_textfsm=True)
        # Disconnect from device
        net_connect.disconnect
        return output
    except (AuthenticationException):
        print ('Authentication failure: ' + deviceName)
        with open("failed.txt", "a+") as data:
              data.write("Authentication_Error: " + deviceName + "\r")
    except (NetMikoTimeoutException):
        print ('Timeout to device: ' + deviceName)
        with open("failed.txt", "a+") as data:
              data.write("Authentication_Timeout: " + deviceName + "\r")
    except (EOFError):
        print ('End of file while attempting device ' + deviceName)
        with open("failed.txt", "a+") as data:
              data.write("EOFError: " + deviceName + "\r")
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + deviceName)
        with open("failed.txt", "a+") as data:
              data.write("SSHException: " + deviceName+"\n")
    except Exception as unknown_error:
        print ('Some other error: ' + str(unknown_error))




        