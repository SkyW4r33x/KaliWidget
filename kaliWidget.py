#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author: Jordan aka SkyW4r33x
# Repository: https://github.com/tuusuario/KaliWidget
# Description: XFCE extension for TARGET, VPN, ETHERNET panel integration
# Version: 2.3.0 (Fixed)

import os
import subprocess
import sys
import shutil
import time
from pathlib import Path
import logging
import getpass
import re

# ------------------------------- Kali Style Class --------------------------- #

class KaliStyle:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BLUE = '\033[38;2;39;127;255m'  
    TURQUOISE = '\033[38;2;71;212;185m' 
    ORANGE = '\033[38;2;255;138;24m' 
    WHITE = '\033[37m'
    GREY = '\033[38;5;242m'
    RED = '\033[38;2;220;20;60m'  
    GREEN = '\033[38;2;71;212;185m' 
    YELLOW = '\033[0;33m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    SUDO_COLOR = '\033[38;2;94;189;171m' 
    APT_COLOR = '\033[38;2;73;174;230m' 
    SUCCESS = f"   {TURQUOISE}{BOLD}✔{RESET}"
    ERROR = f"   {RED}{BOLD}✘{RESET}"
    INFO = f"{BLUE}{BOLD}[i]{RESET}"
    WARNING = f"{YELLOW}{BOLD}[!]{RESET}"

# ------------------------------- XFCE Installer Class --------------------------- #

class XfceInstaller:

    def __init__(self):
        if os.getuid() == 0:
            print(f"{KaliStyle.ERROR} Do not run this script with sudo or as root. Use a normal user.")
            sys.exit(1)
        
        original_user = os.environ.get('SUDO_USER', os.environ.get('USER') or Path.home().name)
        self.home_dir = os.path.expanduser(f'~{original_user}')
        self.current_user = original_user
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.actions_taken = []
        self.sudo_password = None
        
        log_path = os.path.join(self.script_dir, 'install.log')
        if os.path.exists(log_path) and not os.access(log_path, os.W_OK):
            print(f"{KaliStyle.WARNING} Fixing permissions on {log_path}...")
            try:
                subprocess.run(['sudo', 'rm', '-f', log_path], check=True, timeout=30)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print(f"{KaliStyle.WARNING} Could not fix log permissions, creating new log")
                log_path = os.path.join(self.script_dir, f'install_{int(time.time())}.log')
        
        logging.basicConfig(filename=log_path, level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def show_banner(self):
        print(f"""\n{KaliStyle.BLUE}{KaliStyle.BOLD}
            ██╗  ██╗ █████╗ ██╗     ██╗
            ██║ ██╔╝██╔══██╗██║     ██║
            █████╔╝ ███████║██║     ██║
            ██╔═██╗ ██╔══██║██║     ██║
            ██║  ██╗██║  ██║███████╗██║
            ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝
           """)
        print(f"""{KaliStyle.WHITE}{KaliStyle.BOLD}
    ██╗    ██╗██╗██████╗  ██████╗ ███████╗████████╗
    ██║    ██║██║██╔══██╗██╔════╝ ██╔════╝╚══██╔══╝
    ██║ █╗ ██║██║██║  ██║██║  ███╗█████╗     ██║   
    ██║██╗ ██║██║██║  ██║██║   ██║██╔══╝     ██║   
    ╚███╔███╔╝██║██████╔╝╚██████╔╝███████╗   ██║   
     ╚══╝╚══╝ ╚═╝╚═════╝  ╚═════╝ ╚══════╝   ╚═╝
           """)
        print(f"{KaliStyle.WHITE}\t    [ XFCE Installer - v.2.3.0 ]{KaliStyle.RESET}")
        print(f"{KaliStyle.GREY}\t      [ Created by SkyW4r33x ]{KaliStyle.RESET}\n")

    def get_sudo_password(self):
        if self.sudo_password is None:
            self.sudo_password = getpass.getpass(prompt=f"{KaliStyle.INFO} Enter password: ")
        return self.sudo_password

    def run_command(self, command, shell=False, sudo=False, quiet=True, timeout=60):
        try:
            if sudo and not shell:
                if self.sudo_password is None:
                    self.get_sudo_password()
                
                cmd = ['sudo', '-S'] + command
                result = subprocess.run(
                    cmd,
                    shell=shell,
                    check=True,
                    input=self.sudo_password + '\n',
                    stdout=subprocess.PIPE if quiet else None,
                    stderr=subprocess.PIPE if quiet else None,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    command,
                    shell=shell,
                    check=True,
                    stdout=subprocess.PIPE if quiet else None,
                    stderr=subprocess.PIPE if quiet else None,
                    text=True,
                    timeout=timeout
                )
            return True, result.stdout if quiet else ""
        except subprocess.CalledProcessError as e:
            if not quiet:
                print(f"{KaliStyle.ERROR} Error executing command: {' '.join(command)}")
                if hasattr(e, 'stdout') and e.stdout:
                    print(f"Output: {e.stdout}")
                if hasattr(e, 'stderr') and e.stderr:
                    print(f"Error: {e.stderr}")
            logging.error(f"Error executing command: {' '.join(command)} - {e}")
            return False, ""
        except subprocess.TimeoutExpired:
            print(f"{KaliStyle.ERROR} Command timeout: {' '.join(command)}")
            logging.error(f"Command timeout: {' '.join(command)}")
            return False, ""
        except PermissionError:
            print(f"{KaliStyle.ERROR} Insufficient permissions to execute: {' '.join(command)}")
            logging.error(f"Permission error: {' '.join(command)}")
            return False, ""

    def check_command(self, command):
        try:
            result = subprocess.run([command, "--version"], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def check_os(self):
        if not os.path.exists('/etc/debian_version'):
            print(f"{KaliStyle.ERROR} This script is designed for Debian/Kali based systems")
            return False
        return True

    def check_sudo_privileges(self):
        try:
            result = subprocess.run(['sudo', '-n', 'true'], 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  timeout=10)
            if result.returncode == 0:
                return True
            else:
                print(f"{KaliStyle.WARNING} This script needs to execute commands with sudo.")
                return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Could not verify sudo privileges: {str(e)}")
            return False

    def check_required_files(self):
        required_files = ["bin"]
        missing = []
        
        for f in required_files:
            path = os.path.join(self.script_dir, f)
            if not os.path.exists(path):
                missing.append(f)
            elif not os.access(path, os.R_OK):
                print(f"{KaliStyle.ERROR} No read permissions for {f}")
                missing.append(f)
        
        if missing:
            print(f"{KaliStyle.ERROR} Missing required files: {', '.join(missing)}")
            print(f"{KaliStyle.INFO} Make sure they are in {self.script_dir}")
            return False
        return True

    def check_xfce_environment(self):
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session_type = os.environ.get('XDG_SESSION_DESKTOP', '').lower()
        
        if "xfce" not in desktop_env and "xfce" not in session_type:
            print(f"{KaliStyle.WARNING} This script is designed for XFCE environments.")
            print(f"{KaliStyle.INFO} Current desktop: {desktop_env or 'unknown'}")
            response = input(f"{KaliStyle.WARNING} Continue anyway? [y/N]: ").lower()
            if response != 'y':
                return False
        return True

    def install_additional_packages(self):
        print(f"\n{KaliStyle.INFO} Installing tools")
        self.packages = ['jp2a', 'xclip']
        self.max_length = max(len(pkg) for pkg in self.packages)
        self.state_length = 20
        self.states = {pkg: f"{KaliStyle.GREY}Pending{KaliStyle.RESET}" for pkg in self.packages}
        
        def print_status(first_run=False):
            if not first_run:
                print(f"\033[{len(self.packages) + 1}A", end="")
            
            print(f"{KaliStyle.INFO} Installing packages:")
            for pkg, state in self.states.items():
                print(f"\033[K", end="")
                print(f"  {KaliStyle.YELLOW}•{KaliStyle.RESET} {pkg:<{self.max_length}} {state}")
            sys.stdout.flush()

        try:
            self.get_sudo_password()

            print(f"{KaliStyle.INFO} Updating repositories...")
            success, _ = self.run_command(['apt', 'update'], sudo=True, quiet=True)
            if not success:
                print(f"{KaliStyle.ERROR} Error updating repositories")
                return False
            print(f"{KaliStyle.SUCCESS} Repositories updated")

            print_status(first_run=True)
            failed_packages = []
            
            for pkg in self.packages:
                check_result = subprocess.run(['dpkg-query', '-s', pkg], 
                                            stdout=subprocess.DEVNULL, 
                                            stderr=subprocess.DEVNULL)
                if check_result.returncode == 0:
                    self.states[pkg] = f"{KaliStyle.GREY}Already installed{KaliStyle.RESET}"
                    print_status()
                    continue
                
                self.states[pkg] = f"{KaliStyle.YELLOW}Installing...{KaliStyle.RESET}"
                print_status()
                
                success, _ = self.run_command(['apt', 'install', '-y', pkg], sudo=True, quiet=True)
                if success:
                    self.states[pkg] = f"{KaliStyle.GREEN}Completed{KaliStyle.RESET}"
                    self.actions_taken.append({'type': 'package', 'pkg': pkg})
                else:
                    self.states[pkg] = f"{KaliStyle.RED}Failed{KaliStyle.RESET}"
                    failed_packages.append(pkg)
                    print(f"{KaliStyle.WARNING} Warning: Failed to install {pkg}, continuing...")
                
                print_status()
                time.sleep(0.2)
            
            if failed_packages:
                print(f"\n{KaliStyle.WARNING} The following packages failed: {', '.join(failed_packages)}")
                print(f"{KaliStyle.INFO} Check install.log for more details.")
            else:
                print(f"\n{KaliStyle.SUCCESS} Installation completed")
            return True
            
        except Exception as e:
            print(f"\n{KaliStyle.ERROR} Error installing packages: {str(e)}")
            logging.error(f"General error in install_additional_packages: {str(e)}")
            return False

    def copy_files(self):
        print(f"\n{KaliStyle.INFO} Copying files...")
        source_bin = os.path.join(self.script_dir, "bin")
        dest_bin = os.path.join(self.home_dir, '.config/bin')
        
        if os.path.exists(dest_bin):
            print(f"{KaliStyle.WARNING} Bin directory already exists, backing up...")
            backup_dir = f"{dest_bin}.backup.{int(time.time())}"
            try:
                shutil.move(dest_bin, backup_dir)
                self.actions_taken.append({'type': 'backup', 'original': dest_bin, 'backup': backup_dir})
                print(f"{KaliStyle.INFO} Backup created at {backup_dir}")
            except Exception as e:
                print(f"{KaliStyle.ERROR} Error creating backup: {str(e)}")
                return False
        
        try:
            os.makedirs(os.path.dirname(dest_bin), exist_ok=True)
            shutil.copytree(source_bin, dest_bin)
            self.actions_taken.append({'type': 'dir_copy', 'dest': dest_bin})
            print(f"{KaliStyle.SUCCESS} Files copied")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error copying files: {str(e)}")
            logging.error(f"Error copying files: {str(e)}")
            return False

    def set_permissions(self):
        print(f"\n{KaliStyle.INFO} Setting permissions...")
        scripts = [
            os.path.join(self.home_dir, '.config/bin/target.sh'),
            os.path.join(self.home_dir, '.config/bin/ethernet.sh'),
            os.path.join(self.home_dir, '.config/bin/vpnip.sh')
        ]
        
        for script in scripts:
            if not os.path.exists(script):
                print(f"{KaliStyle.WARNING} Script not found: {os.path.basename(script)}")
                continue
                
            try:
                os.chmod(script, 0o755)
                print(f"{KaliStyle.SUCCESS} Permissions set for {os.path.basename(script)}")
            except Exception as e:
                print(f"{KaliStyle.ERROR} Error setting permissions for {script}: {str(e)}")
                logging.error(f"Error setting permissions: {str(e)}")
                return False
        return True

    def add_settarget_function(self):
        print(f"\n{KaliStyle.INFO} Adding settarget function...")
        shell = os.environ.get('SHELL', '').split('/')[-1]
        
        if shell == 'zsh':
            rc_file = '.zshrc'
        elif shell == 'bash':
            rc_file = '.bashrc'
        else:
            print(f"{KaliStyle.WARNING} Shell '{shell}' not supported (only Bash/Zsh). Trying .bashrc...")
            rc_file = '.bashrc'

        rc_path = os.path.join(self.home_dir, rc_file)
        
        if not os.path.exists(rc_path):
            try:
                Path(rc_path).touch()
                print(f"{KaliStyle.INFO} Created {rc_file}")
            except Exception as e:
                print(f"{KaliStyle.ERROR} Could not create {rc_file}: {str(e)}")
                return False

        function_text = f"""
# ------------------------------- settarget Function --------------------------- #
function settarget() {{
    local WHITE='\\033[1;37m'
    local GREEN='\\033[0;32m'
    local YELLOW='\\033[1;33m'
    local RED='\\033[0;31m'
    local BLUE='\\033[0;34m'
    local CYAN='\\033[1;36m'
    local PURPLE='\\033[1;35m'
    local GRAY='\\033[38;5;244m'
    local BOLD='\\033[1m'
    local ITALIC='\\033[3m'
    local COMAND='\\033[38;2;73;174;230m'
    local NC='\\033[0m'
    
    local target_file="{self.home_dir}/.config/bin/target/target.txt"
    
    mkdir -p "$(dirname "$target_file")" 2>/dev/null
    
    if [ $# -eq 0 ]; then
        if [ -f "$target_file" ]; then
            rm -f "$target_file"
            echo -e "\\n${{CYAN}}[${{BOLD}}+${{NC}}${{CYAN}}]${{NC}} Target limpiado correctamente\\n"
        else
            echo -e "\\n${{YELLOW}}[${{BOLD}}!${{NC}}${{YELLOW}}]${{NC}} No hay target para limpiar\\n"
        fi
        return 0
    fi
    
    local ip_address="$1"
    local machine_name="$2"
    
    if [ -z "$ip_address" ] || [ -z "$machine_name" ]; then
        echo -e "\\n${{RED}}▋${{NC}} Error${{RED}}${{BOLD}}:${{NC}}${{ITALIC}} modo de uso.${{NC}}"
        echo -e "${{GRAY}}—————————————————————${{NC}}"
        echo -e "  ${{CYAN}}• ${{NC}}${{COMAND}}settarget ${{NC}}192.168.1.100 WebServer "
        echo -e "  ${{CYAN}}• ${{NC}}${{COMAND}}settarget ${{GRAY}}${{ITALIC}}(limpiar target)${{NC}}\\n"
        return 1
    fi
    
    if ! echo "$ip_address" | grep -qE '^[0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}}$'; then
        echo -e "\\n${{RED}}▋${{NC}} Error${{RED}}${{BOLD}}:${{NC}}"
        echo -e "${{GRAY}}————————${{NC}}"
        echo -e "${{RED}}[${{BOLD}}✘${{NC}}${{RED}}]${{NC}} Formato de IP inválido ${{YELLOW}}→${{NC}} ${{RED}}$ip_address${{NC}}"
        echo -e "${{BLUE}}${{BOLD}}[+] ${{NC}}Ejemplo válido:${{NC}} ${{GRAY}}192.168.1.100${{NC}}\\n"
        return 1
    fi
    
    if ! echo "$ip_address" | awk -F'.' '{{ 
        for(i=1; i<=4; i++) {{ 
            if($i < 0 || $i > 255) exit 1
            if(length($i) > 1 && substr($i,1,1) == "0") exit 1
        }}
    }}'; then
        echo -e "\\n${{RED}}[${{BOLD}}✘${{NC}}${{RED}}]${{NC}} IP inválida ${{RED}}→${{NC}} ${{BOLD}}$ip_address${{NC}}"
        return 1
    fi
    
    echo "$ip_address $machine_name" > "$target_file"
    
    if [ $? -eq 0 ]; then
        echo -e "\\n${{YELLOW}}▌${{NC}} Target establecido correctamente${{YELLOW}}${{BOLD}}:${{NC}}"
        echo -e "${{GRAY}}—————————————————————————————————${{NC}}"
        echo -e "${{CYAN}}→${{NC}} IP Address:${{GRAY}}...........${{NC}} ${{GREEN}}$ip_address${{NC}}"
        echo -e "${{CYAN}}→${{NC}} Machine Name:${{GRAY}}.........${{NC}} ${{GREEN}}$machine_name${{NC}}\\n"
    else
        echo -e "\\n${{RED}}[${{BOLD}}✘${{NC}}${{RED}}]${{NC}} No se pudo guardar el target\\n"
        return 1
    fi
    
    return 0
}}
"""
        try:
            if os.path.exists(rc_path):
                with open(rc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'function settarget()' in content or 'XFCE Installer: settarget function' in content:
                        print(f"{KaliStyle.WARNING} Function already exists in {rc_file}. Skipping.")
                        return True
            
            if os.path.exists(rc_path) and not os.access(rc_path, os.W_OK):
                print(f"{KaliStyle.ERROR} No write permissions for {rc_file}. Check permissions.")
                logging.error(f"No write permissions for {rc_path}")
                return False
            
            with open(rc_path, 'a', encoding='utf-8') as f:
                f.write(function_text)
            
            self.actions_taken.append({'type': 'file_append', 'dest': rc_path, 'content': function_text})
            print(f"{KaliStyle.SUCCESS} Function added to {rc_file}")
            return True
            
        except IOError as e:
            print(f"{KaliStyle.ERROR} Error writing to {rc_file}: {e}")
            logging.error(f"Error adding function: {str(e)}")
            return False

    def remove_existing_genmon(self):
        print(f"\n{KaliStyle.INFO} Removing existing genmon plugins...")
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                print(f"{KaliStyle.WARNING} No plugins found or xfconf-query failed.")
                return True
        except Exception as e:
            print(f"{KaliStyle.WARNING} Error querying plugins: {str(e)}")
            return True

        genmon_ids = []
        for line in output.splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                path, value = parts
                if path.startswith('/plugins/plugin-') and value.strip() == 'genmon':
                    match = re.match(r'/plugins/plugin-(\d+)', path)
                    if match:
                        id_ = int(match.group(1))
                        genmon_ids.append(id_)

        for id_ in genmon_ids:
            success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{id_}', '-r', '-R'])
            if success:
                print(f"{KaliStyle.SUCCESS} Removed genmon plugin {id_}")

        try:
            success, panels_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels'])
            if success:
                panels = [int(l.strip()) for l in panels_output.splitlines() if l.strip().isdigit()]
            else:
                panels = [1]
        except Exception:
            panels = [1]

        for p in panels:
            try:
                success, ids_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids'])
                if success and ids_output.strip():
                    current_ids = [int(l.strip()) for l in ids_output.splitlines() if l.strip().isdigit()]
                    new_ids = [i for i in current_ids if i not in genmon_ids]
                    if len(new_ids) < len(current_ids):
                        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '-r'])
                        if new_ids:
                            args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '--create', '-a']
                            for i in new_ids:
                                args += ['-t', 'int', '-s', str(i)]
                            self.run_command(args)
            except Exception as e:
                logging.warning(f"Error updating panel {p}: {str(e)}")
                continue

        print(f"{KaliStyle.SUCCESS} Existing genmon plugins removed")
        return True

    def find_and_remove_cpugraph(self):
        print(f"\n{KaliStyle.INFO} Removing CPU Graph...")
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v'])
            if not success:
                return 1, None
        except Exception:
            return 1, None

        cpugraph_id = None
        for line in output.splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                path, value = parts
                if value.strip() == 'cpugraph':
                    match = re.match(r'/plugins/plugin-(\d+)', path)
                    if match:
                        cpugraph_id = int(match.group(1))
                        break

        if not cpugraph_id:
            print(f"{KaliStyle.WARNING} No CPU Graph found.")
            return 1, None

        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{cpugraph_id}', '-r', '-R'])

        try:
            success, panels_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels'])
            if success:
                panels = [int(l.strip()) for l in panels_output.splitlines() if l.strip().isdigit()]
            else:
                panels = [1]
        except Exception:
            panels = [1]

        panel_id = 1
        insert_index = None
        
        for p in panels:
            try:
                success, ids_output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids'])
                if success and ids_output.strip():
                    current_ids = [int(l.strip()) for l in ids_output.splitlines() if l.strip().isdigit()]
                    if cpugraph_id in current_ids:
                        insert_index = current_ids.index(cpugraph_id)
                        panel_id = p
                        new_ids = [i for i in current_ids if i != cpugraph_id]
                        
                        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '-r'])
                        if new_ids:
                            args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '--create', '-a']
                            for i in new_ids:
                                args += ['-t', 'int', '-s', str(i)]
                            self.run_command(args)
                        break
            except Exception as e:
                logging.warning(f"Error processing panel {p}: {str(e)}")
                continue

        print(f"{KaliStyle.SUCCESS} CPU Graph removed")
        return panel_id, insert_index

    def add_genmon_to_panel(self, command, period='0.25', title=''):
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l'])
            if success:
                ids = set()
                for line in output.splitlines():
                    match = re.match(r'/plugins/plugin-(\d+)(/.*)?$', line)
                    if match:
                        ids.add(int(match.group(1)))
                next_id = max(ids) + 1 if ids else 1
            else:
                next_id = 1
        except Exception:
            next_id = 1

        success, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}', '-t', 'string', '-s', 'genmon', '--create'])
        if not success:
            print(f"{KaliStyle.WARNING} Failed to create genmon plugin {next_id}")
            return None

        rc_dir = os.path.join(self.home_dir, '.config/xfce4/panel')
        os.makedirs(rc_dir, exist_ok=True)
        rc_file = os.path.join(rc_dir, f'genmon-{next_id}.rc')
        
        try:
            with open(rc_file, 'w', encoding='utf-8') as f:
                f.write(f'Command={command}\n')
                f.write(f'UpdatePeriod={int(float(period) * 1000)}\n')
                f.write(f'Text={title}\n')
                f.write('UseLabel=0\n')
                f.write('Font=Cantarell Ultra-Bold 10\n')

            self.actions_taken.append({'type': 'file_copy', 'dest': rc_file})
            return next_id
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error creating genmon config: {str(e)}")
            return None

    def add_separator_to_panel(self):
        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l'])
            if success:
                ids = set()
                for line in output.splitlines():
                    match = re.match(r'/plugins/plugin-(\d+)(/.*)?$', line)
                    if match:
                        ids.add(int(match.group(1)))
                next_id = max(ids) + 1 if ids else 1
            else:
                next_id = 1
        except Exception:
            next_id = 1

        success1, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}', '-t', 'string', '-s', 'separator', '--create'])
        success2, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}/style', '-t', 'int', '-s', '0', '--create'])
        success3, _ = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}/expand', '-t', 'bool', '-s', 'false', '--create'])

        if not (success1 and success2 and success3):
            print(f"{KaliStyle.WARNING} Failed to create separator plugin {next_id}")
            return None

        return next_id

    def insert_panel_plugin_ids(self, new_ids, panel_id=1, insert_index=None):
        new_ids = [id_ for id_ in new_ids if id_ is not None]
        if not new_ids:
            print(f"{KaliStyle.WARNING} No valid plugin IDs to insert")
            return False

        try:
            success, output = self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids'])
            if success and output.strip():
                current_ids = [int(l.strip()) for l in output.splitlines() if l.strip().isdigit()]
            else:
                current_ids = []
        except Exception:
            current_ids = []

        if insert_index is None or insert_index > len(current_ids):
            insert_index = len(current_ids)

        updated_ids = current_ids[:insert_index] + new_ids + current_ids[insert_index:]

        self.run_command(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids', '-r'])
        
        if updated_ids:
            args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids', '--create', '-a']
            for id_ in updated_ids:
                args += ['-t', 'int', '-s', str(id_)]
            success, _ = self.run_command(args)
            return success
        
        return True

    def add_plugins_to_panel(self, panel_id, insert_index):
        print(f"\n{KaliStyle.INFO} Adding plugins to XFCE panel...")
        
        target_path = os.path.join(self.home_dir, '.config/bin/target.sh')
        vpn_path = os.path.join(self.home_dir, '.config/bin/vpnip.sh')
        ethernet_path = os.path.join(self.home_dir, '.config/bin/ethernet.sh')
        
        missing_scripts = []
        for script, name in [(target_path, 'target.sh'), (vpn_path, 'vpnip.sh'), (ethernet_path, 'ethernet.sh')]:
            if not os.path.exists(script):
                missing_scripts.append(name)
        
        if missing_scripts:
            print(f"{KaliStyle.WARNING} Missing scripts: {', '.join(missing_scripts)}")
            print(f"{KaliStyle.INFO} Continuing with available scripts...")
        
        new_ids = []
        
        if os.path.exists(target_path):
            target_id = self.add_genmon_to_panel(target_path, '0.25', '')
            if target_id:
                new_ids.append(target_id)
                new_ids.append(self.add_separator_to_panel())
        
        if os.path.exists(vpn_path):
            vpn_id = self.add_genmon_to_panel(vpn_path, '0.25', '')
            if vpn_id:
                new_ids.append(vpn_id)
                new_ids.append(self.add_separator_to_panel())
        
        if os.path.exists(ethernet_path):
            ethernet_id = self.add_genmon_to_panel(ethernet_path, '0.25', '')
            if ethernet_id:
                new_ids.append(ethernet_id)
        
        if new_ids:
            success = self.insert_panel_plugin_ids(new_ids, panel_id, insert_index)
            if success:
                print(f"{KaliStyle.SUCCESS} Plugins added successfully")
                return True
            else:
                print(f"{KaliStyle.ERROR} Failed to add plugins to panel")
                return False
        else:
            print(f"{KaliStyle.WARNING} No plugins were added due to missing scripts")
            return False

    def restart_panel(self):
        print(f"\n{KaliStyle.INFO} Restarting XFCE panel...")
        try:
            subprocess.run(['pkill', 'xfce4-panel'], stderr=subprocess.DEVNULL)
            time.sleep(1)
            
            subprocess.Popen(['xfce4-panel'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            
            print(f"{KaliStyle.SUCCESS} Panel restarted")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error restarting panel: {str(e)}")
            print(f"{KaliStyle.INFO} You may need to restart manually: xfce4-panel --restart")
            logging.error(f"Error restarting panel: {str(e)}")
            return True

    def check_previous_installation(self):
        config_bin_path = os.path.join(self.home_dir, '.config/bin')
        if os.path.exists(config_bin_path):
            print(f"{KaliStyle.WARNING} Previous installation detected.")
            print(f"{KaliStyle.INFO} Directory: {config_bin_path}")
            
            while True:
                resp = input(f"{KaliStyle.WARNING} Reinstall? This will backup existing files [Y/n]: ").lower().strip()
                if resp in ['y', 'yes', '']:
                    return True
                elif resp in ['n', 'no']:
                    print(f"{KaliStyle.INFO} Installation cancelled.")
                    sys.exit(0)
                else:
                    print(f"{KaliStyle.ERROR} Please answer 'y' or 'n'")
        return True

    def cleanup(self):
        #print(f"\n{KaliStyle.INFO} Cleaning up...")
        
        try:
            config_bin = os.path.join(self.home_dir, '.config/bin')
            if os.path.exists(config_bin):
                import pwd
                user_info = pwd.getpwnam(self.current_user)
                uid, gid = user_info.pw_uid, user_info.pw_gid
                
                for root, dirs, files in os.walk(config_bin):
                    os.chown(root, uid, gid)
                    for file in files:
                        os.chown(os.path.join(root, file), uid, gid)
                    for dir in dirs:
                        os.chown(os.path.join(root, dir), uid, gid)
        except Exception as e:
            logging.warning(f"Could not set proper ownership: {str(e)}")
        
        #print(f"{KaliStyle.SUCCESS} Cleanup completed")
        return True

    def rollback(self):
        print(f"{KaliStyle.WARNING} Rolling back changes...")
        
        for action in reversed(self.actions_taken):
            try:
                if action['type'] == 'file_copy' or action['type'] == 'file_create':
                    if os.path.exists(action['dest']):
                        os.remove(action['dest'])
                        print(f"{KaliStyle.SUCCESS} Deleted {action['dest']}")
                
                elif action['type'] == 'dir_copy':
                    if os.path.exists(action['dest']):
                        shutil.rmtree(action['dest'])
                        print(f"{KaliStyle.SUCCESS} Deleted directory {action['dest']}")
                
                elif action['type'] == 'backup':
                    if os.path.exists(action['backup']):
                        if os.path.exists(action['original']):
                            shutil.rmtree(action['original'])
                        shutil.move(action['backup'], action['original'])
                        print(f"{KaliStyle.SUCCESS} Restored {action['original']} from backup")
                
                elif action['type'] == 'package':
                    print(f"{KaliStyle.WARNING} Removing package {action['pkg']}...")
                    if self.sudo_password:
                        self.run_command(['apt', 'remove', '-y', action['pkg']], sudo=True, quiet=True)
                
                elif action['type'] == 'file_append':
                    if os.path.exists(action['dest']) and 'content' in action:
                        try:
                            with open(action['dest'], 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            new_content = content.replace(action['content'], '')
                            
                            with open(action['dest'], 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"{KaliStyle.SUCCESS} Removed content from {action['dest']}")
                        except Exception as e:
                            print(f"{KaliStyle.WARNING} Manual cleanup needed for {action['dest']}: {str(e)}")
            
            except Exception as e:
                print(f"{KaliStyle.WARNING} Could not rollback {action}: {str(e)}")
                logging.error(f"Rollback error: {str(e)}")
        
        print(f"{KaliStyle.SUCCESS} Rollback completed")

    def show_final_message(self):
        time.sleep(2)
        os.system('clear')
        print(f"\n\t\t[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Installation Summary [{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}]\n")

        print(f"[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Installed Features\n")
        features = [
            ("Target Monitor", "Panel plugin for target IP display."),
            ("VPN IP Monitor", "Panel plugin for VPN IP display."),
            ("Ethernet IP Monitor", "Panel plugin for Ethernet IP display."),
            ("settarget Function", "Shell function to set target easily.")
        ]
        
        for name, desc in features:
            print(f"   {KaliStyle.YELLOW}▸{KaliStyle.RESET} {KaliStyle.WHITE}{name:<20}{KaliStyle.RESET} {KaliStyle.GREY}→{KaliStyle.RESET} {desc}")
        
        print(f"\n{KaliStyle.TURQUOISE}{'═' * 60}{KaliStyle.RESET}")
        print(f"\n{KaliStyle.WARNING}{KaliStyle.BOLD} Important Notes:{KaliStyle.RESET}")
        print(f"  • Click on IP addresses to copy them to clipboard")
        print(f"  • Use {KaliStyle.APT_COLOR}settarget{KaliStyle.RESET} <IP> <Name> to set target")
        print(f"  • Example: {KaliStyle.APT_COLOR}settarget{KaliStyle.RESET} 192.168.1.100 WebServer")
        print(f"  • Use {KaliStyle.APT_COLOR}settarget{KaliStyle.RESET} (no args) to clear target")
        
        print(f"\n{KaliStyle.WARNING}{KaliStyle.BOLD} Panel Restart:{KaliStyle.RESET}")
        print(f"  • If panel appears corrupted, run: {KaliStyle.APT_COLOR}xfce4-panel{KaliStyle.RESET} {KaliStyle.GREEN}--restart{KaliStyle.RESET}")
        print(f"  • Or logout and login again")
        print(f"  • Panel may disappear temporarily - this is normal")

        print(f"\n\t\t\t{KaliStyle.RED}{KaliStyle.BOLD}H4PPY H4CK1NG!{KaliStyle.RESET}")

    def run(self):
        checks = [
            (self.check_os, "Operating System"),
            (self.check_sudo_privileges, "Sudo Privileges"),
            (self.check_required_files, "Required Files"),
            (self.check_xfce_environment, "XFCE Environment")
        ]
        
        for check_func, description in checks:
            if not check_func():
                print(f"{KaliStyle.ERROR} {description} check failed")
                return False

        os.system('clear')
        self.show_banner()
        
        self.check_previous_installation()

        tasks = [
            (self.install_additional_packages, "Installing additional packages"),
            (self.copy_files, "Copying configuration files"),
            (self.set_permissions, "Setting file permissions"),
            (self.add_settarget_function, "Adding settarget function"),
            (self.remove_existing_genmon, "Removing existing genmon plugins"),
            (lambda: self.add_plugins_to_panel(*self.find_and_remove_cpugraph()), "Adding panel plugins"),
            (self.restart_panel, "Restarting XFCE panel")
        ]

        total_tasks = len(tasks)

        try:
            for i, (task, description) in enumerate(tasks, 1):
                print(f"\n{KaliStyle.GREY}{'─' * 50}{KaliStyle.RESET}")
                print(f"{KaliStyle.INFO} ({i}/{total_tasks}) {description}...")
                
                if not task():
                    print(f"{KaliStyle.ERROR} Failed: {description}")
                    print(f"{KaliStyle.WARNING} Starting rollback...")
                    self.rollback()
                    return False
                
                time.sleep(0.5)

            self.show_final_message()
            
            self.cleanup()
            logging.info("Installation completed successfully")
            return True

        except KeyboardInterrupt:
            print(f"\n{KaliStyle.WARNING} Installation interrupted by user")
            print(f"{KaliStyle.INFO} Starting rollback...")
            self.rollback()
            return False
            
        except Exception as e:
            print(f"{KaliStyle.ERROR} Unexpected error: {str(e)}")
            logging.error(f"Unexpected error in run: {str(e)}")
            print(f"{KaliStyle.INFO} Starting rollback...")
            self.rollback()
            return False

if __name__ == "__main__":
    try:
        installer = XfceInstaller()
        success = installer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{KaliStyle.WARNING} Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{KaliStyle.ERROR} Critical error: {str(e)}")
        sys.exit(1)