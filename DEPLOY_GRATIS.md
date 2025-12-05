# 🆓 Deploy 100% GRATUITO - Guia Rápido

## ✅ Solução: $0/mês

**Frontend**: Vercel (grátis)  
**Backend**: Render.com (grátis)  
**LLM**: Hugging Face API (grátis) ou OpenAI (créditos grátis)

---

## 🚀 Passo 1: Enviar TODO o Projeto para GitHub

Você só enviou o frontend. Precisa enviar TUDO:

```bash
# Voltar para a raiz do projeto
cd C:/Users/jcesar/Documents/ws-mestrado/ws-mora

# Inicializar git na raiz (se ainda não tiver)
git init

# Adicionar tudo
git add .

# Commit
git commit -m "Sistema completo MAS"

# Conectar ao repositório (se já existe)
git remote add origin https://github.com/4stuno/mora.git

# OU atualizar se já existe
git remote set-url origin https://github.com/4stuno/mora.git

# Enviar tudo
git push -u origin master
```

**⚠️ Importante**: Envie da RAIZ do projeto, não só do frontend!

---

## 🚀 Passo 2: Deploy Backend no Render (Grátis)

1. **Acesse**: https://render.com
2. **Crie conta** (conecte com GitHub)
3. **New → Web Service**
4. **Conecte repositório**: `4stuno/mora`
5. **Configure**:
   - **Name**: `mas-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables**:
   - `OPENAI_API_KEY`: sua chave (ou deixe vazio se não usar)
   - `USE_OLLAMA`: `false` (não funciona no Render)
7. **Create Web Service**
8. **Aguarde deploy** (~10 minutos)
9. **Copie URL**: `https://mas-api.onrender.com`

---

## 🚀 Passo 3: Deploy Frontend no Vercel (Grátis)

1. **Acesse**: https://vercel.com
2. **New Project**
3. **Conecte**: `4stuno/mora`
4. **Configure**:
   - **Root Directory**: `frontend`
   - **Build Command**: (deixe vazio)
   - **Output Directory**: `.`
5. **Environment Variables**:
   - `API_URL`: `https://mas-api.onrender.com` (URL do Render)
6. **Deploy**
7. **Pronto!** URL: `https://seu-projeto.vercel.app`

---

## 💡 Opções de LLM Gratuito

### Opção 1: OpenAI (Mais Fácil)
- **Créditos grátis**: $5 para novos usuários
- **Obter**: https://platform.openai.com/api-keys
- **Configurar no Render**: `OPENAI_API_KEY=sua_chave`

### Opção 2: Google Gemini (Grátis)
- **Plano gratuito**: 60 req/min
- **Obter**: https://makersuite.google.com/app/apikey
- **Configurar no Render**: `GOOGLE_API_KEY=sua_chave`

### Opção 3: Hugging Face (100% Grátis)
- **API gratuita**: Sempre disponível
- **Obter**: https://huggingface.co → Settings → Access Tokens
- **Configurar no Render**: `HUGGINGFACE_API_KEY=hf_seu_token`

---

## ⚠️ Importante: Render Free Tier

- **Dorme após 15min** de inatividade
- **Solução**: Use https://uptimerobot.com (grátis) para fazer ping a cada 5min
- Ou aceite o cold start de ~30s na primeira requisição

---

## ✅ Checklist

- [ ] Fazer push de TODO o projeto para GitHub (raiz)
- [ ] Deploy backend no Render
- [ ] Copiar URL da API
- [ ] Deploy frontend no Vercel
- [ ] Configurar API_URL no Vercel
- [ ] Obter API key de LLM (OpenAI/Gemini/HuggingFace)
- [ ] Configurar no Render
- [ ] Testar sistema completo

---

## 🎉 Pronto!

Sistema 100% gratuito online! 🚀

