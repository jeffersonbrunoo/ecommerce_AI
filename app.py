import os
import json
import requests
from typing import Dict, Any
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Carrega variáveis de ambiente (para desenvolvimento local e Docker Compose)
load_dotenv()

# Configurações via ambiente
LANGFLOW_HOST = os.getenv("LANGFLOW_HOST", "http://localhost:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY")
FAQ_FLOW_PATH = os.getenv("FAQ_FLOW_PATH", "langflow_data/faq_responder.json")

# Valida chave de API
if not LANGFLOW_API_KEY:
    raise RuntimeError("⚠️ Defina LANGFLOW_API_KEY no .env ou no env_file do Docker Compose")

# Instancia o Flask
app = Flask(__name__)

class LangflowClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def load_flow_from_json(self, json_file_path: str) -> Dict[str, Any]:
        """Carrega o fluxo do arquivo JSON exportado pelo Langflow"""
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def run_flow_with_tweaks(self, flow_id: str, input_value: str, tweaks: Dict[str, Any] = None) -> Dict[str, Any]:
        """Executa um fluxo existente no Langflow via API pelo seu ID"""
        api_url = f"{self.base_url}/api/v1/run/{flow_id}"
        payload = {
            "input_type": "chat",
            "output_type": "chat",
            "input_value": input_value
        }
        if tweaks:
            payload["tweaks"] = tweaks
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

# Instancia o cliente Langflow
langflow_client = LangflowClient(base_url=LANGFLOW_HOST, api_key=LANGFLOW_API_KEY)

# Carrega o fluxo FAQ e extrai seu ID
faq_flow_data = None
faq_flow_id = None
try:
    if os.path.exists(FAQ_FLOW_PATH):
        faq_flow_data = langflow_client.load_flow_from_json(FAQ_FLOW_PATH)
        faq_flow_id = faq_flow_data.get("id")
        if not faq_flow_id:
            raise RuntimeError("ID do fluxo FAQ não encontrado em faq_responder.json")
        print(f"✅ Fluxo FAQ carregado (ID={faq_flow_id})")  # fluxo id confirmado: 0958b98b-890c-4424-a55e-a82dd3fefc9a fileciteturn11file2
    else:
        print(f"⚠️ Arquivo {FAQ_FLOW_PATH} não encontrado!")
except Exception as e:
    print(f"❌ Erro ao carregar fluxo FAQ: {e}")

# Rotas HTTP
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/responder', methods=['POST'])
def responder():
    pergunta = request.form.get('pergunta', '').strip()
    if not pergunta:
        return render_template('result.html', resposta="Por favor, insira uma pergunta.")
    try:
        raw = langflow_client.run_flow_with_tweaks(faq_flow_id, pergunta)
        outputs = raw.get("outputs", [])
        text = ""
        if outputs:
            first = outputs[0]
            inner = first.get("outputs", [])
            if inner:
                text = inner[0].get("results", {}).get("message", {}).get("text", "")
        resposta = text or "Sem resposta do fluxo"
    except Exception as e:
        resposta = f"‼️ Erro ao executar o fluxo: {e}"
    return render_template('result.html', resposta=resposta)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    pergunta = data.get('message', '').strip()
    if not pergunta:
        return jsonify(success=False, error="Mensagem não fornecida"), 400
    if faq_flow_id:
        try:
            raw = langflow_client.run_flow_with_tweaks(faq_flow_id, pergunta)
            outputs = raw.get("outputs", [])
            text = ""
            if outputs:
                first = outputs[0]
                inner = first.get("outputs", [])
                if inner:
                    text = inner[0].get("results", {}).get("message", {}).get("text", "")
            return jsonify(success=True, response=text)
        except Exception as e:
            return jsonify(success=False, error=str(e)), 500
    return jsonify(success=False, error="Fluxo FAQ não disponível"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
