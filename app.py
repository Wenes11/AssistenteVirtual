import streamlit as st
import google.generativeai as genai
import os, re, time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="DataFlow Mentor | DIO",
    page_icon="\U0001f30c",
    layout="wide",
)

# ─── CSS ───────────────────────────────────────
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

html,body,[data-testid=stAppViewContainer],[data-testid=stAppViewBlockContainer]{
  background:#03010A!important;
  font-family:'Inter',sans-serif!important;
  color:#E2E0FF!important;
}
[data-testid=stAppViewContainer]::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 110% 70% at 5%  0%,  rgba(124,58,237,.20) 0%,transparent 55%),
    radial-gradient(ellipse 80%  60% at 95% 100%,rgba(6,182,212,.16)  0%,transparent 55%),
    radial-gradient(ellipse 60%  50% at 50% 50%, rgba(236,72,153,.09) 0%,transparent 60%),
    radial-gradient(ellipse 35%  30% at 80% 20%, rgba(245,158,11,.07) 0%,transparent 50%);
}
[data-testid=stMain],[data-testid=stMainBlockContainer]{
  background:transparent!important;position:relative;z-index:1;padding-top:1rem!important;
}

/* sidebar */
[data-testid=stSidebar]{
  background:rgba(8,4,24,.97)!important;
  border-right:1px solid rgba(124,58,237,.25)!important;
}
[data-testid=stSidebarContent]{padding:0 1rem 2rem!important;}
[data-testid=stSidebar] *{color:#C4BFDF!important;}
[data-testid=stSidebar] img{opacity:.9;filter:brightness(1.05);}
[data-testid=stSidebar] hr{border:none!important;border-top:1px solid rgba(124,58,237,.20)!important;margin:.9rem 0!important;}
[data-testid=stFileUploader]{
  border:1.5px dashed rgba(124,58,237,.35)!important;
  border-radius:12px!important;background:rgba(124,58,237,.05)!important;
}
[data-testid=stFileUploader]:hover{
  border-color:rgba(124,58,237,.65)!important;background:rgba(124,58,237,.10)!important;
}

/* chat messages */
[data-testid=stChatMessage]{
  background:rgba(13,7,32,.65)!important;
  border:1px solid rgba(255,255,255,.06)!important;
  border-radius:18px!important;
  padding:1rem 1.3rem!important;
  margin-bottom:.7rem!important;
  backdrop-filter:blur(12px)!important;
  animation:rise .28s cubic-bezier(.16,1,.3,1)!important;
}
[data-testid=stChatMessage]:hover{border-color:rgba(124,58,237,.22)!important;}
[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-user]){
  border-left:3px solid #7C3AED!important;background:rgba(124,58,237,.08)!important;
}
[data-testid=stChatMessage]:has([data-testid=chatAvatarIcon-assistant]){
  border-left:3px solid #06B6D4!important;background:rgba(6,182,212,.05)!important;
}
[data-testid=stChatMessage] p{font-size:.93rem!important;line-height:1.72!important;color:#C8C4E8!important;}
[data-testid=stChatMessage] li{font-size:.91rem!important;line-height:1.7!important;color:#B8B4D8!important;}
[data-testid=stChatMessage] strong{color:#EDE8FF!important;font-weight:600!important;}
[data-testid=stChatMessage] code{
  font-family:'Fira Code',monospace!important;font-size:.81rem!important;
  background:rgba(124,58,237,.16)!important;color:#C4B5FD!important;
  border:1px solid rgba(124,58,237,.22)!important;border-radius:5px!important;padding:.12em .4em!important;
}
[data-testid=stChatMessage] pre{
  background:#060212!important;border:1px solid rgba(124,58,237,.22)!important;
  border-top:2px solid #7C3AED!important;border-radius:12px!important;padding:1rem 1.2rem!important;
}
[data-testid=stChatMessage] pre code{
  background:transparent!important;color:#DDD8F8!important;border:none!important;padding:0!important;
}

/* chat input */
[data-testid=stChatInput]{
  background:rgba(8,4,24,.92)!important;
  border:1.5px solid rgba(124,58,237,.35)!important;
  border-radius:18px!important;
  box-shadow:0 8px 40px rgba(0,0,0,.5)!important;
  transition:all .25s!important;
}
[data-testid=stChatInput]:focus-within{
  border-color:#7C3AED!important;
  box-shadow:0 0 0 3px rgba(124,58,237,.18),0 8px 40px rgba(0,0,0,.5)!important;
}
[data-testid=stChatInput] textarea{color:#E2E0FF!important;background:transparent!important;font-family:'Inter',sans-serif!important;}
[data-testid=stChatInput] textarea::placeholder{color:#3D3560!important;}
[data-testid=stChatInput] button{
  background:linear-gradient(135deg,#7C3AED,#06B6D4)!important;
  border:none!important;border-radius:10px!important;
  box-shadow:0 2px 10px rgba(124,58,237,.4)!important;transition:all .2s!important;
}
[data-testid=stChatInput] button:hover{opacity:.85!important;transform:scale(1.07)!important;}

::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(124,58,237,.35);border-radius:99px;}
::-webkit-scrollbar-thumb:hover{background:rgba(124,58,237,.60);}

@keyframes rise{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
@keyframes glow-dot{0%,100%{box-shadow:0 0 6px #34D399;}50%{box-shadow:0 0 14px #34D399;}}

#MainMenu,footer,[data-testid=stToolbar],[data-testid=stDecoration],[data-testid=stStatusWidget]{display:none!important;}
</style>
''', unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.image('https://hermes.digitalinnovation.one/assets/diome/logo-full.png', width=140)
    st.markdown('---')
    st.markdown('''
    <p style="font-size:.70rem;font-weight:700;color:#7C3AED;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.35rem;">
    Base de Conhecimento</p>''', unsafe_allow_html=True)
    uploaded_file = st.file_uploader('', type='txt', label_visibility='collapsed')
    contexto = ''
    if uploaded_file:
        contexto = uploaded_file.read().decode('utf-8')
        st.success(f'`{uploaded_file.name}` carregado.')
    st.markdown('---')
    st.markdown('''
    <div style="background:rgba(124,58,237,.10);border:1px solid rgba(124,58,237,.22);border-radius:12px;padding:.75rem 1rem;">
      <div style="font-size:.65rem;font-weight:700;color:#7C3AED;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.35rem;">Modelo Ativo</div>
      <div style="font-size:.85rem;font-weight:600;color:#EDE8FF;">Gemini 3.8 Flash</div>
      <div style="font-size:.72rem;color:#6B5F8F;margin-top:.3rem;line-height:1.7;">Python &nbsp;·&nbsp; SQL &nbsp;·&nbsp; ETL<br>PySpark &nbsp;·&nbsp; Airflow &nbsp;·&nbsp; dbt</div>
    </div>
    <div style="font-size:.67rem;color:#2A2240;text-align:center;margin-top:1.5rem;">DataFlow Mentor &nbsp;·&nbsp; DIO &nbsp;·&nbsp; 2026</div>
    ''', unsafe_allow_html=True)

# ─── MODELO ────────────────────────────────────────
PERSONA = (
    'Voce e o DataFlow Mentor da DIO, especialista senior em Engenharia de Dados. '
    'Ajude com Python (Pandas, PySpark, Scrapy), SQL, pipelines ETL/ELT, modelagem '
    'e infraestrutura de dados. Seja tecnico, objetivo e didatico com exemplos de codigo.'
)
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name='gemini-3.8-flash', system_instruction=PERSONA)
except Exception as e:
    st.error(f'Erro: {e}')
    st.stop()

# ─── HEADER ────────────────────────────────────────
st.markdown('''
<div style="margin-bottom:.4rem;">
  <span style="display:inline-flex;align-items:center;gap:6px;
    background:rgba(124,58,237,.12);border:1px solid rgba(124,58,237,.30);
    border-radius:999px;padding:3px 12px;
    font-size:.68rem;font-weight:700;color:#06B6D4;letter-spacing:.07em;text-transform:uppercase;">
    <span style="width:6px;height:6px;border-radius:50%;background:#34D399;
      display:inline-block;animation:glow-dot 2s infinite;"></span>
    Online &nbsp;·&nbsp; Gemini 3.8 Flash
  </span>
</div>
<h2 style="font-size:1.6rem;font-weight:700;letter-spacing:-.03em;line-height:1.15;
  background:linear-gradient(120deg,#C4B5FD 0%,#67E8F9 55%,#F9A8D4 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;">
  DataFlow Mentor
</h2>
<p style="font-size:.78rem;color:#4B4575;margin:.2rem 0 1rem;letter-spacing:.01em;">
  Especialista em Engenharia de Dados &nbsp;·&nbsp; DIO 2026
</p>
<div style="height:1px;background:linear-gradient(90deg,rgba(124,58,237,.40),rgba(6,182,212,.20),transparent);margin-bottom:1.25rem;"></div>
''', unsafe_allow_html=True)

# ─── CHAT ──────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    with st.chat_message('assistant'):
        st.markdown(
            'Olá! Sou o **DataFlow Mentor**. Posso te ajudar com:\n\n'
            '- 🐍 **Python** — Pandas, PySpark, Scrapy\n'
            '- 🗄️ **SQL** — queries, otimização, modelagem\n'
            '- ⚙️ **Pipelines** — ETL/ELT, Airflow, Spark, dbt\n'
            '- ☁️ **Cloud** — DataLake, DW, Kafka\n\n'
            '**Como posso te ajudar?**'
        )

for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

if prompt := st.chat_input('Pergunte sobre Engenharia de Dados...'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)
    with st.chat_message('assistant'):
        history = []
        for m in st.session_state.messages[:-1]:
            r = 'user' if m['role'] == 'user' else 'model'
            history.append({'role': r, 'parts': [m['content']]})
        pfinal = f'[Contexto]:\n{contexto}\n\n[Pergunta]:\n{prompt}' if contexto else prompt

        def send_with_retry(cs, up, max_r=2):
            for attempt in range(max_r):
                try:
                    return cs.send_message(up)
                except Exception as e:
                    err = str(e)
                    if '429' in err:
                        m = re.search(r'seconds[^0-9]*(\d+)', err)
                        wait = int(m.group(1)) + 5 if m else 65
                        if attempt < max_r - 1:
                            ph = st.empty()
                            for rem in range(wait, 0, -1):
                                ph.warning(f'Limite atingido. Tentando em {rem}s...')
                                time.sleep(1)
                            ph.empty()
                        else: raise
                    else: raise

        try:
            chat = model.start_chat(history=history)
            with st.spinner('Processando...'):
                resp = send_with_retry(chat, pfinal)
            txt = resp.text
            st.markdown(txt)
            st.session_state.messages.append({'role': 'assistant', 'content': txt})
        except Exception as e:
            err = str(e)
            if '429' in err:
                st.warning('Limite gratuito atingido. Aguarde ~1 minuto.', icon='\u23f3')
            else:
                st.error(f'Erro: {e}')