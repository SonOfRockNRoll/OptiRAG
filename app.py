import streamlit as st
from rag_engine import get_optirag_response

# 1. Sayfa Yapılandırması
st.set_page_config(page_title="OptiRAG Asistanı", page_icon="👓", layout="centered")

# 2. Özel CSS: Silik Gözlük İkonları ve Sade Tasarım
# İkonların görünmesi için 'position: fixed' ve yüksek 'z-index' kullanıldı.
st.markdown("""
    <style>
    /* Genel Arka Plan */
    .stApp {
        background-color: #fdfdfd;
    }
    
    /* Sol Üst Silik Gözlük */
    .bg-icon-1 {
        position: fixed;
        top: 50px;
        left: -30px;
        font-size: 200px;
        color: rgba(0, 0, 0, 0.04);
        transform: rotate(-20deg);
        user-select: none;
        z-index: 0;
    }
    
    /* Sağ Alt Silik Gözlük */
    .bg-icon-2 {
        position: fixed;
        bottom: 50px;
        right: -30px;
        font-size: 180px;
        color: rgba(0, 0, 0, 0.03);
        transform: rotate(15deg);
        user-select: none;
        z-index: 0;
    }

    /* Mesaj Balonları Stili */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #eeeeee !important;
        border-radius: 12px !important;
        z-index: 1; /* Mesajların ikonların üstünde kalmasını sağlar */
    }
    </style>
    
    <div class="bg-icon-1">👓</div>
    <div class="bg-icon-2">👓</div>
    """, unsafe_allow_html=True)

# 3. Başlık Alanı (Sadeleştirildi)
st.title("👓 OptiRAG: Akıllı Optisyenlik Asistanı")
st.markdown("---")

# 4. Sohbet Geçmişi Yönetimi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları Ekrana Yazdır
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. Kullanıcı Etkileşimi
if prompt := st.chat_input("Teknik veya hukuki sorunuzu yazın..."):
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan (Agent) Yanıtı
    with st.chat_message("assistant"):
        with st.spinner("Dokümanlar taranıyor..."):
            response, sources = get_optirag_response(prompt)
            st.markdown(response)
            
            # Kaynak Gösterimi
            if sources:
                with st.expander("📚 Kaynaklar"):
                    for s in sources:
                        st.write(f"- **{s['section']}**: {s['source']}")
    
    # Asistan yanıtını geçmişe ekle
    st.session_state.messages.append({"role": "assistant", "content": response})