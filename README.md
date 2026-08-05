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
| Banco de dados | SQLite em desenvolvimento e PostgreSQL em produção |
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
DATABASE_URL=sqlite:///./data-dev/jaci.db
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
python run.py
```
Acesse: http://localhost:8000

O `run.py` aplica as migrações e aceita porta, restart automático e arquivo de
ambiente:

```bash
python run.py --port 8000 --restart --env-file .env
python run.py --port 8000 --no-restart --env-file .env.production
```

## 🐳 Docker e publicação

Em produção, configure `DATABASE_URL` com uma conexão PostgreSQL gerenciada:

```env
DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/jaci
DATABASE_SSL_MODE=require
BACKUP_ENABLED=true
BACKUP_DIR=/var/backups/jaci
BACKUP_RETENTION_DAYS=30
```

O script de publicação recebe um arquivo de ambiente opcional, cria o banco
quando ele não existir, aplica as migrações e publica o container:

```bash
./publish.sh
./publish.sh .env.production
./publish.sh /caminho/ambiente.env
```

Comandos úteis
```bash
# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Recriar após alterações
docker-compose up -d --build --force-recreate
```

### Backup automático do PostgreSQL

O container servidor cria um dump diário às 02:30 no fuso
`America/Sao_Paulo`, mantém 30 dias por padrão e persiste os arquivos do
container em `/opt/jaci/backups` no host. A rotina ignora SQLite.

Para executar manualmente e consultar o log:

```bash
docker compose exec jaci /app/scripts/backup_database.sh
docker compose exec jaci tail -n 100 /var/log/backup.log
```

Consulte o procedimento completo, incluindo retenção e restauração segura em
banco isolado, em
[docs/operations/postgresql-backups.md](docs/operations/postgresql-backups.md).
O volume local é a única cópia automática atual; recomenda-se replicação futura
para armazenamento externo. Essa evolução é acompanhada no
[BL-0007](docs/domain/backlog/items/BL-0007-replicacao-externa-backups.md).

## Banco de dados e migrações

- Desenvolvimento: SQLite configurado em `.env`.
- Produção: PostgreSQL em nuvem configurado no arquivo de ambiente de produção.
- Migrações: Alembic, aplicadas por `run.py` e `publish.sh`.

Para criar o banco e aplicar migrações manualmente:

```bash
python -m scripts.create_database
python -m scripts.apply_migrations
```

Para criar uma nova migração:

```bash
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```

### Migrar SQLite para PostgreSQL

Primeiro aplique as migrações no PostgreSQL. Depois execute:

```bash
DATABASE_URL='postgresql+psycopg://usuario:senha@host:5432/jaci' \
python -m scripts.migrate_sqlite_to_postgres \
  --source /opt/jaci/data/jaci.db
```

O argumento `--source` aceita tanto o caminho do arquivo quanto uma URL
`sqlite:///`. O destino vem de `DATABASE_URL` no arquivo indicado por `ENV_FILE`,
ou pode ser informado com `--target`. O migrador preserva IDs e relacionamentos
e recusa destinos já populados. Use `--replace` somente quando quiser substituir
explicitamente todos os dados do destino.

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
├── data-dev/             # Banco SQLite local de desenvolvimento
├── Dockerfile
├── docker-compose.yml
├── migrations/           # Migrações Alembic
├── run.py                # Inicialização local/produção
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
  grupos, Home operacional, consulta básica da agenda/histórico, aprendizado de
  templates e operação offline de execuções com fila local, sincronização e
  resolução explícita de conflitos.
- Em evolução: cobertura e rastreabilidade offline remanescente, histórico de
  preços e análise de gastos.

O [backlog ativo](docs/domain/backlog/README.md) é a fonte de verdade para o
estado das demandas. Contratos futuros usam `xfail(strict=True)` até a
implementação aprovada; contratos legados divergentes são rastreados no item
correspondente do backlog.

### Home operacional

A tela inicial prioriza a compra em andamento ou a próxima compra agendada,
apresenta indicadores isolados pelo grupo ativo, ações rápidas, até três alertas
contextuais e as três compras finalizadas mais recentes. O indicador global de
sincronização informa quando a aplicação está offline, e páginas já visitadas
podem ser recuperadas pelo cache do service worker.

As regras detalhadas estão em
[docs/domain/home-dashboard.md](docs/domain/home-dashboard.md).

### PWA e acesso offline parcial

O Jaci possui manifesto instalável para Android e iOS, abre em modo standalone e
mantém em cache o shell da aplicação, recursos estáticos, APIs GET recentes e
páginas visitadas recentemente. Em caso de indisponibilidade da rede, o
indicador global comunica sincronizado, sincronizando, offline ou erro de
sincronização, e uma tela própria explica quando o conteúdo solicitado ainda não
está armazenado.

No PWA instalado, um indicador global de carregamento aparece em navegações,
formulários e requisições HTMX para evitar múltiplos toques durante o delay de
carregamento.

Também há cache local em IndexedDB para grupos, categorias, listas/templates,
execuções recentes e itens. Durante uma execução, alterações suportadas são
aplicadas primeiro ao estado local e registradas numa fila persistente. Ao
reconectar, a fila sincroniza em ordem, preserva operações com falha e exige
resolução explícita quando há conflito.

O escopo implementado, as limitações atuais e o roteiro de validação manual
estão em
[docs/domain/pwa-offline-foundation.md](docs/domain/pwa-offline-foundation.md).
A cobertura e a rastreabilidade remanescentes estão no
[BL-0001](docs/domain/backlog/items/BL-0001-operacao-offline-cobertura-rastreabilidade.md).

## Testes

Instale as dependências de desenvolvimento e execute a suíte:

```bash
pip install -r requirements-dev.txt
venv/bin/pytest
```

A rastreabilidade entre regras, fluxos e testes está em
[tests/README.md](tests/README.md). Uma execução saudável pode conter casos `XFAIL`
para contratos futuros documentados ou contratos legados explicitamente
rastreados; um `XPASS` é tratado como falha até que o contrato seja revisado.

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
