import streamlit as st
import requests
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Generador de Tabla de Contenidos para Tesis",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📚 Generador de Tabla de Contenidos para Tesis")

# Inputs del usuario
with st.form("input_form"):
    titulo = st.text_input("Título de la Tesis")
    tesis_general = st.text_area("Tesis General", height=150)
    bibliografia = st.text_area("Bibliografía", height=150)
    submit_button = st.form_submit_button(label="Generar Tabla de Contenidos")

if submit_button:
    if not titulo.strip() or not tesis_general.strip() or not bibliografia.strip():
        st.error("Por favor, completa todos los campos antes de generar la tabla de contenidos.")
    else:
        with st.spinner("Generando la tabla de contenidos..."):
            # Preparar el prompt en español
            prompt = (
                f"Genera una tabla de contenidos para una tesis con el siguiente título:\n"
                f"**Título:** {titulo}\n\n"
                f"**Tesis General:** {tesis_general}\n\n"
                f"**Bibliografía:** {bibliografia}\n\n"
                f"La tabla de contenidos debe constar de 12 capítulos. Cada capítulo debe tener un título y una idea principal que se desarrollará. Asegúrate de que cada idea central esté vinculada y contribuya al desarrollo de la tesis general."
            )

            # Configurar la solicitud a la API
            api_url = "https://api.together.xyz/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {st.secrets['api_key']}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente que ayuda a generar tablas de contenidos para tesis académicas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2512,
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "repetition_penalty": 1,
                "stop": ["<|eot_id|>"],
                "stream": True
            }

            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), stream=True)

                if response.status_code != 200:
                    st.error(f"Error en la solicitud a la API: {response.status_code} - {response.text}")
                else:
                    # Preparar el contenedor para la respuesta
                    response_container = st.container()
                    contenido_generado = ""

                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: "):
                                json_data = decoded_line.replace("data: ", "")
                                if json_data == "[DONE]":
                                    break
                                try:
                                    data = json.loads(json_data)
                                    delta = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                    contenido_generado += delta
                                    response_container.markdown(contenido_generado)
                                except json.JSONDecodeError:
                                    continue
                    # Formatear y mostrar la tabla de contenidos
                    if contenido_generado:
                        st.success("Tabla de contenidos generada exitosamente:")
                        st.markdown("### Tabla de Contenidos")
                        st.markdown(contenido_generado)
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
