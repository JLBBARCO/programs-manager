# Programs Manager User Generator

Gera um `user.json` com os programas instalados no sistema no formato esperado pelo Programs Manager.

Cada item gerado segue esta estrutura:

```json
{
  "name": "Git",
  "type": "install",
  "id": "Git.Git",
  "checkbox": true
}
```

## Executar direto pelo terminal

Linux e macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager-user-generator/main/run.sh | bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager-user-generator/main/run.ps1 | iex
```

Os scripts baixam o artefato mais recente da release `latest`, extraem em uma pasta temporaria e executam o programa.

## Builds locais

Windows:

```bat
build.bat
```

Linux:

```bash
chmod +x build.sh
./build.sh
```

macOS:

```bash
chmod +x build-mac.sh
./build-mac.sh
```

Os arquivos compilados ficam em `dist/Programs Manager User Generator/`.

## GitHub Actions

O workflow em `.github/workflows/build-release.yml` roda automaticamente em pushes para a branch `main` e tambem pode ser iniciado manualmente pelo GitHub Actions.

Ele compila o programa em:

- Windows, usando `build.bat`;
- Linux, usando `build.sh`;
- macOS, usando `build-mac.sh`.

Depois de compilar, o workflow empacota os builds e publica/substitui os arquivos na release `latest`:

- `programs-manager-user-generator-windows.zip`
- `programs-manager-user-generator-linux.tar.gz`
- `programs-manager-user-generator-macos.tar.gz`

## Desenvolvimento

Instale as dependencias:

```bash
python -m pip install -r requirements.txt
```

Execute o programa em modo fonte:

```bash
python main.py
```
