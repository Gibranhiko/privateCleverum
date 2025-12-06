import streamlit as st

def display_system_status_main(private_gpt_instance):
	"""Mostrar el estado del sistema en la sección de Estadísticas (no en el sidebar)."""
	st.subheader("📊 Estado del sistema")

	if not private_gpt_instance:
		st.error("❌ Sistema no inicializado")
		return False

	try:
		status = private_gpt_instance.get_system_status()

		# Estado de Ollama
		ollama_status = "🟢 En línea" if status['ollama_available'] else "🔴 Fuera de línea"
		st.markdown(f"""
		<div class="status-card" style="padding: 0.75rem; border: 1px solid #eee; border-radius: 8px; margin-bottom: 1rem;">
			<strong>Estado de Ollama:</strong> {ollama_status}
		</div>
		""", unsafe_allow_html=True)

		# Métricas en columnas
		col1, col2 = st.columns(2)
		with col1:
			st.metric("Documentos", status['total_documents'])
		with col2:
			st.metric("Fragmentos", status['total_chunks'])

		# Info adicional
		st.caption(f"Modelo de embeddings: {status['embedding_model']}")

		# Indicadores
		if status['total_documents'] == 0:
			st.warning("📝 No hay documentos cargados")
		else:
			efficiency = status['total_chunks'] / max(status['total_documents'], 1)
			st.success(f"⚡ Promedio {efficiency:.1f} fragmentos/doc")

		# Botón de refresco
		if st.button("🔄 Actualizar estado"):
			st.rerun()

		return True
	except Exception as e:
		st.error(f"Error obteniendo estado: {str(e)}")
		return False
