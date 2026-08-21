# 🛒 Chatbot Mercadinho com IA

Chatbot inteligente para o **Mercadinho Bom Preço**, powered by **Google Gemini**.  
O assistente virtual ajuda clientes com informações sobre produtos, preços, horários e entregas.

---

## 📁 Estrutura do Projeto

```
mercadinho-chatbot/
├── README.md                         # Este arquivo
├── requirements.txt                  # Dependências Python
├── .env                              # Variáveis de ambiente (chave Gemini)
├── backend/
│   └── main.py                       # API FastAPI + integração Gemini
├── frontend/
│   ├── index.html                    # Página do chatbot
│   ├── style.css                     # Estilos (dark mode, glassmorphism)
│   └── script.js                     # Lógica do frontend
├── dados/
│   └── estoque.json                  # Produtos e informações da loja
└── tests/
    ├── __init__.py
    ├── test_api_e_dados.py           # Testes da API e validação de dados
    └── test_chatbot_ia.py            # Testes do chatbot com mocks
```

## 🚀 Como Executar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar a chave da API Gemini

Edite o arquivo `.env` e substitua `COLOQUE_SUA_CHAVE_AQUI` pela sua chave:

```env
GEMINI_API_KEY=sua_chave_aqui
MODEL_NOME=gemini-2.0-flash
```

> 🔑 Obtenha sua chave em [Google AI Studio](https://aistudio.google.com/apikey)

### 3. Rodar o servidor

```bash
cd backend
python main.py
```

Acesse: **http://localhost:8000**

### 4. Rodar os testes

```bash
pytest tests/ -v
```

---

## 🔌 Endpoints da API

| Método | Rota             | Descrição                          |
|--------|------------------|------------------------------------|
| GET    | `/`              | Serve o frontend do chatbot        |
| GET    | `/api/produtos`  | Lista todos os produtos            |
| GET    | `/api/loja`      | Informações da loja                |
| POST   | `/api/chat`      | Envia mensagem e recebe resposta   |
| GET    | `/api/health`    | Status da API e configuração da IA |

### Exemplo — POST `/api/chat`

```json
// Request
{ "mensagem": "Qual o preço do arroz?" }

// Response
{ "resposta": "O Arroz 5kg está por R$ 22,90! 🍚" }
```

---

## 🛠️ Tecnologias

- **Backend**: FastAPI + Uvicorn
- **IA**: Google Gemini (gemini-2.0-flash)
- **Frontend**: HTML5, CSS3 (glassmorphism), JavaScript vanilla
- **Testes**: Pytest + mocks

---

## 📝 Licença

Projeto educacional — uso livre.
