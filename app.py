import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. CARREGAMENTO E VALIDAÇÃO DA CHAVE (ESTRITAMENTE NECESSÁRIO) ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="DataFlow Mentor | DIO", page_icon="🤖")

# Interface Lateral para conferência
with st.sidebar:
    st.image("https://hermes.digitalinnovation.one/assets/diome/logo-full.png", width=150)
    st.title("⚙️ Diagnóstico")
    if not api_key:
        st.error("❌ Chave API não encontrada no .env")
    else:
        st.success("✅ Chave API carregada")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Base de Conhecimento (TXT)", type=("txt"))
    contexto = ""
    if uploaded_file:
        contexto = uploaded_file.read().decode("utf-8")
        st.info("Documento pronto para uso.")

# --- 2. CONFIGURAÇÃO ROBUSTA DO MODELO (ETAPA 1, 3 E FALLBACK) ---
# Usamos o modelo 'gemini-pro' que é o mais compatível universalmente
try:
    genai.configure(api_key=api_key)
    # Lista os modelos para garantir que a chave funciona e ver o que está disponível
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Escolhe o Pro por ser mais antigo e estável para evitar o erro 404
    target_model = 'models/gemini-pro' if 'models/gemini-pro' in available_models else available_models[0]
    model = genai.GenerativeModel(target_model)
except Exception as e:
    st.error(f"Erro de Conexão: {e}")

# Persona do Assistente (Etapa 3)
PERSONA = "Você é o DataFlow Mentor da DIO. Ajude com Engenharia de Dados (Python/SQL)."

# --- 3. INTERFACE DE CHAT (ETAPA 4) ---
st.title("🤖 DataFlow Mentor")
st.caption("Projeto Final - IA Generativa")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Diga algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Construção manual do prompt para evitar erros de 'system_instruction'
        prompt_final = f"{PERSONA}\n\nContexto: {contexto}\n\nPergunta: {prompt}"
        
        try:
            response = model.generate_content(prompt_final)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Falha na Resposta: {e}")
            st.warning("Verifique se sua chave no Google AI Studio tem permissão para o modelo Gemini Pro.")