# 🌙 Jaci

**Sistema de Criação e Gerenciamento de Listas de Compras**

Jaci é uma aplicação web colaborativa para planejamento e execução de compras periódicas. Permite que usuários organizados em grupos criem templates recorrentes de listas de compras, executem-nas em tempo real com múltiplos participantes, registrem valores e quantidades, e acompanhem seus gastos por meio de uma agenda integrada.

O nome é uma homenagem à deusa da lua na mitologia Tupi-Guarani — Jaci, a "Mãe dos Frutos" — que protege as plantas, os ciclos e a fertilidade da terra.

---

## ✨ Funcionalidades

- 🔐 **Autenticação centralizada** — cadastro, login e sessões via Tupã
- 👥 **Grupos** — compartilhe listas com família ou colegas
- 📋 **Templates** — crie modelos de compras com recorrência
- 🔄 **Recorrência** — diária, semanal, quinzenal, mensal ou anual
- 🛒 **Execução em tempo real** — múltiplos usuários na mesma compra
- 💰 **Controle de orçamento** — alertas visuais ao atingir limites
- 📅 **Agenda** — calendário mensal e lista cronológica
- 🔔 **Notificações** — saiba quando alguém inicia ou finaliza uma compra
- 🏠 **Home operacional** — continue a compra ativa, acompanhe indicadores e veja alertas
- ☁️ **Indicador de sincronização** — estado de conexão visível em todas as telas
- 📱 **Responsivo** — funciona no celular durante as compras
- 🌐 **WebSocket + HTMX** — atualizações em tempo real sem recarregar

---

## 🚀 Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Backend | Python 3.12 + FastAPI |
| Banco de dados | SQLite com SQLAlchemy 2.0 |
| Frontend | Jinja2 + HTMX + Alpine.js |
| Tempo real | WebSocket nativo do FastAPI |
| Estilo | Bootstrap 5 + tema personalizado |
| E-mail | Resend (SMTP) |
| Autenticação | Tupã + JWT em cookies httpOnly |

---

## 📦 Requisitos

- Python 3.12+
- pip
- Conta no [Resend](https://resend.com) (para envio de e-mails)

### Opcional (Docker)

- Docker
- Docker Compose

---

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/jaci.git
cd jaci
```

### Configure o ambiente
```bash
cp .env.example .env
```

Edite o arquivo .env com suas configurações:

```env
APP_URL=http://localhost:8000
DATABASE_URL=sqlite:///./data/jaci.db
JWT_SECRET_KEY=uma-chave-secreta-muito-longa-e-aleatoria
TUPA_URL=http://localhost:8001
TUPA_PRODUCT_ID=uuid-do-produto-jaci
TUPA_SERVICE_TOKEN=token-entre-servicos
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASSWORD=re_sua_api_key
SMTP_FROM=onboarding@resend.dev
SMTP_TLS=true
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```
### 4. Execute
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Acesse: http://localhost:8000

## 🐳 Docker
Build e execução
```bash
docker-compose up -d --build
```
O banco de dados SQLite é persistido no volume ./data do host.

Comandos úteis
```bash
# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Recriar após alterações
docker-compose up -d --build --force-recreate

# Backup do banco
cp data/jaci.db backups/jaci_$(date +%Y%m%d_%H%M%S).db
```

## 📁 Estrutura do projeto
```text
jaci/
├── app/
│   ├── models/           # Modelos SQLAlchemy
│   ├── routers/          # Rotas da aplicação
│   ├── services/         # Lógica de negócio
│   ├── utils/            # Segurança, e-mail
│   ├── websocket/        # Gerenciador WebSocket
│   ├── static/           # CSS, JS, imagens
│   └── templates/        # Templates Jinja2
├── data/                 # Volume Docker (banco SQLite)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🔄 Fluxo principal
1. Crie uma conta — a identidade e a sessão são gerenciadas pelo Tupã
2. Crie ou entre em um grupo — convide outras pessoas pelo e-mail
3. Configure categorias — organize seus itens (já vem com 8 categorias padrão)
4. Crie templates — defina listas recorrentes com orçamento
5. Execute compras — gere execuções a partir dos templates
6. Colabore em tempo real — marque itens enquanto outros também compram
7. Acompanhe na agenda — visualize todas as compras no calendário

## Fluxos e evolução

Os fluxos implementados e os contratos futuros são guiados por
[docs/domain/user-flows.md](docs/domain/user-flows.md):

- Implementados: onboarding, templates, geração e execução de compras, colaboração,
  grupos, Home operacional e consulta básica da agenda/histórico.
- Em evolução: aprendizado de templates e histórico de preços/análise de gastos.
- Planejado: operação offline com fila local, sincronização e resolução explícita
  de conflitos.

Os fluxos ainda não implementados já possuem contratos TDD marcados com
`xfail(strict=True)`. Isso mantém a expectativa executável sem esconder a ausência
da funcionalidade.

### Home operacional

A tela inicial prioriza a compra em andamento ou a próxima compra agendada,
apresenta indicadores isolados pelo grupo ativo, ações rápidas, até três alertas
contextuais e as três compras finalizadas mais recentes. O indicador global de
sincronização informa quando a aplicação está offline, e páginas já visitadas
podem ser recuperadas pelo cache do service worker.

As regras detalhadas estão em
[docs/domain/home-dashboard.md](docs/domain/home-dashboard.md).

## Testes

Instale as dependências de desenvolvimento e execute a suíte:

```bash
pip install -r requirements-dev.txt
venv/bin/pytest
```

A rastreabilidade entre regras, fluxos e testes está em
[tests/README.md](tests/README.md). Uma execução saudável pode conter casos `XFAIL`
para contratos futuros documentados; um `XPASS` é tratado como falha até que o
fluxo seja revisado e declarado implementado.

## 🔐 Segurança

- Senhas armazenadas exclusivamente pelo Tupã
- JWT do Tupã validado via JWKS e armazenado em cookie httpOnly
- Renovação de sessão com refresh token
- Isolamento de dados por grupo
- Bloqueio otimista em edições simultâneas

## Migração de usuários existentes

Configure `TUPA_URL`, `TUPA_PRODUCT_ID` e `TUPA_SERVICE_TOKEN`, depois execute:

```bash
python3 -m scripts.migrate_auth_to_tupa
```

O script envia os hashes existentes para `/auth/migrate`, associa o UUID retornado
ao perfil local e remove o hash local após cada migração concluída.

## 📧 Configuração de e-mail
O Jaci usa o Resend para envio de e-mails.

1. Crie uma conta gratuita (100 e-mails/dia)
2. Gere uma API Key
3. Configure no .env:
    - SMTP_USER=resend
    - SMTP_PASSWORD=re_sua_api_key
4. Para usar um domínio personalizado, verifique-o no painel do Resend

## 🌐 Deploy
### Com Caddy (HTTPS automático)
Adicione ao docker-compose.yml:

```yaml
services:
  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
```

Caddyfile:

```text
jaci.app {
    reverse_proxy jaci:8000
}
```

### Cookies seguros
Em produção, altere no código:

- secure=True nos cookies
- APP_URL=https://seu-dominio.com

## 📝 Licença
Este projeto é de uso pessoal. Sinta-se livre para usar, modificar e compartilhar.

## 🌙 Sobre o nome
Jaci, na mitologia Tupi-Guarani, é a deusa da lua e mãe dos frutos. Protetora das plantas, dos ciclos e da fertilidade da terra — o espírito perfeito para um aplicativo que ajuda a organizar a despensa com cuidado e conexão com a natureza.

Feito com 🌙 por vguerrax
