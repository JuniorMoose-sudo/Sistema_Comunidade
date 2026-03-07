import streamlit as st


def render_header(parish_info: dict):
    """Renderiza o cabeçalho principal da comunidade."""
    st.markdown(
        f"""
<div class="community-header">
    <h1 style="margin:0; font-size: 2.5rem;">⛪ Comunidade Jesus de Názare</h1>
    <p style="margin:0; opacity:0.9; font-size: 1.1rem;">📞 (83) 99999-9999 | 📍 Rua da Comunidade, 123</p>
    <p style="margin:0; opacity:0.9; font-size: 1rem;">🏛️ {parish_info['nome']} | Diocese de Campina Grande</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, subtitle: str | None = None, color: str = "#3B82F6"):
    """Renderiza um card de métrica padronizado."""
    subtitle_html = f"<small>{subtitle}</small>" if subtitle else ""
    st.markdown(
        f"""
<div class="metric-card">
    <h3 style="margin:0; color: #6B7280;">{title}</h3>
    <h1 style="margin:0; color: {color};">{value}</h1>
    {subtitle_html}
</div>
""",
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str):
    """Wrapper simples para métricas menores."""
    st.metric(label, value)

