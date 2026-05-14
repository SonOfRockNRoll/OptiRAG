import streamlit as st
from rag_engine import get_optirag_response
from collections import defaultdict

# ─── 1. Sayfa Yapılandırması ─────────────────────────────────────────────────
st.set_page_config(
    page_title="OptiRAG Asistanı",
    page_icon="👓",
    layout="wide",
)

# ─── 2. Özel CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #fdfdfd; }
.bg-icon-1 {
    position: fixed; top: 50px; left: -30px;
    font-size: 200px; color: rgba(0,0,0,0.04);
    transform: rotate(-20deg); user-select: none; z-index: 0;
}
.bg-icon-2 {
    position: fixed; bottom: 50px; right: -30px;
    font-size: 180px; color: rgba(0,0,0,0.03);
    transform: rotate(15deg); user-select: none; z-index: 0;
}
.stChatMessage {
    background-color: rgba(255,255,255,0.9) !important;
    border: 1px solid #eeeeee !important;
    border-radius: 12px !important;
    z-index: 1;
}
</style>
<div class="bg-icon-1">👓</div>
<div class="bg-icon-2">👓</div>
""", unsafe_allow_html=True)

# ─── 3. Session State Başlatma ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Merhaba! Ben **OptiRAG**. Optisyenlik mevzuatı, göz hastalıkları ve cam teknolojileri hakkında sormak istediğiniz her şeyi yanıtlayabilirim.",
            "sources": []
        }
    ]
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# ─── 4. Yardımcı Fonksiyonlar ────────────────────────────────────────────────
def render_sources(sources: list):
    """Bulunan dökümanları arayüzde tıklanabilir şık linkler olarak gösterir."""
    if not sources:
        return

    st.markdown("**📚 Kaynaklar:**")
    grouped = defaultdict(list)
    for s in sources:
        grouped[s['domain']].append(s)

    for domain, items in grouped.items():
        with st.expander(f"📍 {domain} ({len(items)} Döküman)"):
            for item in items:
                st.markdown(f"↳ [{item['section']}]({item['url']})")

# ─── 5. Yan Menü (Sidebar) ───────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Arama Geçmişi")
    if not st.session_state.search_history:
        st.info("Henüz arama yapılmadı.")
    else:
        for item in reversed(st.session_state.search_history):
            st.caption(f"• {item['short']}")
        
        st.markdown("---")
        if st.button("🗑️ Geçmişi Temizle", use_container_width=True):
            st.session_state.search_history = []
            st.rerun()

# ─── 6. Ana İçerik ───────────────────────────────────────────────────────────
st.title("👓 OptiRAG: Akıllı Optisyenlik Asistanı")
st.markdown("---")

# Geçmiş mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            render_sources(msg["sources"])

# ─── 7. Kullanıcı Girişi ─────────────────────────────────────────────────────
if prompt := st.chat_input("Teknik veya hukuki sorunuzu yazın..."):
    short = prompt[:55] + "…" if len(prompt) > 55 else prompt
    st.session_state.search_history.append({"query": prompt, "short": short})
    if len(st.session_state.search_history) > 30:
        st.session_state.search_history.pop(0)

    st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Dokümanlar taranıyor…"):
            answer, sources = get_optirag_response(prompt)
        st.markdown(answer)
        render_sources(sources)
        
    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})