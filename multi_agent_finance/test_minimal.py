"""
Teste mínimo para debug no Streamlit Cloud
"""
import streamlit as st
import sys
from pathlib import Path

st.title("🔍 Debug Test - Minimal App")

st.write("✅ Streamlit importado com sucesso!")
st.write(f"Python version: {sys.version}")
st.write(f"Current directory: {Path.cwd()}")
st.write(f"App file location: {Path(__file__).parent}")

# Tenta importar os módulos um a um
st.subheader("Testing imports:")

try:
    app_dir = Path(__file__).parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    st.write(f"✅ sys.path configurado: {app_dir}")
except Exception as e:
    st.error(f"❌ Erro ao configurar sys.path: {e}")

try:
    from agents.technical_agent import TechnicalAgent
    st.write("✅ TechnicalAgent importado")
except Exception as e:
    st.error(f"❌ Erro ao importar TechnicalAgent: {e}")

try:
    from utils.data_fetcher import DataFetcher
    st.write("✅ DataFetcher importado")
except Exception as e:
    st.error(f"❌ Erro ao importar DataFetcher: {e}")

try:
    from orchestrator.orchestrator import AgentOrchestrator
    st.write("✅ AgentOrchestrator importado")
except Exception as e:
    st.error(f"❌ Erro ao importar AgentOrchestrator: {e}")

st.success("Teste completo!")
