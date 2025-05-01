import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Función para codificar imagen en base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "⚠️ Error: La imagen no se encontró en la ruta especificada."

# Configuración de la página
st.set_page_config(page_title='🛡️ Tablero del Caballero Ilustrado', layout="centered")

# Título y descripción medieval
st.markdown("""
    <h1 style='text-align: center; color: #4B3621;'>🛡️ Tablero del Caballero Ilustrado</h1>
    <p style='text-align: center; font-size: 18px;'>Dibuja tus símbolos, runas o esquemas de batalla, y el Oráculo de la Torre los interpretará con sabiduría ancestral.</p>
    """, unsafe_allow_html=True)

# Panel lateral temático
with st.sidebar:
    st.markdown("## 📜 Acerca del Oráculo")
    st.markdown("Este artefacto mágico interpreta tus símbolos y bocetos. Dibuja sobre el pergamino encantado y descubre su sabiduría.")

# Estética del canvas
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('✒️ Grosor de la tinta', 1, 30, 5)
stroke_color = "#2F1B0C"  # Marrón oscuro, como tinta antigua
bg_color = '#F5F5DC'  # Color pergamino

# Componente canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 215, 0, 0.3)",  # dorado suave translúcido
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Clave API
ke = st.text_input('🔐 Ingresa tu Clave de Acceso al Grimorio (API Key)', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ.get('OPENAI_API_KEY')

# Cliente OpenAI
client = OpenAI(api_key=api_key) if api_key else None

# Botón de análisis
analyze_button = st.button("🔍 Invocar Sabiduría del Oráculo", type="primary")

# Procesamiento si se cumple todo
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("🧙‍♂️ El Oráculo está interpretando tu símbolo..."):

        # Procesar imagen
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe en español lo que observas en la imagen. Sé claro, como un sabio consejero de la corte."

        # Construir mensaje
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
            ],
        }]

        # Petición al modelo
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
            )

            content = response.choices[0].message.content
            if content:
                message_placeholder.markdown(f"### 📖 Respuesta del Oráculo:\n\n{content}")
        except Exception as e:
            st.error(f"⚠️ Ha ocurrido un error al invocar al Oráculo: {e}")
else:
    if not api_key:
        st.warning("🛑 Por favor, ingresa tu clave mágica (API key) para continuar.")
    elif analyze_button and canvas_result.image_data is None:
        st.warning("🛑 Por favor, dibuja tu símbolo en el pergamino antes de invocar al Oráculo.")

