# Sistema de Testes - Programs Manager

Este diretório contém o sistema automatizado de testes para o Programs Manager, que descobre e testa todas as funções principais da aplicação.

## 📋 O que foi testado?

O sistema de testes valida:
- ✓ Módulos da biblioteca (`lib/system`, `lib/json`, `lib/log`, `lib/customizations`, etc.)
- ✓ Funções públicas de cada módulo
- ✓ Tratamento de erros e exceções
- ✓ Compatibilidade com diferentes sistemas operacionais

## 🚀 Como executar

### Opção 1: Executar com Python diretamente

```bash
# Navegar até a raiz do projeto
cd programs-manager

# Executar os testes
python test/run_tests.py
```

### Opção 2: Executar com pytest (recomendado)

```bash
# Instalar pytest
pip install pytest

# Executar os testes
pytest test/run_tests.py -v
```

## 📊 Relatórios gerados

Após a execução, três relatórios são criados na pasta `test/`:

### 1. **test_report.txt**
Relatório em texto puro com:
- Resumo de resultados (total, passou, falhou, pulado)
- Taxa de sucesso percentual
- Detalhes de cada teste
- Erros e mensagens específicas

### 2. **test_report.json**
Dados estruturados em JSON contendo:
- Timestamp de execução
- Duração total em segundos
- Resumo com estatísticas
- Array completo de resultados com status individual

### 3. **test_report.html**
Relatório visual interativo com:
- Dashboard com resumo visual
- Gráficos de status (passou/falhou/pulado)
- Taxa de sucesso em percentual
- Detalhes de cada teste com cores
- Stack traces formatados para erros

## 📈 Estrutura do relatório

```
┌─────────────────────────────────────┐
│   Relatório de Testes               │
│   Programs Manager                  │
└─────────────────────────────────────┘
│
├─ RESUMO
│  ├─ Total de testes: N
│  ├─ Passou: X
│  ├─ Falhou: Y
│  └─ Pulado: Z
│
├─ TESTES QUE PASSARAM (✓)
│  ├─ Função 1
│  ├─ Função 2
│  └─ ...
│
├─ TESTES QUE FALHARAM (✗)
│  ├─ Função A
│  │  └─ Erro: ...
│  └─ ...
│
└─ TESTES PULADOS (⊘)
   ├─ Função α
   └─ ...
```

## 🔍 Interpretando os resultados

### Status dos testes:

- **✓ PASSED**: Função testada com sucesso
- **✗ FAILED**: Função falhou durante teste (verifique o erro)
- **⊘ SKIPPED**: Função pulada por requerer setup específico ou ser auxiliar

### Exemplo de saída:

```
✓ PASSED:
  - lib.system.nameSO: Sistema operacional detectado: Windows

✗ FAILED:
  - lib.json.read_json: Erro ao ler arquivo
    Stack Trace: FileNotFoundError: ...

⊘ SKIPPED:
  - lib.install.acquire_installation_lock: Função requer lock seguro
```

## 📝 Funções testadas por módulo

### lib.system
- `nameSO()` - Detecta sistema operacional

### lib.json
- `read_json()` - Lê configuração JSON
- `write_json()` - Escreve arquivo JSON
- `append_programs()` - Adiciona programas ao JSON
- `read_local_json_file()` - Lê JSON local
- `save_local_json_file()` - Salva JSON local
- `fetch_repo_bytes()` - Busca dados do repositório
- `fetch_repo_text()` - Busca texto do repositório
- `ensure_repo_file()` - Garante arquivo do repositório

### lib.log
- `get_log_file_path()` - Obtém caminho do arquivo de log
- `log()` - Registra mensagem de log
- `start_shared_log_server()` - Inicia servidor de log compartilhado
- `get_shared_log_server_url()` - Obtém URL do servidor de log

### lib.customizations
- `apply_vision_cursor_black()` - Aplica tema de cursor
- `disable_startup_programs()` - Desativa programas na inicialização
- `enable_startup_whitelist()` - Ativa whitelist na inicialização
- `save_startup_keys()` - Salva chaves de inicialização

### lib.install.single_instance
- `acquire_installation_lock()` - Adquire lock de instalação
- `release_installation_lock()` - Libera lock de instalação
- `is_installation_cancelled()` - Verifica se instalação foi cancelada

## 🛠️ Adicionar novos testes

Para adicionar novos testes:

1. Abra `test/run_tests.py`
2. Localize o método `discover_and_test_modules()`
3. Adicione o módulo e funções à lista `modules_to_test`:

```python
modules_to_test = [
    ("seu.novo.modulo", ["funcao1", "funcao2"]),
    # ...
]
```

4. Adicione lógica específica de teste no método `test_function()` se necessário:

```python
elif func_name == "sua_funcao":
    output = func(arg1, arg2)
    result["message"] = f"Resultado: {output}"
    self.passed_tests += 1
```

## 📦 Dependências

Os testes requerem:
- Python 3.7+
- Módulos padrão (inspect, traceback, json, pathlib, datetime)
- Módulos do projeto (`lib.system`, `lib.json`, `lib.log`, etc.)

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'lib'"
- Certifique-se de estar executando na raiz do projeto
- Verifique se o arquivo `__init__.py` existe em `lib/`

### "FileNotFoundError" nos testes de JSON
- Arquivos JSON estão em `install/` e são baixados do repositório em tempo de execução
- O teste será pulado se o arquivo não existir

### Testes falhando no Linux/macOS
- Alguns testes são específicos do Windows (ex: startup programs)
- Esses testes serão pulados automaticamente no SO correto

## 📄 Exemplo de uso em CI/CD

```yaml
- name: Run Tests
  run: |
    cd ${{ github.workspace }}
    python test/run_tests.py
    
- name: Upload Reports
  uses: actions/upload-artifact@v4
  with:
    name: test-reports
    path: test/test_report.*
```

## 📞 Contato

Para problemas com os testes, abra uma issue no repositório.
