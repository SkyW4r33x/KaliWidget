#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author: Jordan aka SkyW4r33x
# Description: XFCE dotfiles installer
# Version: 2.2.0

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
        
        log_path = os.path.join(self.script_dir, 'install.log')
        if os.path.exists(log_path) and not os.access(log_path, os.W_OK):
            print(f"{KaliStyle.WARNING} Fixing permissions on {log_path}...")
            subprocess.run(['sudo', 'rm', '-f', log_path], check=True)
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
    ██║██N╗██║██║██║  ██║██║   ██║██╔══╝     ██║   
    ╚███╔███╔╝██║██████╔╝╚██████╔╝███████╗   ██║   
     ╚══╝╚══╝ ╚═╝╚═════╝  ╚═════╝ ╚══════╝   ╚═╝
           """)
        print(f"{KaliStyle.WHITE}\t    [ XFCE Installer - v.2.2.0 ]{KaliStyle.RESET}")
        print(f"{KaliStyle.GREY}\t      [ Created by SkyW4r33x ]{KaliStyle.RESET}\n")

    def run_command(self, command, shell=False, sudo=False, quiet=True):
        try:
            if sudo and not shell:
                command = ['sudo'] + command
            result = subprocess.run(
                command,
                shell=shell,
                check=True,
                stdout=subprocess.PIPE if quiet else None,
                stderr=subprocess.PIPE if quiet else None,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            if not quiet:
                print(f"{KaliStyle.ERROR} Error executing command: {command}")
                print(f"Output: {e.stdout}")
                print(f"Error: {e.stderr}")
            logging.error(f"Error executing command: {command} - {e}\nOutput: {e.stdout}\nError: {e.stderr}")
            return False
        except PermissionError:
            print(f"{KaliStyle.ERROR} Insufficient permissions to execute: {command}")
            return False

    def check_command(self, command):
        try:
            subprocess.run([command, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def check_os(self):
        if not os.path.exists('/etc/debian_version'):
            print(f"{KaliStyle.ERROR} This script is designed for Debian/Kali based systems")
            return False
        return True

    def check_sudo_privileges(self):
        try:
            result = subprocess.run(['sudo', '-n', 'true'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return True
            else:
                print(f"{KaliStyle.WARNING} This script needs to execute commands with sudo.")
                return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Could not verify sudo privileges: {str(e)}")
            return False

    def check_required_files(self):
        required_files = [
            "bin"
        ]
        missing = [f for f in required_files if not os.path.exists(os.path.join(self.script_dir, f))]
        if missing:
            print(f"{KaliStyle.ERROR} Missing required files: {', '.join(missing)}")
            print(f"{KaliStyle.INFO} Make sure they are in {self.script_dir}")
            return False
        return True

    def check_xfce_environment(self):
        entorno_escritorio = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        if "xfce" not in entorno_escritorio:
            print(f"{KaliStyle.ERROR} This script is designed for XFCE environments only.")
            return False
        return True

    def install_additional_packages(self):
        print(f"\n{KaliStyle.INFO} Installing tools")
        self.packages = [
            'jp2a', 'xclip'
        ]
        self.max_length = max(len(pkg) for pkg in self.packages)
        self.state_length = 12
        self.states = {pkg: f"{KaliStyle.GREY}Pending{KaliStyle.RESET}" for pkg in self.packages}
        
        def print_status(first_run=False):
            if not first_run:
                print(f"\033[{len(self.packages) + 1}A", end="")
            
            print(f"{KaliStyle.INFO} Installing packages:")
            for pkg, state in self.states.items():
                print(f"\033[K", end="")
                print(f"  {KaliStyle.YELLOW}•{KaliStyle.RESET} {pkg:<{self.max_length}} {state:<{self.state_length}}")
            sys.stdout.flush()

        try:
            print(f"{KaliStyle.INFO} Updating repositories...")
            if not self.run_command(['apt', 'update'], sudo=True, quiet=True):
                print(f"{KaliStyle.ERROR} Error updating repositories")
                return False
            print(f"{KaliStyle.SUCCESS} Repositories updated")

            print_status(first_run=True)
            failed_packages = []
            for pkg in self.packages:
                check_installed = subprocess.run(['dpkg-query', '-s', pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if check_installed.returncode == 0:
                    self.states[pkg] = f"{KaliStyle.GREEN}Already installed{KaliStyle.RESET}"
                    print_status()
                    continue
                
                self.states[pkg] = f"{KaliStyle.YELLOW}Installing...{KaliStyle.RESET}"
                print_status()
                try:
                    if self.run_command(['apt', 'install', '-y', pkg], sudo=True, quiet=True):
                        self.states[pkg] = f"{KaliStyle.GREEN}Completed{KaliStyle.RESET}"
                        self.actions_taken.append({'type': 'package', 'pkg': pkg})  
                    else:
                        self.states[pkg] = f"{KaliStyle.RED}Failed{KaliStyle.RESET}"
                        failed_packages.append(pkg)
                        print(f"{KaliStyle.WARNING} Warning: Failed to install {pkg}, continuing...")
                except subprocess.CalledProcessError as e:
                    self.states[pkg] = f"{KaliStyle.RED}Failed{KaliStyle.RESET}"
                    failed_packages.append(pkg)
                    logging.error(f"Error installing {pkg}: {e}\nOutput: {e.stdout}\nError: {e.stderr}")
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
            print(f"{KaliStyle.WARNING} Bin directory already exists, skipping copy.")
            return True
        
        try:
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
            print(f"{KaliStyle.WARNING} Shell not supported (only Bash/Zsh). Skipping.")
            return True

        rc_path = os.path.join(self.home_dir, rc_file)
        function_text = f"""
    # XFCE Installer: settarget function - Start
    function settarget() {{
        # Colores ANSI para la salida
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
        local NC='\\033[0m' # Sin color
        
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
    # XFCE Installer: settarget function - End
    """
        try:
            # Verificar si la función ya existe
            if os.path.exists(rc_path):
                with open(rc_path, 'r') as f:
                    content = f.read()
                    if 'function settarget()' in content:
                        print(f"{KaliStyle.WARNING} Function already exists in {rc_file}. Skipping.")
                        return True
            # Verificar permisos de escritura
            if os.path.exists(rc_path) and not os.access(rc_path, os.W_OK):
                print(f"{KaliStyle.ERROR} No write permissions for {rc_file}. Check permissions.")
                logging.error(f"No write permissions for {rc_path}")
                return False
            # Escribir la función
            with open(rc_path, 'a') as f:
                f.write(function_text)
            self.actions_taken.append({'type': 'file_append', 'dest': rc_path})
            print(f"{KaliStyle.SUCCESS} Function added to {rc_file}")
            return True
        except IOError as e:
            print(f"{KaliStyle.ERROR} Error writing to {rc_file}: {e}")
            logging.error(f"Error adding function: {str(e)}")
            return False

    def remove_existing_genmon(self):
        print(f"\n{KaliStyle.INFO} Removing existing genmon plugins...")
        try:
            output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v']).decode('utf-8')
        except subprocess.CalledProcessError:
            print(f"{KaliStyle.WARNING} No plugins found.")
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
            subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{id_}', '-r', '-R'])

        try:
            panels_output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels']).decode('utf-8')
            panels = [int(l.strip()) for l in panels_output.splitlines() if l.strip().isdigit()]
        except subprocess.CalledProcessError:
            panels = [1]

        for p in panels:
            try:
                ids_output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids']).decode('utf-8')
                current_ids = [int(l.strip()) for l in ids_output.splitlines() if l.strip().isdigit()]
                new_ids = [i for i in current_ids if i not in genmon_ids]
                if len(new_ids) < len(current_ids):
                    subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '-r'])
                    if new_ids:
                        args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '--create', '-a']
                        for i in new_ids:
                            args += ['-t', 'int', '-s', str(i)]
                        subprocess.run(args)
            except subprocess.CalledProcessError:
                pass

        print(f"{KaliStyle.SUCCESS} Existing genmon removed")
        return True

    def find_and_remove_cpugraph(self):
        print(f"\n{KaliStyle.INFO} Removing CPU Graph...")
        try:
            output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l', '-v']).decode('utf-8')
        except subprocess.CalledProcessError:
            return None, None

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
            return None, None

        subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{cpugraph_id}', '-r', '-R'])

        try:
            panels_output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', '/panels']).decode('utf-8')
            panels = [int(l.strip()) for l in panels_output.splitlines() if l.strip().isdigit()]
        except subprocess.CalledProcessError:
            panels = [1]

        panel_id = None
        insert_index = None
        for p in panels:
            try:
                ids_output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids']).decode('utf-8')
                current_ids = [int(l.strip()) for l in ids_output.splitlines() if l.strip().isdigit()]
                if cpugraph_id in current_ids:
                    insert_index = current_ids.index(cpugraph_id)
                    panel_id = p
                    new_ids = [i for i in current_ids if i != cpugraph_id]
                    subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '-r'])
                    if new_ids:
                        args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{p}/plugin-ids', '--create', '-a']
                        for i in new_ids:
                            args += ['-t', 'int', '-s', str(i)]
                        subprocess.run(args)
                    break
            except subprocess.CalledProcessError:
                pass

        print(f"{KaliStyle.SUCCESS} CPU Graph removed")
        return panel_id, insert_index

    def add_genmon_to_panel(self, command, period='0.25', title=''):
        try:
            output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l']).decode('utf-8')
            ids = set()
            for line in output.splitlines():
                match = re.match(r'/plugins/plugin-(\d+)(/.*)?$', line)
                if match:
                    ids.add(int(match.group(1)))
            next_id = max(ids) + 1 if ids else 1
        except subprocess.CalledProcessError:
            next_id = 1

        subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}', '-t', 'string', '-s', 'genmon', '--create'])

        rc_dir = os.path.join(self.home_dir, '.config/xfce4/panel')
        os.makedirs(rc_dir, exist_ok=True)
        rc_file = os.path.join(rc_dir, f'genmon-{next_id}.rc')
        with open(rc_file, 'w') as f:
            f.write(f'Command={command}\n')
            f.write(f'UpdatePeriod={int(float(period) * 1000)}\n')
            f.write(f'Text={title}\n')
            f.write('UseLabel=0\n')
            f.write('Font=Cantarell Ultra-Bold 10\n')

        self.actions_taken.append({'type': 'file_copy', 'dest': rc_file})
        return next_id

    def add_separator_to_panel(self):
        try:
            output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', '/plugins', '-l']).decode('utf-8')
            ids = set()
            for line in output.splitlines():
                match = re.match(r'/plugins/plugin-(\d+)(/.*)?$', line)
                if match:
                    ids.add(int(match.group(1)))
            next_id = max(ids) + 1 if ids else 1
        except subprocess.CalledProcessError:
            next_id = 1

        subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}', '-t', 'string', '-s', 'separator', '--create'])
        subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}/style', '-t', 'int', '-s', '0', '--create'])
        subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/plugins/plugin-{next_id}/expand', '-t', 'bool', '-s', 'false', '--create'])

        return next_id

    def insert_panel_plugin_ids(self, new_ids, panel_id=1, insert_index=None):
        try:
            output = subprocess.check_output(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids']).decode('utf-8')
            current_ids = [int(l.strip()) for l in output.splitlines() if l.strip().isdigit()]
        except subprocess.CalledProcessError:
            current_ids = []

        if insert_index is None:
            insert_index = len(current_ids)

        updated_ids = current_ids[:insert_index] + new_ids + current_ids[insert_index:]

        subprocess.run(['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids', '-r'])
        args = ['xfconf-query', '-c', 'xfce4-panel', '-p', f'/panels/panel-{panel_id}/plugin-ids', '--create', '-a']
        for id_ in updated_ids:
            args += ['-t', 'int', '-s', str(id_)]
        subprocess.run(args)

    def add_plugins_to_panel(self, panel_id, insert_index):
        print(f"\n{KaliStyle.INFO} Adding plugins to XFCE panel...")
        new_ids = []
        target_path = os.path.join(self.home_dir, '.config/bin/target.sh')
        vpn_path = os.path.join(self.home_dir, '.config/bin/vpnip.sh')
        ethernet_path = os.path.join(self.home_dir, '.config/bin/ethernet.sh')
        
        new_ids.append(self.add_genmon_to_panel(target_path, '0.25', ''))
        new_ids.append(self.add_separator_to_panel())
        new_ids.append(self.add_genmon_to_panel(vpn_path, '0.25', ''))
        new_ids.append(self.add_separator_to_panel())
        new_ids.append(self.add_genmon_to_panel(ethernet_path, '0.25', ''))
        
        self.insert_panel_plugin_ids(new_ids, panel_id, insert_index)
        print(f"{KaliStyle.SUCCESS} Plugins added")
        return True

    def restart_panel(self):
        print(f"\n{KaliStyle.INFO} Restarting XFCE panel...")
        try:
            subprocess.run(['xfce4-panel', '--restart'])
            print(f"{KaliStyle.SUCCESS} Panel restarted")
            return True
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error restarting panel: {str(e)}")
            logging.error(f"Error restarting panel: {str(e)}")
            return False

    def check_previous_installation(self):
        config_bin_path = os.path.join(self.home_dir, '.config/bin')
        if os.path.exists(config_bin_path):
            print(f"{KaliStyle.WARNING} Already installed. Reinstall? [Y/n]")
            resp = input().lower()
            if resp != 'y' and resp != '':
                print(f"{KaliStyle.ERROR} Exiting.")
                sys.exit(0)
        return True

    def cleanup(self):
        print(f"\n{KaliStyle.INFO} Cleaning up...")
        print(f"{KaliStyle.SUCCESS} Completed")
        print(f"\n\t\t\t\t{KaliStyle.RED}{KaliStyle.BOLD}H4PPY H4CKNG{KaliStyle.RESET}")
        return True

    def rollback(self):
        print(f"{KaliStyle.WARNING} Rolling back changes...")
        for action in reversed(self.actions_taken):
            if action['type'] == 'file_copy' and os.path.exists(action['dest']):
                os.remove(action['dest'])
                print(f"{KaliStyle.SUCCESS} Deleted {action['dest']}")
            elif action['type'] == 'dir_copy' and os.path.exists(action['dest']):
                shutil.rmtree(action['dest'])
                print(f"{KaliStyle.SUCCESS} Deleted {action['dest']}")
            elif action['type'] == 'package':
                print(f"{KaliStyle.WARNING} Removing package {action['pkg']}...")
                self.run_command(['apt', 'remove', '-y', action['pkg']], sudo=True, quiet=True)
            elif action['type'] == 'file_append':
                print(f"{KaliStyle.WARNING} Manual rollback needed for {action['dest']}")
        print(f"{KaliStyle.SUCCESS} Changes rolled back")

    def show_final_message(self):
        time.sleep(2)
        os.system('clear')
        print(f"\n\t\t[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Installation Summary [{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}]\n\n")

        print(f"[{KaliStyle.BLUE}{KaliStyle.BOLD}+{KaliStyle.RESET}] Installed Features\n")
        features = [
            ("Targeted", "Panel plugin for target IP."),
            ("IP VPN", "Panel plugin for VPN IP SkyW4r33x."),
            ("IP Ethernet", "Panel plugin for Ethernet IP."),
            ("settarget", "Shell function to set target.")
        ]
        
        for name, desc in features:
            print(f"   {KaliStyle.YELLOW}▸{KaliStyle.RESET} {KaliStyle.WHITE}{name:<17}{KaliStyle.RESET} {KaliStyle.GREY}→{KaliStyle.RESET} {desc}")
        
        print(f"\n{KaliStyle.TURQUOISE}{'═' * 50}{KaliStyle.RESET}")
        print(f"\n{KaliStyle.WARNING}{KaliStyle.BOLD} Important:{KaliStyle.RESET} Click on IPs copies to clipboard. Use {KaliStyle.APT_COLOR}settarget{KaliStyle.RESET} <IP> <Name>")
        print(f"{KaliStyle.WARNING}{KaliStyle.BOLD} Note:{KaliStyle.RESET} You must restart XFCE to apply changes. Run {KaliStyle.APT_COLOR}xfce4-panel{KaliStyle.RESET}{KaliStyle.GREEN} --restart{KaliStyle.RESET} or log out and log back in.")
        print(f"{KaliStyle.WARNING} If the taskbar disappears temporarily, don't worry—this is normal. Simply restart XFCE to restore it.")

    def run(self):
        if not all([self.check_os(), self.check_sudo_privileges(), self.check_required_files(), self.check_xfce_environment()]):
            return False

        os.system('clear')
        self.show_banner()
        self.check_previous_installation()

        tasks = [
            (self.install_additional_packages, "Additional packages installation"),
            (self.copy_files, "Files copy"),
            (self.set_permissions, "Permissions setup"),
            (self.add_settarget_function, "Settarget function addition"),
            (self.remove_existing_genmon, "Remove existing genmon"),
            (lambda: self.add_plugins_to_panel(*self.find_and_remove_cpugraph()), "Add plugins to panel"),
            (self.restart_panel, "Restart panel")
        ]

        total_tasks = len(tasks)

        try:
            for i, (task, description) in enumerate(tasks, 1):
                print(f"\n{KaliStyle.GREY}{'─' * 40}{KaliStyle.RESET}")
                print(f"{KaliStyle.INFO} ({i}/{total_tasks}) Starting {description}...")
                if not task():
                    print(f"{KaliStyle.ERROR} Error in {description}")
                    self.rollback()
                    self.cleanup()
                    return False
                time.sleep(0.5)
            print()

            self.show_final_message()

            self.cleanup()
            logging.info("Installation completed successfully")
            return True

        except KeyboardInterrupt:
            print(f"\n{KaliStyle.WARNING} Installation interrupted")
            self.rollback()
            self.cleanup()
            return False
        except Exception as e:
            print(f"{KaliStyle.ERROR} Error: {str(e)}")
            logging.error(f"General error in run: {str(e)}")
            self.rollback()
            self.cleanup()
            return False

if __name__ == "__main__":
    installer = XfceInstaller()
    installer.run()