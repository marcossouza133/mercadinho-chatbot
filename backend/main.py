"""
Backend do Chatbot Mercadinho com IA
API FastAPI que integra com Google Gemini para respostas inteligentes
"""

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NOME = os.getenv("MODEL_NOME", "gemini-3.6-flash")
ESTOQUE_PATH = Path(__file__).resolve().parent.parent / "dados" / "estoque.json"

# ---------------------------------------------------------------------------
# Dados do estoque
# ---------------------------------------------------------------------------

def carregar_estoque() -> dict:
    """Carrega os dados do estoque a partir do JSON."""
    with open(ESTOQUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def contexto_loja() -> str:
    """Monta o contexto textual da loja para enviar ao modelo de IA."""
    dados = carregar_estoque()
    loja = dados["loja"]
    produtos = dados["produtos"]

    lista_produtos = "\n".join(
        f"  - {p['nome']}: R$ {p['preco']:.2f}" for p in produtos
    )

    return (
        f"Você é o assistente virtual do **{loja['nome']}**.\n"
        f"Endereço: {loja['endereco']}\n"
        f"Horário: {loja['horario']}\n"
        f"Telefone: {loja['telefone']}\n"
        f"Entrega grátis para compras acima de R$ {loja['entrega_gratis_acima']:.2f}. "
        f"Taxa de entrega: R$ {loja['taxa_entrega']:.2f}.\n\n"
        f"Produtos disponíveis:\n{lista_produtos}\n\n"
        "Responda sempre em português brasileiro, de forma simpática e objetiva. "
        "Se o cliente perguntar sobre algo fora do escopo da loja, diga educadamente "
        "que só pode ajudar com assuntos do mercadinho."
    )

# ---------------------------------------------------------------------------
# Configuração do Gemini
# ---------------------------------------------------------------------------

def configurar_gemini():
    """Configura e retorna o modelo Gemini."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "COLOQUE_SUA_CHAVE_AQUI":
        return None
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=MODEL_NOME,
        system_instruction=contexto_loja(),
    )
    return model


modelo_ia = configurar_gemini()

# ---------------------------------------------------------------------------
# App FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Chatbot Mercadinho com IA",
    description="API do chatbot inteligente do Mercadinho Bom Preço",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir frontend como arquivos estáticos
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class MensagemInput(BaseModel):
    mensagem: str


class MensagemOutput(BaseModel):
    resposta: str


class ProdutoOutput(BaseModel):
    id: int
    nome: str
    preco: float


class LojaOutput(BaseModel):
    nome: str
    horario: str
    endereco: str
    telefone: str
    entrega_gratis_acima: float
    taxa_entrega: float

# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def servir_frontend():
    """Serve a página principal do chatbot."""
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/api/produtos", response_model=list[ProdutoOutput])
async def listar_produtos():
    """Retorna a lista de produtos disponíveis."""
    dados = carregar_estoque()
    return dados["produtos"]


@app.get("/api/loja", response_model=LojaOutput)
async def info_loja():
    """Retorna informações sobre a loja."""
    dados = carregar_estoque()
    return dados["loja"]


@app.post("/api/chat", response_model=MensagemOutput)
async def chat(msg: MensagemInput):
    """Recebe uma mensagem do usuário e retorna a resposta da IA."""
    if not msg.mensagem.strip():
        raise HTTPException(status_code=400, detail="Mensagem não pode estar vazia.")

    if modelo_ia is None:
        raise HTTPException(
            status_code=503,
            detail="Chave da API Gemini não configurada. Atualize o arquivo .env.",
        )

    try:
        response = modelo_ia.generate_content(msg.mensagem)
        return MensagemOutput(resposta=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Verifica se a API está funcionando."""
    return {
        "status": "ok",
        "ia_configurada": modelo_ia is not None,
        "modelo": MODEL_NOME,
    }


# ---------------------------------------------------------------------------
# Execução direta
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
