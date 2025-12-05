# Frontend - Interface Web do Sistema MAS

Interface web moderna para testar e demonstrar o sistema multiagente.

## 🚀 Como Usar

### Opção 1: Servidor HTTP simples

```bash
# Terminal 1: Iniciar API
python -m api.main

# Terminal 2: Iniciar servidor HTTP
cd frontend
python -m http.server 8080
```

Acesse: http://localhost:8080

### Opção 2: Abrir direto no navegador

```bash
# Terminal 1: Iniciar API
python -m api.main

# Terminal 2: Abrir arquivo
# Windows:
start frontend/index.html

# Linux/Mac:
xdg-open frontend/index.html
# ou
open frontend/index.html
```

## 📋 Funcionalidades

### 💬 Consultas
- Interface de chat interativa
- Teste queries em linguagem natural
- Veja respostas dos agentes
- Visualize citações (documentos e IRIs)

### ❓ Competency Questions
- Execute CQs individuais com um clique
- Execute todas as CQs de uma vez
- Veja resultados formatados

### 🧠 Reasoner DL
- Teste classificação de classes
- Verifique consistência da ontologia
- Execute realização (tipos inferidos)
- Veja materialização de inferências

### ℹ️ Sobre
- Visualize arquitetura do sistema
- Veja componentes e tecnologias
- Status do sistema em tempo real

## 🎨 Design

Interface moderna com:
- Design responsivo
- Cores gradientes
- Animações suaves
- Feedback visual claro

## ⚙️ Configuração

Se a API estiver em outra porta, edite `frontend/script.js`:

```javascript
const API_URL = 'http://localhost:8000'; // Altere se necessário
```

