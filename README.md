<div align="center">

<img src="https://hermes.digitalinnovation.one/assets/diome/logo-full.png" width="180" alt="DIO Logo"/>

# 🌌 DataFlow Mentor
### Assistente Virtual Especializado em Engenharia de Dados

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.53-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini_3.8_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![DIO](https://img.shields.io/badge/Projeto_Final-DIO-E91E8C?style=flat-square)](https://dio.me)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

*Projeto Final do Desafio de IA Generativa — Digital Innovation One*

</div>

---

## 📖 Sobre o Projeto

O **DataFlow Mentor** é um assistente conversacional inteligente, construído com **Python + Streamlit + Google Gemini 3.8 Flash**, desenvolvido como projeto final do desafio de IA Generativa da [DIO (Digital Innovation One)](https://dio.me).

O projeto resolve um problema real do dia a dia de quem trabalha com Engenharia de Dados: **navegar por documentações extensas, debugar código e tirar dúvidas técnicas rapidamente**, sem precisar alternar entre múltiplas abas e fóruns.

Com o DataFlow Mentor, o desenvolvedor tem acesso a um mentor sênior disponível 24/7 que:

- 💬 **Responde perguntas técnicas** com exemplos de código prontos para uso
- 📂 **Lê documentos personalizados** enviados pelo usuário (RAG simplificado)
- 🧠 **Mantém o contexto da conversa** ao longo de toda a sessão
- 🔄 **Lida com limites de API** automaticamente com retry e countdown

---

## 🏗️ Arquitetura do Projeto

```
┌─────────────────────────────────────────────────────────┐
│                     DATAFLOW MENTOR                      │
│                                                          │
│  ┌──────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │ Usuário  │───▶│  Streamlit   │───▶│  Google Gemini │  │
│  │  (Chat)  │◀───│  Frontend    │◀───│  3.8 Flash API │  │
│  └──────────┘    └──────────────┘    └────────────────┘  │
│                        │                      │           │
│                  ┌─────▼─────┐         ┌─────▼─────┐    │
│                  │  Session   │         │  System   │    │
│                  │  History   │         │ Instruction│    │
│                  └───────────┘         └───────────┘    │
│                        │                                  │
│                  ┌─────▼─────┐                           │
│                  │ .txt Base │  ◀── RAG Simplificado     │
│                  │  Upload   │                           │
│                  └───────────┘                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🧱 Pilares Técnicos do Desafio DIO

### 1. 📄 Documentação do Agente — Persona
O agente foi configurado via **System Instruction** nativa do Gemini, garantindo que o modelo mantenha persona consistente em todas as interações:

```python
PERSONA = (
    "Você é o DataFlow Mentor da DIO, especialista sênior em Engenharia de Dados. "
    "Ajude com Python (Pandas, PySpark, Scrapy), SQL, pipelines ETL/ELT, "
    "modelagem e infraestrutura de dados. Seja técnico, objetivo e didático "
    "com exemplos de código sempre que possível."
)

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=PERSONA,   # ← passada diretamente ao modelo
)
```

> A vantagem de usar `system_instruction` em vez de concatenar no prompt: o modelo trata a persona como contexto fixo e prioritário, reduzindo alucinações.

---

### 2. 📚 Base de Conhecimento — RAG Simplificado
O projeto implementa uma versão simplificada de **RAG (Retrieval-Augmented Generation)**: o usuário pode enviar qualquer arquivo `.txt` (documentação, manual, runbook) que é injetado diretamente no prompt como contexto prioritário:

```python
if uploaded_file:
    contexto = uploaded_file.read().decode("utf-8")

# Prompt com contexto RAG
prompt_final = (
    f"[Contexto do documento carregado]:
{contexto}

"
    f"[Pergunta]:
{prompt}"
)
```

**Casos de uso práticos:**
- Enviar documentação do Apache Airflow e perguntar sobre DAGs
- Enviar um runbook de infraestrutura e pedir ajuda com comandos
- Enviar um schema de banco e pedir queries otimizadas

---

### 3. ✍️ Engenharia de Prompts
Técnicas aplicadas para garantir respostas precisas e profissionais:

| Técnica | Implementação |
|---------|--------------|
| **System Instruction** | Persona fixa passada ao modelo na inicialização |
| **Contextual Injection** | Documento do usuário injetado no prompt como contexto prioritário |
| **Few-shot implícito** | A persona instrui o modelo a sempre fornecer exemplos de código |
| **Conversation History** | Histórico completo da sessão enviado a cada chamada |

```python
# Histórico no formato nativo do Gemini
history = [
    {"role": "user",  "parts": ["mensagem anterior do usuário"]},
    {"role": "model", "parts": ["resposta anterior do assistente"]},
    # ...
]
chat = model.start_chat(history=history)
response = chat.send_message(prompt_final)
```

---

### 4. 🖥️ Aplicação Funcional — Stack Técnica

| Tecnologia | Versão | Função |
|------------|--------|--------|
| **Python** | 3.10+ | Linguagem principal |
| **Streamlit** | 1.53+ | Interface web interativa |
| **Google Gemini 3.8 Flash** | Latest | Motor de linguagem (LLM) |
| **google-generativeai** | Latest | SDK oficial do Gemini |
| **python-dotenv** | Latest | Gerenciamento seguro de variáveis |

---

### 5. 📊 Avaliação e Resiliência

O assistente foi validado com prompts complexos cobrindo os principais tópicos de Data Engineering. Além disso, o sistema conta com **retry automático com countdown** para lidar com limites de quota da API:

```python
def send_with_retry(chat_session, prompt, max_retries=2):
    for attempt in range(max_retries):
        try:
            return chat_session.send_message(prompt)
        except Exception as e:
            if "429" in str(e):  # Rate limit
                # Extrai o tempo de espera da resposta da API
                wait = extrair_tempo(str(e))
                countdown(wait)  # Exibe contador na UI
            else:
                raise
```

---

### 6. 🚀 Pitch — Problema e Solução

**Problema:** Engenheiros de dados perdem tempo navegando por documentações extensas, Stack Overflow e fóruns para resolver problemas cotidianos de pipelines, SQL e infraestrutura.

**Solução:** O DataFlow Mentor atua como um **mentor sênior sempre disponível** — você descreve o problema em linguagem natural e recebe respostas técnicas com exemplos de código prontos para uso, podendo inclusive alimentar o assistente com sua própria documentação interna.

**Diferencial:** Suporte a base de conhecimento customizada (RAG) + histórico de conversa real + resiliência a limites de API.

---

## 🛠️ Como Instalar e Rodar

### Pré-requisitos
- Python **3.10+**
- Conta no [Google AI Studio](https://aistudio.google.com/) com uma API Key gratuita

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/Wenes11/AssistenteVirtual.git
cd AssistenteVirtual
```

**2. Crie e ative um ambiente virtual (recomendado)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure a API Key**

Crie um arquivo `.env` na raiz do projeto:
```env
GEMINI_API_KEY=sua_chave_aqui
```

> Obtenha sua chave gratuita em: [aistudio.google.com](https://aistudio.google.com/)

**5. Execute o app**
```bash
streamlit run app.py
```

O app abre automaticamente em `http://localhost:8501` 🚀

---

## 📁 Estrutura do Projeto

```
AssistenteVirtual/
│
├── app.py                  # Aplicação principal (UI + lógica de chat)
├── requirements.txt        # Dependências do projeto
├── .env                    # Chave de API (não versionado)
├── .gitignore              # Arquivos ignorados pelo Git
│
└── .streamlit/
    └── config.toml         # Tema visual do Streamlit (dark/cosmic)
```

---

## ✨ Funcionalidades

- [x] Chat conversacional com histórico de sessão
- [x] Persona especializada via System Instruction
- [x] Upload de base de conhecimento `.txt` (RAG simplificado)
- [x] Retry automático com countdown ao atingir limite de API
- [x] Tema visual cósmico (dark mode com gradientes nebulares)
- [x] Modelo Gemini 3.8 Flash (mais rápido e atual)
- [ ] Suporte a PDF e CSV como base de conhecimento *(em breve)*
- [ ] Streaming de respostas *(em breve)*
- [ ] Histórico persistente entre sessões *(em breve)*

---

## 👨‍💻 Desenvolvedor

<div align="center">

**João Vitor Vargas Martins**

Graduando em Ciência da Computação — Estácio (2027)
Junior Data Engineer & Embaixador DIO

[![LinkedIn](https://img.shields.io/badge/LinkedIn-joaovvargas-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/joaovvargas)
[![GitHub](https://img.shields.io/badge/GitHub-Wenes11-181717?style=flat-square&logo=github)](https://github.com/Wenes11)

</div>

---

<div align="center">
  <sub>Feito com 💜 para o desafio de IA Generativa da DIO</sub>
</div>
