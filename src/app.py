"""
🌸 云思园 — Streamlit 原型界面
AI 思念亲人平台 · 纪念页面原型

使用方式：
    pip install streamlit
    streamlit run src/app.py
"""

import streamlit as st
import json
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="🌸 云思园 — AI 思念亲人平台",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义 CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #fef9f0 0%, #f5ebe0 100%);
    }
    .stApp {
        background: linear-gradient(180deg, #fef9f0 0%, #f5ebe0 100%);
    }
    .memorial-header {
        text-align: center;
        padding: 2rem 0;
    }
    .memorial-header h1 {
        font-size: 2.5rem;
        color: #8b5e3c;
        margin-bottom: 0.5rem;
    }
    .memorial-header p {
        color: #a0845c;
        font-size: 1.1rem;
    }
    .persona-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(139, 94, 60, 0.1);
        margin-bottom: 1rem;
        border: 1px solid rgba(139, 94, 60, 0.1);
    }
    .chat-bubble {
        padding: 0.8rem 1.2rem;
        border-radius: 16px;
        margin-bottom: 0.8rem;
        max-width: 80%;
    }
    .chat-user {
        background: #e8d5b7;
        margin-left: auto;
        text-align: right;
    }
    .chat-persona {
        background: white;
        border: 1px solid #e8d5b7;
    }
    .memory-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #d4a574;
    }
    .feature-card {
        text-align: center;
        padding: 1.5rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def load_sample_personas():
    """加载示例人格数据"""
    try:
        with open("data/sample-personas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div class="memorial-header">
        <h1>🌸 云思园</h1>
        <p>用 AI 技术保存和延续亲人的记忆与声音</p>
        <p><em>让思念不再只是回忆，而是可以触碰的温暖</em></p>
    </div>
    """, unsafe_allow_html=True)


def render_home():
    """渲染首页"""
    render_header()

    st.markdown("---")

    # 核心功能展示
    st.markdown("## ✨ 核心功能")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📸</div>
            <h3>记忆上传</h3>
            <p>上传照片、语音、文字、视频<br>保存珍贵记忆</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>AI 人格训练</h3>
            <p>基于记忆素材<br>训练数字人格</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <h3>温暖对话</h3>
            <p>与数字亲人聊天<br>重温温暖记忆</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎙️</div>
            <h3>语音通话</h3>
            <p>聆听熟悉的声音<br>跨越时空的陪伴</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🕯️</div>
            <h3>虚拟纪念</h3>
            <p>在线纪念堂<br>虚拟祭扫追思</p>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌳</div>
            <h3>家族树</h3>
            <p>构建家族族谱<br>传承家族记忆</p>
        </div>
        """, unsafe_allow_html=True)


def render_memorial(persona):
    """渲染纪念页面"""
    name = persona["name"]
    relation = persona["relation"]
    info = persona["basic_info"]
    voice = persona["voice_profile"]
    model = persona["personality_model"]

    render_header()

    # 人物卡片
    st.markdown(f"""
    <div class="persona-card">
        <h2 style="text-align:center; color:#8b5e3c;">🕯️ {name} · {relation}</h2>
        <p style="text-align:center; color:#a0845c;">
            {info['birth_year']} — {info['death_year']} · {info['birthplace']} · {info['occupation']}
        </p>
        <p style="text-align:center;">
            {' · '.join(info['personality_traits'])}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 记忆墙
    st.markdown("### 📸 记忆墙")
    memories = persona.get("memories", [])
    for mem in memories:
        icon = {"photo": "🖼️", "voice": "🎙️", "text": "📝", "video": "🎬"}.get(mem["type"], "📌")
        st.markdown(f"""
        <div class="memory-card">
            <strong>{icon} {mem['description']}</strong>
            {'<br><em>' + mem.get('content', mem.get('transcript', ''))[:100] + '...</em>' if mem.get('content') or mem.get('transcript') else ''}
        </div>
        """, unsafe_allow_html=True)

    # 对话区域
    st.markdown("### 💬 与" + name + "对话")
    st.caption(f"说话风格：{voice['speaking_style']}")

    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示对话历史
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-bubble chat-user">{msg['content']}</div>
            <div style="clear:both;"></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-bubble chat-persona">🌸 <strong>{name}</strong>：{msg['content']}</div>
            <div style="clear:both;"></div>
            """, unsafe_allow_html=True)

    # 输入框
    user_input = st.chat_input(f"对{name}说些什么...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 模拟回复（原型演示）
        responses = model["typical_responses"]
        if "你好" in user_input or "嗨" in user_input:
            reply = responses["greeting"]
        elif "再见" in user_input or "走了" in user_input:
            reply = responses["farewell"]
        elif "难过" in user_input or "伤心" in user_input or "想你" in user_input:
            reply = responses["comfort"]
        elif "加油" in user_input or "努力" in user_input:
            reply = responses["encouragement"]
        else:
            catchphrase = voice["catchphrases"][0] if voice["catchphrases"] else "嗯，妈妈在呢。"
            reply = f"{catchphrase} {model['core_values'][0]}，记得照顾好自己。"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


def main():
    """主函数"""
    # 侧边栏导航
    with st.sidebar:
        st.markdown("## 🌸 云思园")
        page = st.radio("导航", ["首页", "纪念空间"], label_visibility="collapsed")

    data = load_sample_personas()

    if page == "首页":
        render_home()
    elif page == "纪念空间":
        if data and data.get("personas"):
            persona_names = [f"{p['name']}（{p['relation']}）" for p in data["personas"]]
            selected = st.sidebar.selectbox("选择亲人", persona_names)
            idx = persona_names.index(selected)
            render_memorial(data["personas"][idx])
        else:
            st.warning("未找到示例人格数据，请确保 data/sample-personas.json 文件存在。")
            render_home()


if __name__ == "__main__":
    main()
