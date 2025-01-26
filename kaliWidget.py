#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

from colorama import Fore, Style
import os
import time
import getpass

def verificar_entorno():
    entorno_escritorio = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    if "xfce" not in entorno_escritorio:
        print(Fore.RED + Style.BRIGHT + '\n[x] ' + Style.RESET_ALL + 'Este script está diseñado para funcionar solo en entornos XFCE en Linux.')
        exit()

def banner():
    print('')
    os.system('clear')
    banner = '''
            ██╗  ██╗ █████╗ ██╗     ██╗
            ██║ ██╔╝██╔══██╗██║     ██║
            █████╔╝ ███████║██║     ██║
            ██╔═██╗ ██╔══██║██║     ██║
            ██║  ██╗██║  ██║███████╗██║
            ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝
           '''
    banner1 = '''
    ██╗    ██╗██╗██████╗  ██████╗ ███████╗████████╗
    ██║    ██║██║██╔══██╗██╔════╝ ██╔════╝╚══██╔══╝
    ██║ █╗ ██║██║██║  ██║██║  ███╗█████╗     ██║   
    ██║███╗██║██║██║  ██║██║   ██║██╔══╝     ██║   
    ╚███╔███╔╝██║██████╔╝╚██████╔╝███████╗   ██║   
     ╚══╝╚══╝ ╚═╝╚═════╝  ╚═════╝ ╚══════╝   ╚═╝  (By SkyW4r33x) 
                                                    v.2.1
           '''
    print(banner + Fore.BLUE + banner1 + Fore.RESET)
    os.system('jp2a --color --width=40  kali-banner.png')

def main():
    # Instalación de jp2a
    os.system('clear')
    print(Fore.GREEN + Style.BRIGHT + '''
    ╔════════════════════════════════════╗
    ║        Instalado requisitos        ║
    ╚════════════════════════════════════╝
    ''' + Style.RESET_ALL)
    time.sleep(1)
    os.system('sudo apt-get update')
    os.system('sudo apt-get install jp2a')
    os.system('sudo apt-get install xclip')

    while True:
        banner()
        print(Fore.YELLOW + '''
    ╔═══════════════════════════╗
    ║ Se instalará lo siguiente ║
    ╠═══════════════════════════╣
    ╠==»    Targeted            ║
    ╠==»    IP VPN              ║
    ╠==»    IP Ethernet         ║
    ╚═══════════════════════════╝
      ¿Deseas continuar? [S/N]
        ''' + Fore.RESET)
        resp = input(Fore.GREEN + '» ' + Style.RESET_ALL)

        if resp.lower() == 's':

            nombre_usuario = getpass.getuser()

            # Copiando archivos
            time.sleep(1)
            print(Fore.BLUE + Style.BRIGHT + '\n[+] ' + Style.RESET_ALL + 'Copiando archivos.')
            os.system('cp -r Archivos/bin ~/.config')
            time.sleep(1)

            # Dando permisos de ejecución
            print(Fore.BLUE + Style.BRIGHT + '\n[+] ' + Style.RESET_ALL + 'Dando permisos correspondientes de ejecución.')
            os.system('chmod +x ~/.config/bin/target.sh')
            os.system('chmod +x ~/.config/bin/ethernet.sh')
            os.system('chmod +x ~/.config/bin/vpnip.sh')
            time.sleep(1)

            # Integrando settarget a .zshrc
            print(Fore.BLUE + Style.BRIGHT + '\n[+] ' + Style.RESET_ALL + 'Integrando settarget a .zshrc')
            os.system("""echo '
# settargeted
function settarget(){
    ip_address=$1
    machine_name=$2
    echo "$ip_address $machine_name" > $HOME/.config/bin/target/target.txt
}' >> ~/.zshrc """)

            # Guía para el usuario
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n════════════════════ (GUÍA DE USUARIO) ═══════════════════════' + Style.RESET_ALL)
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n[1] ' + Style.RESET_ALL + 'Elimina el' + Style.BRIGHT + ' motor genérico ' + Style.RESET_ALL + 'que Kali Linux tiene por defecto, guíate\n'
                                                                           '    del siguiente video: https://i.imgur.com/6jRe3jT.mp4\n')
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n[2] ' + Style.RESET_ALL + 'Ahora toca activar' + Style.BRIGHT + ' Targeted ' + Style.RESET_ALL + 'guíate\n'
                                                                           '    del siguiente video: https://i.imgur.com/4Xuzdgi.mp4\n'
                                                       + Style.BRIGHT + Fore.YELLOW + f'    Ruta: /home/{nombre_usuario}/.config/bin/target.sh\n' + Style.RESET_ALL)
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n[3] ' + Style.RESET_ALL + 'El siguiente es' + Style.BRIGHT + ' IP VPN ' + Style.RESET_ALL + 'guíate\n'
                                                                           '    del siguiente video: https://i.imgur.com/BunV9M7.mp4\n'
                                                       + Style.BRIGHT + Fore.YELLOW + f'    Ruta: /home/{nombre_usuario}/.config/bin/vpnip.sh \n' + Style.RESET_ALL)
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n[4] ' + Style.RESET_ALL + 'Por último' + Style.BRIGHT + ' IP Ethernet ' + Style.RESET_ALL + 'guíate\n'
                                                                           '    del siguiente video: https://i.imgur.com/IHKxldr.mp4\n'
                                                       + Style.BRIGHT + Fore.YELLOW + f'    Ruta: /home/{nombre_usuario}/.config/bin/ethernet.sh' + Style.RESET_ALL)
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n══════════════════════ (CORRECCIÓN) ══════════════════════════' + Style.RESET_ALL)
            time.sleep(1)
            print(Fore.CYAN + Style.BRIGHT + '\n[?] ' + Style.RESET_ALL + 'Quizá al ejecutar el script el área de trabajo se haya disminuido a 1\n'
                                                                           '    guíate del video: https://i.imgur.com/nkoUR9q.mp4\n'
                                                                           '    Si no es así, omite esto.')
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n══════════════════════ (IMPORTANTE) ══════════════════════════' + Style.RESET_ALL)
            time.sleep(1)
            print(Fore.GREEN + Style.BRIGHT + '\n[+] ' + Style.RESET_ALL + 'Recuerda que en esta nueva version, al hacer clic en la IP,\n'
                                                                           '    IP ETHERNET o TARGET, se copiará automáticamente en la clipboard.')
            time.sleep(1)
            print(Fore.RED + Style.BRIGHT + '\n[!] ' + Style.RESET_ALL + 'Saliendo del programa . . .')
            time.sleep(1)
            break

        elif pregunta.lower() == 'n':
            print(Fore.RED + Style.BRIGHT + '\n[!] ' + Style.RESET_ALL + 'Saliendo del programa.')
            time.sleep(2)
            exit()

        else:
            print(Fore.RED + Style.BRIGHT + '\n[✗] ' + Style.RESET_ALL + 'Has ingresado un dato no válido\n' + Style.BRIGHT + '    Vuelve a intentarlo' + Style.RESET_ALL)
            time.sleep(2)
            os.system('clear')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + Style.BRIGHT + '\n\n[!] ' + Style.RESET_ALL + 'Script interrumpido, Saliendo del programa . . .')
        exit()


