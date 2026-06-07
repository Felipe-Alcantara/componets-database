#!/usr/bin/env python3
"""
start_app.py — Inicialização do site Felixo UI Index (Felixo System Design).

Com um único comando: instala dependências (backend Python + frontend Node),
sobe a API Flask e o frontend Vite, e abre o navegador.

Uso:
    python start_app.py                # instala (se preciso) + sobe tudo + abre navegador
    python start_app.py restart        # reinicia as instâncias nas portas
    python start_app.py --no-browser   # sobe sem abrir o navegador
    python start_app.py --no-install   # pula a instalação de dependências
"""

import os
import sys
import time
import socket
import argparse
import subprocess
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
DB_PATH = ROOT.parent / "scraper" / "data" / "components.db"

HOST = "127.0.0.1"
API_PORT = 5001
WEB_PORT = 5173
URL = f"http://{HOST}:{WEB_PORT}"


def log(msg: str) -> None:
    print(f"[start_app] {msg}", flush=True)


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, port)) == 0


def kill_port(port: int) -> None:
    log(f"Liberando a porta {port}...")
    try:
        if os.name == "nt":
            out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
            pids = {
                line.split()[-1]
                for line in out.splitlines()
                if f":{port}" in line and "LISTENING" in line
            }
            for pid in pids:
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
        else:
            out = subprocess.run(["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True).stdout
            for pid in out.split():
                subprocess.run(["kill", "-9", pid], capture_output=True)
    except FileNotFoundError:
        log(f"Não consegui liberar a porta {port} automaticamente. Feche o processo manualmente.")


def install_deps() -> bool:
    # Backend Python
    req = BACKEND_DIR / "requirements.txt"
    log("Instalando dependências do backend (Flask)...")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)])
    if r.returncode != 0:
        log("pip falhou; tentando com --break-system-packages...")
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req), "--break-system-packages"]
        )
    if r.returncode != 0:
        log("Falha ao instalar dependências do backend. Resolva e rode de novo.")
        return False

    # Frontend Node
    npm = "npm.cmd" if os.name == "nt" else "npm"
    if not (FRONTEND_DIR / "node_modules").exists():
        log("Instalando dependências do frontend (npm install)...")
        try:
            r = subprocess.run([npm, "install"], cwd=str(FRONTEND_DIR))
        except FileNotFoundError:
            log("npm não encontrado. Instale o Node.js para subir o frontend.")
            return False
        if r.returncode != 0:
            log("Falha no npm install. Resolva e rode de novo.")
            return False
    return True


def open_browser_when_ready() -> None:
    log("Aguardando o frontend responder...")
    for _ in range(120):  # ~60s
        if port_in_use(WEB_PORT):
            log(f"Frontend de pé. Abrindo {URL}")
            webbrowser.open(URL)
            return
        time.sleep(0.5)
    log(f"O frontend demorou para subir. Abra manualmente: {URL}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inicia o site Felixo UI Index.")
    parser.add_argument("command", nargs="?", default="start", choices=["start", "restart"])
    parser.add_argument("--no-browser", action="store_true", help="não abre o navegador")
    parser.add_argument("--no-install", action="store_true", help="pula a instalação")
    args = parser.parse_args()

    if not DB_PATH.exists():
        log(f"Banco não encontrado em {DB_PATH}.")
        log("Rode a coleta antes: na pasta scraper/, 'python main.py --all-sources --commit'.")
        return 1

    # Reinício / portas ocupadas
    for port in (API_PORT, WEB_PORT):
        if port_in_use(port):
            if args.command == "restart":
                kill_port(port)
                time.sleep(1)
            else:
                log(f"A porta {port} já está em uso. Use 'python start_app.py restart'.")
                if not args.no_browser:
                    webbrowser.open(URL)
                return 0

    if not args.no_install:
        if not install_deps():
            return 1

    npm = "npm.cmd" if os.name == "nt" else "npm"
    procs = []
    try:
        log(f"Subindo a API Flask em http://{HOST}:{API_PORT} ...")
        procs.append(subprocess.Popen([sys.executable, "app.py"], cwd=str(BACKEND_DIR)))

        log(f"Subindo o frontend Vite em {URL} ...")
        procs.append(subprocess.Popen([npm, "run", "dev"], cwd=str(FRONTEND_DIR)))

        if not args.no_browser:
            import threading
            threading.Thread(target=open_browser_when_ready, daemon=True).start()

        log("Site rodando. Ctrl+C para parar.")
        # Espera até qualquer processo encerrar
        while all(p.poll() is None for p in procs):
            time.sleep(0.5)
        return 0
    except KeyboardInterrupt:
        log("Encerrando...")
        return 0
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
