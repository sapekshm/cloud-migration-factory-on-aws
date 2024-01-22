#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: Apache-2.0


import sys
if not sys.warnoptions:
    import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=Warning)
    import paramiko


def execute_cmd(host, username, key, cmd, using_key):
    output = ''
    error = ''
    ssh = None
    try:
        ssh = open_ssh(host, username, key, using_key)
        if ssh is None:
            error = "Not able to get the SSH connection for the host " + host
            print(error)
        else:
            stdin, stdout, stderr = ssh.exec_command(cmd)  # nosec B601
            for line in stdout.readlines():
                output = output + line
            for line in stderr.readlines():
                error = error + line
    except IOError as io_error:
        error = "Unable to execute the command " + cmd + " due to " + \
                str(io_error)
        print(error)
    except paramiko.SSHException as ssh_exception:
        error = "Unable to execute the command " + cmd + " due to " + \
                str(ssh_exception)
        print(error)
    finally:
        if ssh is not None:
            ssh.close()
    return output, error


def open_ssh(host, username, key_pwd, using_key):
    ssh = None
    try:
        if using_key:
            from io import StringIO
            private_key = paramiko.RSAKey.from_private_key(StringIO(key_pwd))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, pkey=private_key)
        else:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, password=key_pwd)
    except IOError as io_error:
        error = "Unable to connect to host " + host + " with username " + \
                username + " due to " + str(io_error)
        print(error)
    except paramiko.SSHException as ssh_exception:
        error = "Unable to connect to host " + host + " with username " + \
                username + " due to " + str(ssh_exception)
        print(error)
    return ssh


def find_distribution(host, username, key_pwd, using_key):
    distribution = "linux"
    output, error = execute_cmd(host, username, key_pwd, "cat /etc/*release",
                                using_key)
    if "ubuntu" in output:
        distribution = "ubuntu"
    elif "fedora" in output:
        distribution = "fedora"
    elif "suse" in output:
        distribution = "suse"
    return distribution

def uninstall_ads(host, username, key_pwd, using_key):
    print("")
    print("--------------------------------------------------------------------")
    print("- Uninstalling Application Discovery Service Agent for:  "+ host + " -")
    print("--------------------------------------------------------------------")
    try:
        output = None
        error = None
        # Step 1 - run uninstall
        command = "sudo rpm -e --nodeps aws-discovery-agent"
        print("Executing " + command)
        output, error1 = execute_cmd(host=host, username=username, key=key_pwd,
                                cmd=command, using_key=using_key)
        print(output)
        command = "sudo apt-get remove aws-discovery-agent:i386"
        print("Executing " + command)
        output, error2 = execute_cmd(host=host, username=username, key=key_pwd,
                                cmd=command, using_key=using_key)
        print(output)

        command = "sudo zypper remove aws-discovery-agent"
        print("Executing " + command)
        output, error3 = execute_cmd(host=host, username=username, key=key_pwd,
                                cmd=command, using_key=using_key)
        print(output)

    except Exception as e:
        error = 'Got exception! ' + str(e)
    if (error1 == '' or error2 == '' or error3 == '' or 'warning: /etc/opt/aws/discovery/config saved as /etc/opt/aws/discovery/config.rpmsave' in error1) and 'Error: Uninstallation failed' not in output:
        print("***** Agent uninstallation completed successfully on "
              +host+ "*****")
        return True
    else:
        print("An error was returned from the uninstall command on "+host+" due to: ")
        print("")
        print('rpm: ' + error1 + ', apt-get: ' + error2 + ', zypper: ' + error3)
        return False
