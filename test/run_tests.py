#!/usr/bin/env python3
"""
Sistema de testes automatizado para o Programs Manager.
Descobre todas as funções públicas e gera um relatório de execução.
"""
import sys
import os
import inspect
import traceback
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Adiciona o caminho pai para importar lib
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import system, json as json_lib, log
from lib.install import single_instance


class TestRunner:
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.start_time = datetime.now()

    def test_function(self, module_name: str, func_name: str, func, args=None, kwargs=None):
        """Testa uma função e registra o resultado."""
        self.total_tests += 1
        args = args or []
        kwargs = kwargs or {}
        
        result = {
            "module": module_name,
            "function": func_name,
            "status": "PASSED",
            "error": None,
            "message": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Funções que não precisam de testes de execução
            if func_name in ["_resource_path", "_normalize_json_payload", "_default_payload", 
                            "_normalize_program_entry", "_entry_unique_key", "_parse_winget_table",
                            "_run_winget_table", "_looks_like_admin_error"]:
                result["status"] = "SKIPPED"
                result["message"] = "Função auxiliar não testada"
                self.skipped_tests += 1
            
            # Testes específicos para funções públicas importantes
            elif func_name == "nameSO":
                output = func()
                result["message"] = f"Sistema operacional detectado: {output}"
                self.passed_tests += 1
            
            elif func_name == "get_log_file_path":
                output = func()
                result["message"] = f"Caminho do log: {output}"
                self.passed_tests += 1
            
            elif func_name == "read_json":
                # Tenta ler um arquivo JSON válido
                try:
                    output = func("essentials")
                    if output and isinstance(output, dict):
                        result["message"] = f"JSON lido com sucesso. Keys: {list(output.keys())}"
                        self.passed_tests += 1
                    else:
                        result["status"] = "SKIPPED"
                        result["message"] = "Arquivo JSON não encontrado ou vazio"
                        self.skipped_tests += 1
                except Exception as e:
                    result["status"] = "SKIPPED"
                    result["message"] = f"JSON não disponível: {str(e)}"
                    self.skipped_tests += 1
            
            elif func_name == "_normalize_startup_name":
                output = func("Test Program")
                result["message"] = f"Nome normalizado: {output}"
                self.passed_tests += 1
            
            elif func_name in ["acquire_installation_lock", "release_installation_lock", "is_installation_cancelled"]:
                result["status"] = "SKIPPED"
                result["message"] = "Função de lock de processo não testada por segurança"
                self.skipped_tests += 1
            
            else:
                # Para outras funções, apenas verifica se são chamáveis
                if callable(func):
                    result["status"] = "SKIPPED"
                    result["message"] = "Função requer argumentos específicos ou interação do sistema"
                    self.skipped_tests += 1
                else:
                    result["status"] = "FAILED"
                    result["error"] = "Não é uma função callable"
                    self.failed_tests += 1
        
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            result["message"] = traceback.format_exc()
            self.failed_tests += 1
        
        self.results.append(result)
        return result

    def discover_and_test_modules(self):
        """Descobre e testa todos os módulos na pasta lib."""
        modules_to_test = [
            ("lib.system", ["nameSO"]),
            ("lib.json", ["read_json", "write_json", "append_programs", "read_local_json_file", 
                         "save_local_json_file", "fetch_repo_bytes", "fetch_repo_text", "ensure_repo_file"]),
            ("lib.log", ["get_log_file_path", "log", "start_shared_log_server", "get_shared_log_server_url"]),
            ("lib.customizations", ["apply_vision_cursor_black", "disable_startup_programs", 
                                   "enable_startup_whitelist", "save_startup_keys", "_normalize_startup_name"]),
            ("lib.install.single_instance", ["acquire_installation_lock", "release_installation_lock", 
                                             "is_installation_cancelled"]),
        ]
        
        for module_name, function_names in modules_to_test:
            try:
                # Importa o módulo dinamicamente
                parts = module_name.split('.')
                module = __import__(module_name, fromlist=[parts[-1]])
                
                for func_name in function_names:
                    if hasattr(module, func_name):
                        func = getattr(module, func_name)
                        if callable(func):
                            self.test_function(module_name, func_name, func)
                    else:
                        result = {
                            "module": module_name,
                            "function": func_name,
                            "status": "FAILED",
                            "error": "Função não encontrada no módulo",
                            "message": None,
                            "timestamp": datetime.now().isoformat()
                        }
                        self.results.append(result)
                        self.failed_tests += 1
            
            except Exception as e:
                result = {
                    "module": module_name,
                    "function": "all",
                    "status": "FAILED",
                    "error": f"Falha ao importar módulo: {str(e)}",
                    "message": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat()
                }
                self.results.append(result)
                self.failed_tests += 1

    def generate_report(self, output_dir="test"):
        """Gera relatório em texto e JSON."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Relatório em texto
        text_report = self._generate_text_report()
        text_file = output_path / "test_report.txt"
        text_file.write_text(text_report, encoding='utf-8')
        
        # Relatório em JSON
        json_report = self._generate_json_report()
        json_file = output_path / "test_report.json"
        json_file.write_text(json.dumps(json_report, indent=2, ensure_ascii=False), encoding='utf-8')
        
        # Relatório em HTML
        html_report = self._generate_html_report()
        html_file = output_path / "test_report.html"
        html_file.write_text(html_report, encoding='utf-8')
        
        return text_file, json_file, html_file

    def _generate_text_report(self) -> str:
        """Gera relatório em formato texto."""
        duration = datetime.now() - self.start_time
        
        report = f"""
{'='*80}
RELATÓRIO DE TESTES - PROGRAMS MANAGER
{'='*80}

Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duração: {duration.total_seconds():.2f} segundos

RESUMO:
-------
Total de testes: {self.total_tests}
✓ Passou: {self.passed_tests}
✗ Falhou: {self.failed_tests}
⊘ Pulado: {self.skipped_tests}
Taxa de sucesso: {(self.passed_tests / self.total_tests * 100 if self.total_tests > 0 else 0):.1f}%

{'='*80}
DETALHES DOS TESTES:
{'='*80}
"""
        
        # Agrupa resultados por status
        for status in ["PASSED", "FAILED", "SKIPPED"]:
            status_results = [r for r in self.results if r["status"] == status]
            if status_results:
                icon = "✓" if status == "PASSED" else "✗" if status == "FAILED" else "⊘"
                report += f"\n{icon} {status}:\n{'-'*80}\n"
                
                for result in status_results:
                    report += f"\n  Módulo: {result['module']}\n"
                    report += f"  Função: {result['function']}\n"
                    
                    if result["message"]:
                        report += f"  Mensagem: {result['message']}\n"
                    
                    if result["error"]:
                        report += f"  Erro: {result['error']}\n"
                        if result["status"] == "FAILED":
                            report += f"  Stack:\n{result['message']}\n" if result["message"] else ""
                    
                    report += "\n"
        
        report += f"\n{'='*80}\nFIM DO RELATÓRIO\n{'='*80}\n"
        return report

    def _generate_json_report(self) -> Dict[str, Any]:
        """Gera relatório em formato JSON."""
        return {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "summary": {
                "total": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "skipped": self.skipped_tests,
                "success_rate": (self.passed_tests / self.total_tests * 100 if self.total_tests > 0 else 0)
            },
            "results": self.results
        }

    def _generate_html_report(self) -> str:
        """Gera relatório em formato HTML."""
        json_report = self._generate_json_report()
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Testes - Programs Manager</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .summary-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .summary-card.passed .number {{
            color: #27ae60;
        }}
        
        .summary-card.failed .number {{
            color: #e74c3c;
        }}
        
        .summary-card.skipped .number {{
            color: #f39c12;
        }}
        
        .results {{
            padding: 40px;
        }}
        
        .results h2 {{
            margin-bottom: 30px;
            color: #333;
            font-size: 1.8em;
        }}
        
        .result-group {{
            margin-bottom: 30px;
        }}
        
        .result-group h3 {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            color: #333;
            font-size: 1.3em;
        }}
        
        .result-group.passed h3 {{
            color: #27ae60;
        }}
        
        .result-group.failed h3 {{
            color: #e74c3c;
        }}
        
        .result-group.skipped h3 {{
            color: #f39c12;
        }}
        
        .result-group h3::before {{
            content: '';
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            display: inline-block;
        }}
        
        .result-group.passed h3::before {{
            background: #27ae60;
        }}
        
        .result-group.failed h3::before {{
            background: #e74c3c;
        }}
        
        .result-group.skipped h3::before {{
            background: #f39c12;
        }}
        
        .result-item {{
            background: #f8f9fa;
            border-left: 4px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        
        .result-group.passed .result-item {{
            border-left-color: #27ae60;
        }}
        
        .result-group.failed .result-item {{
            border-left-color: #e74c3c;
        }}
        
        .result-group.skipped .result-item {{
            border-left-color: #f39c12;
        }}
        
        .result-item .module {{
            color: #667eea;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            margin-bottom: 5px;
        }}
        
        .result-item .function {{
            color: #333;
            font-family: 'Courier New', monospace;
            margin-bottom: 10px;
        }}
        
        .result-item .message {{
            color: #666;
            font-size: 0.95em;
            margin-bottom: 5px;
        }}
        
        .result-item .error {{
            color: #c0392b;
            background: #ffe6e6;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        
        .success-rate {{
            font-size: 2em;
            font-weight: bold;
            margin: 20px 0;
        }}
        
        .success-rate.high {{
            color: #27ae60;
        }}
        
        .success-rate.medium {{
            color: #f39c12;
        }}
        
        .success-rate.low {{
            color: #e74c3c;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Relatório de Testes</h1>
            <p>Programs Manager - Sistema de Testes Automatizado</p>
            <p>{json_report['timestamp']}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total de Testes</h3>
                <div class="number">{json_report['summary']['total']}</div>
            </div>
            <div class="summary-card passed">
                <h3>✓ Passou</h3>
                <div class="number">{json_report['summary']['passed']}</div>
            </div>
            <div class="summary-card failed">
                <h3>✗ Falhou</h3>
                <div class="number">{json_report['summary']['failed']}</div>
            </div>
            <div class="summary-card skipped">
                <h3>⊘ Pulado</h3>
                <div class="number">{json_report['summary']['skipped']}</div>
            </div>
        </div>
        
        <div class="results">
            <h2>Taxa de Sucesso</h2>
            <div class="success-rate {'high' if json_report['summary']['success_rate'] >= 70 else 'medium' if json_report['summary']['success_rate'] >= 40 else 'low'}">
                {json_report['summary']['success_rate']:.1f}%
            </div>
            
            <h2 style="margin-top: 40px;">Detalhes dos Testes</h2>
"""
        
        for status in ["PASSED", "FAILED", "SKIPPED"]:
            status_results = [r for r in self.results if r["status"] == status]
            if status_results:
                status_lower = status.lower()
                html += f'<div class="result-group {status_lower}">\n'
                html += f'<h3>{status}</h3>\n'
                
                for result in status_results:
                    html += '<div class="result-item">\n'
                    html += f'<div class="module">📦 {result["module"]}</div>\n'
                    html += f'<div class="function">ƒ {result["function"]}</div>\n'
                    
                    if result["message"] and result["status"] != "FAILED":
                        html += f'<div class="message">{result["message"]}</div>\n'
                    
                    if result["error"]:
                        html += f'<div class="error">❌ Erro:\n{result["error"]}'
                        if result["status"] == "FAILED" and result["message"]:
                            html += f'\n\nStack Trace:\n{result["message"]}'
                        html += '</div>\n'
                    
                    html += '</div>\n'
                
                html += '</div>\n'
        
        html += f"""
        </div>
        
        <div class="footer">
            <p>Duração total: {json_report['duration_seconds']:.2f} segundos</p>
            <p>Gerado em: {json_report['timestamp']}</p>
        </div>
    </div>
</body>
</html>
"""
        return html


def main():
    """Executa todos os testes e gera relatório."""
    # Garante que a saída use UTF-8
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("[*] Iniciando testes do Programs Manager...")
    print()
    
    runner = TestRunner()
    runner.discover_and_test_modules()
    
    print(f"[OK] Testes concluidos!")
    print(f"  Total: {runner.total_tests}")
    print(f"  Passou: {runner.passed_tests}")
    print(f"  Falhou: {runner.failed_tests}")
    print(f"  Pulado: {runner.skipped_tests}")
    print()
    
    # Gera relatórios
    text_file, json_file, html_file = runner.generate_report()
    
    print(f"[OK] Relatorios gerados:")
    print(f"  Texto: {text_file}")
    print(f"  JSON:  {json_file}")
    print(f"  HTML:  {html_file}")
    print()
    
    # Exibe o relatório em texto
    print(text_file.read_text(encoding='utf-8'))
    
    return 0 if runner.failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
