"""
Testes da API e dos dados do estoque.
"""

import json
import sys
from pathlib import Path

import pytest

# Adiciona o diretório raiz do projeto ao path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient
from main import app, carregar_estoque, contexto_loja, ESTOQUE_PATH


client = TestClient(app)


# ---------- Testes de dados (estoque.json) ----------

class TestDadosEstoque:
    """Testes para validar a estrutura dos dados do estoque."""

    def test_arquivo_estoque_existe(self):
        assert ESTOQUE_PATH.exists(), "Arquivo estoque.json não encontrado"

    def test_estoque_json_valido(self):
        dados = carregar_estoque()
        assert isinstance(dados, dict)

    def test_produtos_existem(self):
        dados = carregar_estoque()
        assert "produtos" in dados
        assert isinstance(dados["produtos"], list)
        assert len(dados["produtos"]) > 0

    def test_cada_produto_tem_campos_obrigatorios(self):
        dados = carregar_estoque()
        for produto in dados["produtos"]:
            assert "id" in produto, f"Produto sem id: {produto}"
            assert "nome" in produto, f"Produto sem nome: {produto}"
            assert "preco" in produto, f"Produto sem preco: {produto}"

    def test_precos_positivos(self):
        dados = carregar_estoque()
        for produto in dados["produtos"]:
            assert produto["preco"] > 0, f"Preço inválido: {produto}"

    def test_ids_unicos(self):
        dados = carregar_estoque()
        ids = [p["id"] for p in dados["produtos"]]
        assert len(ids) == len(set(ids)), "IDs duplicados encontrados"

    def test_loja_existe(self):
        dados = carregar_estoque()
        assert "loja" in dados
        loja = dados["loja"]
        campos = ["nome", "horario", "endereco", "telefone", "entrega_gratis_acima", "taxa_entrega"]
        for campo in campos:
            assert campo in loja, f"Campo '{campo}' ausente na loja"

    def test_contexto_loja_retorna_string(self):
        ctx = contexto_loja()
        assert isinstance(ctx, str)
        assert "Mercadinho Bom Preço" in ctx


# ---------- Testes da API (endpoints) ----------

class TestAPI:
    """Testes para os endpoints da API."""

    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "ia_configurada" in data
        assert "modelo" in data

    def test_listar_produtos(self):
        response = client.get("/api/produtos")
        assert response.status_code == 200
        produtos = response.json()
        assert isinstance(produtos, list)
        assert len(produtos) > 0
        assert "nome" in produtos[0]
        assert "preco" in produtos[0]

    def test_info_loja(self):
        response = client.get("/api/loja")
        assert response.status_code == 200
        loja = response.json()
        assert "nome" in loja
        assert "endereco" in loja
        assert "horario" in loja

    def test_chat_mensagem_vazia(self):
        response = client.post("/api/chat", json={"mensagem": ""})
        assert response.status_code == 400

    def test_chat_mensagem_espacos(self):
        response = client.post("/api/chat", json={"mensagem": "   "})
        assert response.status_code == 400

    def test_chat_sem_corpo(self):
        response = client.post("/api/chat")
        assert response.status_code == 422

    def test_frontend_serve(self):
        response = client.get("/")
        assert response.status_code == 200
