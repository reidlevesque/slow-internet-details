"""
This will generate all the information needed to debug internet connections
"""
import datetime
import subprocess
import sys
import re
import os

_today = datetime.date.today()
_now = datetime.datetime.now()

def readlines_stdin():
    ret = ''
    while True:
        line = sys.stdin.readline()
        ret += line
        if line.endswith('reserved.\n'):
            break
    return ret

def preamble():
    f.write("PREAMBLE:\n")
    f.write("My computer is connected directly to the modem. It is running Windows 10.\n")
    f.write("Time of the test was " + _now.isoformat(' ') + '\n')
    f.write("\n")
    f.write("I have tried a different Coax cable from the modem to the wall\n")
    f.write("I have tried reseating my Ethernet cable\n")
    f.write("I have tried a different Ethernet cable\n")
    f.write("I have tried a different computer\n")
    f.write("I have tried disabling the firewall\n")
    f.write("All end up with the same result\n")
    f.write("\n\n")

def speed_test():
    f.write("SPEED TEST:\n")
    subprocess.Popen('"c:/Program Files/Mozilla Firefox/firefox.exe" "http://speedtest.net/"')
    ping = input("Ping: ")
    download = input("Download Speed: ")
    upload = input("Upload Speed: ")
    f.write(ping + " ms ping; " + download + " Mbps Down; " + upload + " Mbps Up\n")
    f.write("\n\n")

def ipconfig():
    f.write("IPCONFIG:\n")
    capture = False
    ipconfig_output = subprocess.check_output('ipconfig /all')

    # print ipconfig_output
    for line in str(ipconfig_output).split("\\r\\n"):
        print(line)
        # print line
        if line.startswith("Ethernet adapter eth0"):
            capture = True
        elif line.startswith("Tunnel adapter Teredo Tunneling Pseudo-Interface"):
            capture = False

        if capture:
            f.write(line + "\n")

            match = re.match(r'^\s+DNS Servers.*:\s(.*)$', line)
            if match:
                dns_server = match.group(1)

            match = re.match(r'^\s+Default Gateway.*:\s(.*)$', line)
            if match:
                default_gateway = match.group(1)

    f.write("\n")
    return (default_gateway, dns_server)

def modem_information():
    f.write("MODEM INFORMATION:\n")
    subprocess.Popen('"c:/Program Files/Mozilla Firefox/firefox.exe" "http://192.168.100.1/index.html#status_docsis/m/1/s/2"')
    print("Info: ")
    f.write(readlines_stdin())
    f.write("\n\n")

def factory_reset():
    f.write("AFTER FACTORY RESET:\n")
    f.write("DNS is set to obtain automatically\n")
    input("Perform Factory Reset and press Enter to continue")
    f.write("\n\n")

def ping_tests(default_gateway, dns_server):
    f.write("PING TESTS:\n")
    default_gateway_results = do_command('ping -n 50', default_gateway)
    dns_server_results = do_command('ping -n 50', dns_server)
    google_results = do_command('ping -n 50', 'google.ca')

    print_results(default_gateway_results, 'Default Gateway')
    print_results(dns_server_results, 'DNS Server')
    print_results(google_results, 'google.ca')

def traceroute_tests(dns_server):
    f.write("TRACE ROUTE TESTS:\n")
    dns_server_results = do_command('tracert', dns_server)
    google_results = do_command('tracert', 'google.ca')

    print_results(dns_server_results, 'DNS Server')
    print_results(google_results, 'google.ca')

def print_results(results, title):
    f.write(title + ":")
    ping_output = results.stdout.readlines()
    for line in ping_output:
        f.write(str(line).rstrip("\\r\\n'").lstrip("b'") + '\n')
    f.write("\n")

def do_command(cmd, server):
    cmd = cmd + ' ' + server
    print(cmd)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)

if __name__ == '__main__':
    os.makedirs('documents', exist_ok=True)
    with open("documents/" + _today.isoformat() + "_issue.txt", 'w') as f:
        preamble()
        speed_test()
        ipconfig()
        modem_information()
        f.flush()

        factory_reset()

        speed_test()
        _default_gateway, _dns_server = ipconfig()
        modem_information()
        f.flush()
        ping_tests(_default_gateway, _dns_server)
        traceroute_tests(_dns_server)
