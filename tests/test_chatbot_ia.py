"""
Testes do chatbot IA — verifica comportamento do endpoint /api/chat
e lógica de configuração do Gemini.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient


class TestChatbotIAConfig:
    """Testes de configuração do modelo de IA."""

    def test_modelo_none_quando_chave_invalida(self):
        """Se a chave for o placeholder, modelo_ia deve ser None."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "COLOQUE_SUA_CHAVE_AQUI"}):
            # Re-importa para testar com a chave padrão
            import importlib
            import main
            importlib.reload(main)
            assert main.modelo_ia is None

    def test_modelo_none_quando_chave_vazia(self):
        """Se a chave estiver vazia, modelo_ia deve ser None."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            import importlib
            import main
            importlib.reload(main)
            assert main.modelo_ia is None


class TestChatbotEndpoint:
    """Testes do endpoint /api/chat."""

    def test_chat_retorna_503_sem_ia(self):
        """Quando a IA não está configurada, deve retornar 503."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "COLOQUE_SUA_CHAVE_AQUI"}):
            import importlib
            import main
            importlib.reload(main)
            client = TestClient(main.app)

            response = client.post("/api/chat", json={"mensagem": "Oi"})
            assert response.status_code == 503
            assert "Chave da API" in response.json()["detail"]

    def test_chat_sucesso_com_mock(self):
        """Simula resposta do Gemini para testar o fluxo completo."""
        import main

        # Cria mock do modelo
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Olá! Posso ajudar com nossos produtos."
        mock_model.generate_content.return_value = mock_response

        # Substitui o modelo real pelo mock
        original = main.modelo_ia
        main.modelo_ia = mock_model

        try:
            client = TestClient(main.app)
            response = client.post("/api/chat", json={"mensagem": "Quais produtos vocês têm?"})
            assert response.status_code == 200
            data = response.json()
            assert "resposta" in data
            assert data["resposta"] == "Olá! Posso ajudar com nossos produtos."
            mock_model.generate_content.assert_called_once_with("Quais produtos vocês têm?")
        finally:
            main.modelo_ia = original

    def test_chat_erro_no_modelo(self):
        """Simula erro no Gemini para verificar tratamento de exceção."""
        import main

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("Erro de rede")

        original = main.modelo_ia
        main.modelo_ia = mock_model

        try:
            client = TestClient(main.app)
            response = client.post("/api/chat", json={"mensagem": "teste"})
            assert response.status_code == 500
            assert "Erro ao gerar resposta" in response.json()["detail"]
        finally:
            main.modelo_ia = original

    def test_chat_valida_campo_mensagem(self):
        """Payload sem o campo 'mensagem' deve retornar 422."""
        import main
        client = TestClient(main.app)
        response = client.post("/api/chat", json={"texto": "Olá"})
        assert response.status_code == 422
