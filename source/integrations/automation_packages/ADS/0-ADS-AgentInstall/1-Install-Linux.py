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


def install_wget(host, username, key_pwd, using_key):
    ssh = None
    try:
        # Find the distribution
        distribution = find_distribution(host, username, key_pwd, using_key)
        print("")
        print("***** Installing wget *****")
        ssh = open_ssh(host, username, key_pwd, using_key)
        if distribution == "ubuntu":
            ssh.exec_command("sudo apt-get update")  # nosec B601
            stdin, stdout, stderr = ssh.exec_command(  # nosec B601
                "sudo DEBIAN_FRONTEND=noninteractive apt-get install wget")  # nosec B601
        elif distribution == "suse":
            stdin, stdout, stderr = ssh.exec_command("sudo zypper install wget")  # nosec B601
            stdin.write('Y\n')
            stdin.flush()
        else:
            # This condition works with centos, fedora and RHEL distributions
            # ssh.exec_command("sudo yum update")  # nosec B601
            stdin, stdout, stderr = ssh.exec_command("sudo yum install wget -y")  # nosec B601
        # Check if there is any error while installing wget
        error = ''
        for line in stderr.readlines():
            error = error + line
        if not error:
            print("wget got installed successfully")
            # Execute the command wget and check if it got configured correctly
            stdin, stdout, stderr = ssh.exec_command("wget")  # nosec B601
            error = ''
            for line in stderr.readlines():
                error = error + line
            if "not found" in error or "command-not-found" in error:
                print(
                    "wget is not recognized, unable to proceed! due to " + error)
        else:
            print("something went wrong while installing wget ", error)
    finally:
        if ssh is not None:
            ssh.close()

def install_ads(agent_linux_download_url, region, host, username, key_pwd, using_key, AccessKeyId, SecretAccessKey):
    print("")
    print("--------------------------------------------------------------------")
    print("- Installing Application Discovery Service Agent for:  "+ host + " -")
    print("--------------------------------------------------------------------")
    try:
        output = None
        error = None
        # Step 2 - download linux installer
        command = "wget -O ./aws-discovery-agent.tar.gz " + agent_linux_download_url
        output, error = execute_cmd(host=host, username=username, key=key_pwd,
                                cmd=command, using_key=using_key)
        if "not found" in error or "No such file or directory" in error:
            install_wget(host, username, key_pwd, using_key)
            output, error = execute_cmd(host=host, username=username, key=key_pwd,
                                    cmd=command, using_key=using_key)
        # Step 2 - extract linux installer
        command = "tar -xzf aws-discovery-agent.tar.gz"
        display_command = "tar -xzf aws-discovery-agent.tar.gz"
        print("Executing " + display_command)
        output, error = execute_cmd(host=host, username=username, key=key_pwd,
                                cmd=command, using_key=using_key)
        print(output)
        # Step 3 - execute linux installer
        command = "sudo bash install -r " + \
              region + " -k \"" + AccessKeyId + "\" -s \"" + SecretAccessKey + "\""
        display_command = "sudo bash install -r " + \
              region + " -k " + AccessKeyId + " -s *************"
        print("Executing " + display_command)
        output, error = execute_cmd(host=host, username=username, key=key_pwd,
                                cmd=command, using_key=using_key)
        print(output)
    except Exception as e:
        error = 'Got exception! ' + str(e)
    if (error == '' or 'Created symlink from' in error) and 'Error: Installation failed' not in output:
        print("***** Agent installation completed successfully on "
              +host+ "*****")
        return True
    else:
        print("Unable to install Agent on "+host+" due to: ")
        print("")
        print(error)
        return False
