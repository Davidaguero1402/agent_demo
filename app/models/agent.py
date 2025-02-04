import openai 
from openai import OpenAI
import anthropic
from dotenv import load_dotenv
import os
import google.generativeai as genai
from google.generativeai import GenerativeModel
from ..funciones.funcions import what_is_his_weight, calculate, average_dog_weight
# Cargar las variables de entorno
load_dotenv()

# Configurar las API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))

class AgentOpenai:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

        self.known_actions = {
            "calculate": calculate,
            "average_dog_weight": average_dog_weight,
            "what_is_his_weight": what_is_his_weight 
        }

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=self.messages
        )
        return completion.choices[0].message['content']
class AgentGemini:
    def __init__(self, system=""):
        self.model = genai.GenerativeModel('gemini-1.5-flash') 
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

        self.known_actions = {
            "calculate": calculate,
            "average_dog_weight": average_dog_weight,
            "what_is_his_weight": what_is_his_weight
        }

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        # Accedemos al último mensaje enviado por el usuario
        message = self.messages[-1]["content"]
        if "peso" in message.lower() and "david" in message.lower():
            action = "what_is_his_weight"
            name = "David"
            result = self.known_actions[action](name)
            return f"Observation: {result}"

        # Verificamos si el mensaje contiene una acción conocida
        for action, func in self.known_actions.items():
            if action in message:
                # Si se encuentra una acción conocida, ejecutamos la función correspondiente
                result = func(message.replace(f"{action}: ", "").strip())
                return f"Observation: {result}"

        # Si no hay ninguna acción conocida, se utiliza el modelo de Gemini
        response = self.model.generate_content(
            " ".join(msg["content"] for msg in self.messages if msg["role"] == "user")
        )
        return response.text

    async def generate_content(self, prompt: str):
        """
        Método necesario para la compatibilidad con human_query_to_sql y build_answer
        """
        response = self.model.generate_content(prompt)
        return response



class AgentAntropic:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        prompt_text = " ".join(msg["content"] for msg in self.messages if msg["role"] == "user")
        response = client.completions.create(
            model="claude-v1",  # Asegúrate de usar el modelo correcto según la API de Anthropic
            prompt=prompt_text,
            max_tokens_to_sample=100  # Ajusta el número de tokens según tus necesidades
        )
        return response.completion  # Ajusta esto según el formato de respuesta correcto  # Ajusta esto según el formato de respuesta correcto

from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

class AgentDeepSeek:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

        self.known_actions = {
            "calculate": calculate,
            "average_dog_weight": average_dog_weight,
            "what_is_his_weight": what_is_his_weight
        }

        # Configurar el cliente de OpenAI para usar DeepSeek
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        # Verificar si el último mensaje contiene una acción conocida
        if self.messages:  # Asegurarse de que hay mensajes
            last_message = self.messages[-1]["content"]  # Obtener el último mensaje del usuario

            for action, func in self.known_actions.items():
                if action in last_message:
                    # Si se encuentra una acción conocida, ejecutamos la función correspondiente
                    result = func(last_message.replace(f"{action}: ", "").strip())
                    return f"Observation: {result}"

        # Si no hay ninguna acción conocida, se utiliza la API de DeepSeek
        response = self.client.chat.completions.create(
            model="deepseek-chat",  # Usar el modelo de DeepSeek
            messages=self.messages,
            temperature=0.7,
            max_tokens=100,
            stream=False
        )
        return response.choices[0].message.content

    async def generate_content(self, prompt: str):
        """
        Método necesario para la compatibilidad con human_query_to_sql y build_answer
        """
        response = self.client.chat.completions.create(
            model="deepseek-chat",  # Usar el modelo de DeepSeek
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100,
            stream=False
        )
        return response.choices[0].message.content

def factory(config):
    # Diccionario que asocia el nombre del modelo con la clase correspondiente
    agents = {
        "openai": AgentOpenai,
        "gemini": AgentGemini,
        "antropic": AgentAntropic,
        "deepseek": AgentDeepSeek
    }
    
    # Retornar una instancia del agente adecuado basado en la configuración
    AgentClass = agents.get(config.lower())
    
    if AgentClass:
        return AgentClass()
    else:
        raise ValueError(f"El modelo '{config}' no está soportado.")
