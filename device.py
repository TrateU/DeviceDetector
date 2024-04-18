import os
import shutil
import time
import linecache
import getpass
import hashlib
import random
from inputimeout import inputimeout

USB_DEVICES_STORE = "lsusb -t > info/devices"

USB_DEVICES_CHECK = "lsusb -t > info/devices_check"

CHECK_DIFFERENCE = "diff info/devices info/devices_check > info/diff"

USB_MODE = 0

hashed_pass = 0

    

def find_bus(dev):
    file = open("info/devices_check")
    line_num = -1
    for num, line in enumerate(file, 0):
        if dev[8:35] in line:
            line_num = num
            break
    
    if line_num < 0: 
        print("ERROR LINE NOT FOUND")
    
    file.seek(0)

    lines = file.readlines()

    found_bus_line = ""

    for i in range(line_num, -1, -1):
        if "/:" in lines[i]:
            found_bus_line = lines[i]
            break

    found_split = found_bus_line.split(" ")

    return found_split[found_split.index("Bus") + 1][:-5]
    
    
    




def is_diff_empty():
    try:
        file_size = os.path.getsize("info/diff")
    except FileNotFoundError:
        print("Error: diff file not found.")
        return -1
    return file_size

def load_new_devices():
    os.system(USB_DEVICES_CHECK)

if __name__ == "__main__":
    import sys
    os.system("sudo whoami > info/user")
    user = open("info/user").readline().rstrip()
    os.system("rm info/user")
    salt = str(random.randint(-10000,100000))

    hashed_pass = hashlib.sha256((getpass.getpass(prompt="Set Password: ") + salt).encode()).hexdigest()

    try:
        os.system(USB_DEVICES_STORE)


        print("Monitoring Devices...")
        while True:
            load_new_devices()
            os.system(CHECK_DIFFERENCE)
            file_size = is_diff_empty()
            time.sleep(1)
            if file_size > 0:
                diff = open("info/diff")

                new_devices = diff.readlines()[1:]

                prev_port = -1
                prev_dev = -1

                for d in new_devices:
                    if d[0] == '<' or d[0] == "-": continue
                    d = d.replace(">", "")
                    bus_num = find_bus(d)
                    if bus_num[0] == '0': bus_num = bus_num[-1:]


                    dev_split = d.split(" ")

                    port_num = dev_split[dev_split.index("Port") + 1][:-1]
                    dev_num = dev_split[dev_split.index("Dev") + 1][:-1]

                    #if prev_port == port_num and prev_dev == dev_num: continue
                    
                    prev_port = port_num
                    prev_dev = dev_num

                    print("NEW DEVICE DETECTED!")
                    
                    command = "lsusb -s " + bus_num + ":" + dev_num
                    os.system(command)


                    
                    valid = True
                    while valid:
                        print("\nDevice will be rejected in 30 seconds.")
                        try:
                            choice = inputimeout(prompt='Allow device to connect? (y/n) or type v for more information: ', timeout=30)
                        except Exception:
                            command = "echo '" + bus_num + "-" + port_num + "' |sudo tee /sys/bus/usb/drivers/usb/unbind > info/errors"
                            os.system(command)
                            print("\n\nDevice was disconected.")
                            valid = False
                            continue
                        
                        if choice == 'n' or choice == 'N':
                            valid = False
                            command = "echo '" + bus_num + "-" + port_num + "' |sudo tee /sys/bus/usb/drivers/usb/unbind > info/errors"
                            os.system(command)
                            print("\n\nDevice was disconected.")
                        elif choice == 'Y' or choice == 'y':
                            if hashed_pass == hashlib.sha256((getpass.getpass(prompt="Password: ") + salt).encode()).hexdigest():
                                valid = False
                                print("\n\nDevice Accepted")
                            else:
                                print("Invalid Password. Disconnecting the device.")
                                valid = False
                                command = "echo '" + bus_num + "-" + port_num + "' |sudo tee /sys/bus/usb/drivers/usb/unbind > info/errors"
                                os.system(command)
                            
                        elif choice == 'V' or choice == 'v':
                            command = "lsusb -s " + bus_num + ":" + dev_num + " -v"
                            os.system(command)
                            time.sleep(3)
                        else:
                            print("ERROR INVALID OPTION")
                    
                os.system(USB_DEVICES_STORE)
                print("\nMonitoring Devices...")
                        
                        
                

                        


                




             
                
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
