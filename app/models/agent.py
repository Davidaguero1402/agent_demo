import openai
import anthropic
from dotenv import load_dotenv
import os
import google.generativeai as genai
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
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            " ".join(msg["content"] for msg in self.messages if msg["role"] == "user")
        )
        return response.text
    
    def generate_content(self, prompt):
        return self.model.generate_content(prompt)




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

def factory(config):
    # Diccionario que asocia el nombre del modelo con la clase correspondiente
    agents = {
        "openai": AgentOpenai,
        "gemini": AgentGemini,
        "antropic": AgentAntropic
    }
    
    # Retornar una instancia del agente adecuado basado en la configuración
    AgentClass = agents.get(config.lower())
    
    if AgentClass:
        return AgentClass()
    else:
        raise ValueError(f"El modelo '{config}' no está soportado.")
