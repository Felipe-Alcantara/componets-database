import subprocess
from pathlib import Path

CACHE_DIR = Path(".cache/repos")


def ensure_repo(repo_url: str, name: str) -> Path | None:
    """
    Clona (shallow) ou atualiza um repositório público num cache local.
    Retorna o Path do repo clonado, ou None em caso de falha.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest = CACHE_DIR / name

    if dest.exists():
        print(f"  [git] {name} já em cache, atualizando...")
        try:
            subprocess.run(
                ["git", "-C", str(dest), "pull", "--depth", "1", "--quiet"],
                check=True, capture_output=True, timeout=300,
            )
        except Exception as exc:
            print(f"  [git] aviso: pull falhou ({exc}), usando cache existente")
        return dest

    print(f"  [git] clonando {repo_url} (shallow)...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--quiet", repo_url, str(dest)],
            check=True, capture_output=True, timeout=600,
        )
        return dest
    except subprocess.CalledProcessError as exc:
        print(f"  [git] erro ao clonar {repo_url}: {exc.stderr.decode()[:200]}")
        return None
    except Exception as exc:
        print(f"  [git] erro ao clonar {repo_url}: {exc}")
        return None


def read_text(path: Path) -> str:
    """Lê um arquivo de texto do disco, ignorando erros de encoding."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
