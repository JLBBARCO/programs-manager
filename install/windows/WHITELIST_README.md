# White List - Programas de Startup Permitidos

Este arquivo contém uma lista de programas que devem permanecer ativos no startup do Windows após a customização.

## Como funciona

1. O script `customization.bat` desativa TODOS os programas de startup por padrão
2. Depois, lê este arquivo `white_list.txt` e reativa os programas que estão na lista
3. A busca é **case-insensitive** e suporta **correspondência parcial**

## Formato

- Um programa por linha
- Sem espaços no início ou fim
- Sem comentários
- A busca é feita em minúsculas, então você pode escrever em qualquer case

Exemplo:

```
onedrive
teams
discord
nvidia
```

## Como descobrir nomes de programas

### Opção 1: Usar o script helper (Windows)

Execute `listar-startup.bat` no PowerShell como administrador:

```powershell
.\\listar-startup.bat
```

Isso mostrará todos os programas registrados no startup.

### Opção 2: Verificar o Registro manualmente

Abra `regedit` e navegue para:

- `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run` (64-bit)

Os nomes das entradas (não dos valores) são os que você deve adicionar.

### Opção 3: PowerShell

```powershell
# User startup
Get-ItemProperty "HKCU:\\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# System startup 32-bit
Get-ItemProperty "HKLM:\\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# System startup 64-bit
Get-ItemProperty "HKLM:\\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
```

## Programas recomendados

- **Microsoft**: `onedrive`, `teams`, `msedge`
- **NVIDIA**: `nvidia`, `nvbackend`, `nvinitialize`
- **Intel Graphics**: `igfxtray`, `igfxpers`, `igfxhk`
- **AMD**: `amd`, `radeon`
- **Segurança**: `securityhealth`, `defender`
- **Comunicação**: `discord`, `whatsapp`, `teams`, `slack`
- **Utilitários**: `rainmeter`, `lively`

## Regras de Busca

A busca é **case-insensitive** e **parcial**, então:

| Entrada na Whitelist | Programas que serão reativados                      |
| -------------------- | --------------------------------------------------- |
| `onedrive`           | Microsoft.OneDrive, OneDriveStandAlone, ...         |
| `nvidia`             | NVIDIA GeForce Experience, NVBackend, nvcuda, ...   |
| `teams`              | Microsoft Teams, ms-teams, teams, ...               |
| `igfx`               | igfxtray, igfxpers, igfxhk, Intel UHD Graphics, ... |

## Adicionando novos programas

1. Descubra o nome exato usando uma das opções acima
2. Abra `white_list.txt` em um editor de texto (Notepad, VS Code, etc)
3. Adicione uma nova linha com o nome ou parte do nome
4. Salve o arquivo
5. Execute o programa novamente e a customização reativará o novo programa

### Exemplo

Se você quer reativar "Spotify" e seu nome no registro é "Spotify", adicione:

```
spotify
```

Se o nome for "SpotifyHelper", você pode adicionar qualquer uma dessas variações:

```
spotify
spotifyhelper
helper
```

## Notas Importantes

- **Correspondência Parcial**: Se a whitelist tem "teams" e o programa é "Microsoft Teams", ele será ativado
- **Case-Insensitive**: "ONEDRIVE", "OneDrive", "onedrive" funcionam do mesmo jeito
- **Máximo de Flexibilidade**: Use partes curtas e únicas dos nomes para evitar ativações acidentais

## Programas conhecidos do Windows

| Programa         | Nomes típicos no Registro        |
| ---------------- | -------------------------------- |
| OneDrive         | `OneDrive`, `Microsoft.OneDrive` |
| Microsoft Edge   | `msedge`, `Microsoft Edge`       |
| Microsoft Teams  | `Teams`, `ms-teams`              |
| Windows Defender | `SecurityHealth`, `Defender`     |
| Windows Updates  | `waasassistant`                  |
| Cortana          | `Cortana`                        |
| Xbox App         | `Xbox`                           |

## Troubleshooting

### Programa não está sendo reativado

1. Verifique o nome exato usando `listar-startup.bat`
2. Confirme que está escrito corretamente (sem espaços extras)
3. Considere usar uma parte maior do nome para correspondência melhor
4. Execute o programa como administrador

### Programa inesperado foi reativado

A busca é parcial, então um termo pode corresponder a múltiplos programas.

Exemplo: Se você adicionar `edge`, pode reativar `Microsoft Edge` E qualquer programa com "edge" no nome.

Solução: Use nomes mais específicos.

## Editar depois da compilação

Depois que o programa foi compilado com PyInstaller:

**Windows**:

```
dist/Auto Install Programs/install/Windows/white_list.txt
```

**Linux**:

```
dist/Auto Install Programs/install/Windows/white_list.txt
```

**macOS**:

```
dist/Auto Install Programs/open dist/Auto\ Install\ Programs.app/Contents/Resources/install/Windows/white_list.txt
```

Você pode editar o arquivo e executar o programa novamente.
