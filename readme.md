# Sistema de Atendimento Inteligente para E‑commerce

Um sistema completo de atendimento ao cliente que automatiza respostas a dúvidas frequentes (FAQ), recomenda produtos e envia e‑mails com informações de pedidos. Integra o **Langflow** (fluxos visuais exportados em JSON) com uma **API Flask**, tudo orquestrado via **Docker Compose**.

---

## 🛠️ Funcionalidades

- **FAQ automático**: responde perguntas frequentes carregando o fluxo `faq_responder.json`.
- **Recomendações de produtos**: (em desenvolvimento) fluxo de recomendação simulado em `recommendation_flow.json`.
- **Informações de pedido**: (em desenvolvimento) fluxo de consulta de pedidos em `order_info_flow.json`.
- **Web UI**: formulários HTML para interação via navegador.
- **API JSON**: endpoint `/api/chat` para integração via aplicações externas.
- **Envio de e‑mail**: rota dedicada para disparo de e‑mails ao cliente (configurável).

---

## 📁 Estrutura do Projeto

```bash
E-COMMERCE_ASSISTANT/
├── Dockerfile               # Imagem Docker da API Flask
├── docker-compose.yml       # Orquestra Flask + Langflow
├── requirements.txt         # Dependências Python
├── .env                     # Variáveis de ambiente (não versionar)
│
├── langflow_data/           # Fluxos exportados do Langflow
│   └── faq_responder.json   # Exemplo de fluxo FAQ
│   └── recommendation_flow.json  # Fluxo de recomendação
│   └── order_info_flow.json     # Fluxo de pedidos
│
├── app.py                   # Código principal da aplicação Flask
├── templates/               # HTML Jinja2
│   ├── index.html           # Formulário de entrada
│   └── result.html          # Exibição de respostas
└── static/
    └── style.css            # Arquivos estáticos (CSS, imagens)
```

---

## ⚙️ Pré‑requisitos

- Docker (>= 20.10) e Docker Compose (>= 1.29)
- (Opcional, para dev local) Python 3.10+, pip

---

## 🚀 Como Executar

1. **Clone o repositório**

   ```bash
   git clone https://github.com/SEU_USUARIO/ecommerce-assistant.git
   cd ecommerce-assistant
   ```

2. **Configure as variáveis de ambiente** Crie um arquivo `.env` na raiz com:

   ```dotenv
   # Chave de API gerada no Langflow (Settings → API Keys)
   LANGFLOW_API_KEY=<SUA_CHAVE>

   # Host do Langflow no Docker Compose
   LANGFLOW_HOST=http://langflow:7860

   # Caminho para o JSON do fluxo FAQ (opcional)
   FAQ_FLOW_PATH=langflow_data/faq_responder.json

   # Configurações de e-mail (exemplo SMTP)
   SMTP_HOST=smtp.exemplo.com
   SMTP_PORT=587
   SMTP_USER=usuario@dominio.com
   SMTP_PASS=sua_senha
   EMAIL_FROM=contato@ecommerce.com
   ```

3. **Suba os serviços com Docker Compose**

   ```bash
   docker-compose up -d --build
   ```

   - **Flask App**: [http://localhost:5000](http://localhost:5000)
   - **Langflow UI**: [http://localhost:7860](http://localhost:7860)

4. **Acesse a aplicação**

   - Navegue até `/` para usar o formulário.
   - Envie perguntas e aguarde as respostas processadas pelo Langflow.

---

## 📝 Endpoints

- **GET /** → Formulário HTML (index.html)
- **POST /responder** → Processa formulário e renderiza `result.html` com a resposta.
- **POST /api/chat** → API JSON
  ```json
  Request:
  {
    "message": "Sua pergunta",
    "type": "faq"  // ou: recommendation, order
  }

  Response Promissor:
  {
    "success": true,
    "response": "Texto de resposta gerado"
  }
  ```

---

## 🔄 Adicionando Novos Fluxos

1. No Langflow, crie seu fluxo (FAQ, recomendação, pedido etc.).
2. No menu **Share → Export**, baixe o JSON do fluxo.
3. Salve em `langflow_data/<nome_do_fluxo>.json`.
4. Exporte a variável no `.env` (se quiser path custom):
   ```dotenv
   MY_FLOW_PATH=langflow_data/novo_fluxo.json
   ```
5. No `app.py`, carregue e extraia o ID:
   ```python
   flow_data = langflow_client.load_flow_from_json(os.getenv("MY_FLOW_PATH"))
   flow_id = flow_data["id"]
   ```
6. Crie rota ou inclua no switch de `tipo` para chamá-lo via `run_flow_with_tweaks(flow_id, input_value)`.

---

## 🛡️ Produção

- Remova `debug=True` em `app.run()`.
- Use Gunicorn:
  ```dockerfile
  RUN pip install gunicorn
  CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "4"]
  ```
- Configure HTTPS no proxy (Nginx, Traefik).

