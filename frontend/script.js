/**
 * Mercadinho Bom Preço — Chatbot Frontend
 * Lógica de interação com a API e manipulação do DOM
 */

const API = window.location.origin;

// --- DOM refs ---------------------------------------------------------------
const messagesEl = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const btnSend = document.getElementById("btn-send");
const btnProdutos = document.getElementById("btn-produtos");
const btnInfo = document.getElementById("btn-info");
const sidebar = document.getElementById("sidebar");
const sidebarTitle = document.getElementById("sidebar-title");
const sidebarContent = document.getElementById("sidebar-content");
const btnCloseSidebar = document.getElementById("btn-close-sidebar");
const sidebarOverlay = document.getElementById("sidebar-overlay");
const statusBadge = document.getElementById("status-badge");

// --- Helpers ----------------------------------------------------------------

/** Faz scroll suave para o fim das mensagens */
function scrollToBottom() {
    requestAnimationFrame(() => {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    });
}

/** Converte markdown básico em HTML simples */
function simpleMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/\n/g, "<br>");
}

/** Cria o elemento de uma mensagem */
function createMessage(content, type) {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${type}-message`;

    const avatar = document.createElement("div");
    avatar.className = `avatar ${type}-avatar`;
    avatar.textContent = type === "bot" ? "🤖" : "👤";

    const bubble = document.createElement("div");
    bubble.className = `bubble ${type}-bubble`;
    bubble.innerHTML = simpleMarkdown(content);

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    return wrapper;
}

/** Mostra o indicador de "digitando…" */
function showTyping() {
    const wrapper = document.createElement("div");
    wrapper.className = "message bot-message";
    wrapper.id = "typing-indicator";

    const avatar = document.createElement("div");
    avatar.className = "avatar bot-avatar";
    avatar.textContent = "🤖";

    const dots = document.createElement("div");
    dots.className = "bubble bot-bubble typing-dots";
    dots.innerHTML = "<span></span><span></span><span></span>";

    wrapper.appendChild(avatar);
    wrapper.appendChild(dots);
    messagesEl.appendChild(wrapper);
    scrollToBottom();
}

/** Remove o indicador de "digitando…" */
function hideTyping() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

// --- Sidebar ----------------------------------------------------------------

function openSidebar() {
    sidebar.classList.remove("hidden");
    requestAnimationFrame(() => {
        sidebar.classList.add("open");
        sidebarOverlay.classList.remove("hidden");
        sidebarOverlay.classList.add("open");
    });
}

function closeSidebar() {
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("open");
    setTimeout(() => {
        sidebar.classList.add("hidden");
        sidebarOverlay.classList.add("hidden");
    }, 350);
}

btnCloseSidebar.addEventListener("click", closeSidebar);
sidebarOverlay.addEventListener("click", closeSidebar);

// --- Produtos ---------------------------------------------------------------
btnProdutos.addEventListener("click", async () => {
    sidebarTitle.textContent = "📦 Produtos Disponíveis";
    sidebarContent.innerHTML = "<p style='color:var(--clr-text-muted)'>Carregando…</p>";
    openSidebar();

    try {
        const res = await fetch(`${API}/api/produtos`);
        const produtos = await res.json();

        sidebarContent.innerHTML = produtos.map(p => `
            <div class="product-card">
                <span class="p-name">${p.nome}</span>
                <span class="p-price">R$ ${p.preco.toFixed(2)}</span>
            </div>
        `).join("");
    } catch {
        sidebarContent.innerHTML = "<p style='color:var(--clr-danger)'>Erro ao carregar produtos.</p>";
    }
});

// --- Info da loja -----------------------------------------------------------
btnInfo.addEventListener("click", async () => {
    sidebarTitle.textContent = "ℹ️ Informações da Loja";
    sidebarContent.innerHTML = "<p style='color:var(--clr-text-muted)'>Carregando…</p>";
    openSidebar();

    try {
        const res = await fetch(`${API}/api/loja`);
        const loja = await res.json();

        sidebarContent.innerHTML = `
            <div class="info-block">
                <div class="label">Nome</div>
                <div class="value">${loja.nome}</div>
            </div>
            <div class="info-block">
                <div class="label">Endereço</div>
                <div class="value">${loja.endereco}</div>
            </div>
            <div class="info-block">
                <div class="label">Horário</div>
                <div class="value">${loja.horario}</div>
            </div>
            <div class="info-block">
                <div class="label">Telefone</div>
                <div class="value">${loja.telefone}</div>
            </div>
            <div class="info-block">
                <div class="label">Entrega grátis acima de</div>
                <div class="value">R$ ${loja.entrega_gratis_acima.toFixed(2)}</div>
            </div>
            <div class="info-block">
                <div class="label">Taxa de entrega</div>
                <div class="value">R$ ${loja.taxa_entrega.toFixed(2)}</div>
            </div>
        `;
    } catch {
        sidebarContent.innerHTML = "<p style='color:var(--clr-danger)'>Erro ao carregar informações.</p>";
    }
});

// --- Chat -------------------------------------------------------------------
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const texto = userInput.value.trim();
    if (!texto) return;

    // Mensagem do usuário
    messagesEl.appendChild(createMessage(texto, "user"));
    userInput.value = "";
    btnSend.disabled = true;
    scrollToBottom();

    // Indicador de digitação
    showTyping();

    try {
        const res = await fetch(`${API}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensagem: texto }),
        });

        hideTyping();

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || "Erro na API");
        }

        const data = await res.json();
        messagesEl.appendChild(createMessage(data.resposta, "bot"));
    } catch (err) {
        hideTyping();
        messagesEl.appendChild(
            createMessage(`⚠️ ${err.message || "Não foi possível obter resposta."}`, "bot")
        );
    }

    btnSend.disabled = false;
    userInput.focus();
    scrollToBottom();
});

// --- Health check -----------------------------------------------------------
async function checkHealth() {
    try {
        const res = await fetch(`${API}/api/health`);
        const data = await res.json();

        if (data.status === "ok" && data.ia_configurada) {
            statusBadge.textContent = "Online";
            statusBadge.className = "badge badge-ok";
        } else if (data.status === "ok") {
            statusBadge.textContent = "Sem IA";
            statusBadge.className = "badge badge-err";
        }
    } catch {
        statusBadge.textContent = "Offline";
        statusBadge.className = "badge badge-err";
    }
}

// Verifica saúde ao carregar
checkHealth();
// Re-verifica a cada 30 segundos
setInterval(checkHealth, 30000);
