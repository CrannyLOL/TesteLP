# Sistema de Satisfação dos Clientes

Aplicação web para recolher, analisar e exportar dados de satisfação de clientes com painel administrativo.

## 🎯 Funcionalidades

- ✅ Página de votação com 3 níveis de satisfação
- ✅ Painel administrativo com estatísticas em tempo real
- ✅ Gráficos interactivos
- ✅ Exportação de dados em CSV e TXT
- ✅ Interface responsiva para todos os dispositivos
- ✅ Integração com Firebase Realtime Database

## 🚀 Iniciar Rapidamente

### 1. Instale as dependências
```bash
pip install -r requirements.txt
```

### 2. Configure o Firebase (Opcional)
- Descarregue `firebase-credentials.json` do [Firebase Console](https://console.firebase.google.com/)
- Coloque o ficheiro na pasta raiz do projecto
- **Nota**: Se não configurar o Firebase, a aplicação funcionará com armazenamento local (votos_locais.json)

### 3. Execute a aplicação
```bash
python app.py
```

Aceda a: http://localhost:5000

## 🔐 Administrador
- URL: `/admin_login`
- Palavra-passe: `admin1711`

## 📊 Painel de Controlo
- Visualize as estatísticas do dia
- Exporte dados em CSV ou TXT
- Analise tendências dos últimos 7 dias
- Consulte o histórico completo com paginação

## 🛠️ Tecnologias Utilizadas
- **Backend**: Flask (Python)
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Base de Dados**: Firebase Realtime Database

## 📱 Responsividade
Funciona perfeitamente em:
- Computador / Desktop
- Tablet
- Telemóvel
- Modo horizontal / Landscape

---

**Versão 1.0.0** | Fevereiro 2026
