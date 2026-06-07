"""
API REST do Felixo UI Index.

Camada web fina: valida entrada, chama o repository e serializa em JSON.
Toda a lógica de dados vive em repository.py.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

import repository as repo

app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "db": repo.db_exists()})


@app.get("/api/filters")
def filters():
    if not repo.db_exists():
        return jsonify({"error": "banco não encontrado. Rode a coleta primeiro."}), 503
    return jsonify(repo.get_filters())


@app.get("/api/components")
def components():
    if not repo.db_exists():
        return jsonify({"error": "banco não encontrado. Rode a coleta primeiro."}), 503

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(60, max(1, int(request.args.get("per_page", 24))))
    except ValueError:
        return jsonify({"error": "page e per_page devem ser inteiros"}), 400

    result = repo.search_components(
        q=request.args.get("q", "").strip(),
        source=request.args.get("source", "").strip(),
        framework=request.args.get("framework", "").strip(),
        category=request.args.get("category", "").strip(),
        tag=request.args.get("tag", "").strip(),
        include_demos=request.args.get("include_demos") == "1",
        page=page,
        per_page=per_page,
    )
    return jsonify(result)


@app.get("/api/components/<external_id>")
def component_detail(external_id):
    if not repo.db_exists():
        return jsonify({"error": "banco não encontrado. Rode a coleta primeiro."}), 503
    comp = repo.get_component(external_id)
    if not comp:
        return jsonify({"error": "componente não encontrado"}), 404
    return jsonify(comp)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
