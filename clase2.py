import streamlit as st
from groq import Groq


# --- 1. CONFIGURACIÓN DE LA PÁGINA (Desafío 6) ---
st.set_page_config(
    page_title="Cerbero IA", # Título de la pestaña
    page_icon="🤖"
)


# Título principal de la aplicación (Desafío 6)
# --- 2. CONFIGURACIÓN DE GROQ ---
# ⚠️ INGRESA TU API KEY AQUÍ ⚠️
# Obtén tu clave de: https://console.groq.com/keys
# TU CLAVE API YA ESTÁ PEGADA
GROQ_API_KEY = "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"


# Lista de modelos disponibles de Groq
MODELOS_DISPONIBLES = [
    'llama-3.1-8b-instant',
    'llama-3.3-70b-versatile',
    'deepseek-r1-distill-llama-70b'
]


# Inicializa el cliente de Groq. Manejamos errores si la clave no está.
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error("Error: La clave API de Groq es inválida o falta.")
    st.info("Por favor, obtén tu clave de https://console.groq.com/keys y pégala en la línea 22 del archivo app.py.")
    st.stop() # Detiene la ejecución si la clave falla


# --- 3. SELECCIÓN DEL MODELO (Nuevo) ---
# Se agrega un menú desplegable en la barra lateral para seleccionar el modelo
with st.sidebar:
    st.header("Configuración de IA")
    MODELO_SELECCIONADO = st.selectbox(
        "Selecciona el Motor de IA (Groq)",
        MODELOS_DISPONIBLES,
        index=0, # Por defecto selecciona el primer modelo
        key="modelo_seleccionado"
    )
    st.info(f"Modelo actual: **{MODELO_SELECCIONADO}**")


# --- 4. INICIALIZACIÓN DE LA SESIÓN DE CHAT ---


# Define avatares para el chat
AVATARS = {"user": "👤", "assistant": "🤖"}


# Inicializa el historial de chat en st.session_state si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Mensaje inicial del asistente usando el nuevo avatar
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy un asistente impulsado por IA. Puedes cambiar mi motor en el menú de la izquierda."})


# --- 5. VISUALIZACIÓN DEL HISTORIAL DENTRO DE UN RECUADRO ---


# El contenedor permite que el historial de chat aparezca en un recuadro con scroll.
# Se añade una 'key' para asegurar el redibujado.
with st.container(height=500, border=True, key="chat_history_container"): 
    # Muestra el historial de mensajes al recargar la aplicación
    for message in st.session_state.messages:
        # Usamos el diccionario AVATARS para asignar el emoji correcto
        with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
            st.markdown(message["content"])


# --- 6. MANEJO DE LA ENTRADA DEL USUARIO ---


# Captura la entrada del usuario en el campo de chat
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # 1. Muestra el mensaje del usuario en la interfaz
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Usamos el avatar del usuario
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(prompt)


    # 2. Genera la respuesta de la IA (con streaming)
    # Usamos el avatar del asistente
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        
        # Creamos un placeholder para actualizar el texto en vivo
        message_placeholder = st.empty() 
        
        # Prepara los mensajes para la API de Groq
        messages_for_api = [
            {"role": "system", "content": f"Eres un asistente de chat impulsado por el modelo {MODELO_SELECCIONADO}. Siempre responde en español, de manera concisa y en lenguaje natural (prosa)."},
        ] + st.session_state.messages
        
        try:
            # Llamada a la API de Groq, usando el modelo SELECCIONADO
            stream = client.chat.completions.create(
                messages=messages_for_api,
                model=MODELO_SELECCIONADO, # <--- USAMOS LA VARIABLE DEL SELECTBOX
                stream=True
            )
            
            # Recopila el texto completo de la respuesta del asistente
            full_response = ""
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    # Actualizamos el contenido del placeholder con el cursor
                    message_placeholder.markdown(full_response + "▌") 
            
            # Eliminamos el cursor final
            message_placeholder.markdown(full_response)
            
            # 3. Agrega la respuesta completa al historial de la sesión
            st.session_state.messages.append({"role": "assistant", "content": full_response})


        except Exception as e:
            error_message = f"Ocurrió un error al contactar a la IA: {e}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

