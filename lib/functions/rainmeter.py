import os
import shutil
import webbrowser
from lib import log, system

rainmeter_install_data = [
    {
        "name": "Rainmeter",
        "type": "install",
        "id": "Rainmeter.Rainmeter",
        "checkbox": True
    }
]

# 1. Caminho de ORIGEM (Onde o instalador global do Rainmeter cria o atalho)
# O Windows permite ler desta pasta sem ser administrador
rainmeter_shortcut_start_menu = r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Rainmeter.lnk'

# 2. Caminho de DESTINO (A pasta Startup do usuário atual)
# Aqui você tem permissão total de escrita sem precisar de admin
user_appdata = os.environ['APPDATA']
startup_folder = os.path.join(user_appdata, r'Microsoft\Windows\Start Menu\Programs\Startup')


def _create_rainmeter_shortcut():
    """Busca o atalho global e copia para a inicialização do usuário atual."""
    try:
        # Garante que a pasta Startup do usuário existe
        if not os.path.exists(startup_folder):
            os.makedirs(startup_folder)

        # Define o caminho completo do arquivo final
        destination = os.path.join(startup_folder, 'Rainmeter.lnk')

        # Copia o arquivo (Lê do global -> Escreve no usuário)
        shutil.copy(rainmeter_shortcut_start_menu, destination)
        log.info("Atalho do Rainmeter copiado para a Inicialização do Usuário com sucesso.")
        
    except FileNotFoundError:
        log.error(f"Erro: O atalho original não foi encontrado em: {rainmeter_shortcut_start_menu}. O Rainmeter foi instalado corretamente?")
    except Exception as e:
        log.error(f"Erro inesperado ao copiar atalho: {e}")


def _open_rainmeter_skins_site():
    webbrowser.open('https://visualskins.com', new=2)


def rainmeter():
    from lib import install
    
    # Executa a instalação (pode pedir a janela de Admin do Windows se o winget exigir)
    install.install(rainmeter_install_data, system.name())
    
    # Executa a cópia para a inicialização e abre o site
    _create_rainmeter_shortcut()
    _open_rainmeter_skins_site()