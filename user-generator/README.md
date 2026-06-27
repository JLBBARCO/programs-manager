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
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run-user-generator.sh | bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run-user-generator.ps1 | iex
```

Os scripts baixam o artefato mais recente da release `latest`, extraem em uma pasta temporaria e executam o programa.

## Builds locais

Windows:

```bat
build-compilers/build-user-generator.bat
```

Linux:

```bash
chmod +x build-compilers/build-user-generator.sh
./build-compilers/build-user-generator.sh
```

macOS:

```bash
chmod +x build-compilers/build-mac-user-generator.sh
./build-compilers/build-mac-user-generator.sh
```

Os arquivos compilados ficam em `dist/Programs Manager User Generator/`.

## GitHub Actions

O workflow em `.github/workflows/build-user-generator.yml` roda automaticamente em pushes para `main` e `develop` quando o user-generator muda, e tambem pode ser iniciado manualmente pelo GitHub Actions.

Ele compila o programa em:

- Windows, usando `build-compilers/build-user-generator.bat`;
- Linux, usando `build-compilers/build-user-generator.sh`;
- macOS, usando `build-compilers/build-mac-user-generator.sh`.

Depois de compilar, o workflow empacota os builds. O workflow `.github/workflows/release.yml` publica/substitui os arquivos na release correta:

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
python user-generator/main.py
```
