# AGENTS.md

## Projeto: Jaci

Jaci é uma aplicação web para planejamento e execução colaborativa de compras recorrentes.

O sistema permite que grupos (famílias, casais ou pessoas que compartilham despesas) criem templates de listas de compras, executem essas listas colaborativamente, registrem valores pagos e acompanhem gastos ao longo do tempo.

O principal objetivo do produto é ajudar usuários a planejar compras recorrentes, reduzir retrabalho e controlar gastos domésticos.

---

## Princípios do Produto

Toda alteração no sistema deve preservar os seguintes princípios:

1. Mobile-first.
2. Simplicidade operacional durante a compra.
3. Colaboração em tempo real.
4. Funcionamento resiliente em ambientes com conexão instável.
5. Separação clara entre planejamento e execução.
6. Aprendizado contínuo com base no histórico de compras.

Em caso de conflito entre funcionalidades, priorize:

* Confiabilidade sobre tempo real.
* Simplicidade sobre flexibilidade excessiva.
* Persistência de dados sobre atualização instantânea.

---

## Conceitos do Domínio

### Grupo

Unidade de compartilhamento de dados.

Usuários pertencem a um ou mais grupos.

Todos os dados são isolados por grupo.

---

### Categoria

Classificação de itens.

Exemplos:

* Mantimentos
* Hortifruti
* Limpeza

Categorias pertencem ao grupo.

---

### Template

Modelo recorrente de compras.

Contém:

* nome
* recorrência
* orçamento
* itens planejados

Templates não armazenam dados financeiros.

---

### ItemTemplate

Representa um item planejado.

Campos principais:

* nome
* categoria_id
* qtd_planejada
* observacoes

---

### Execução

Instância concreta de uma compra.

Pode ser:

* vinculada a um template
* avulsa

Contém:

* data_agendada
* orçamento
* status
* itens executados

Status possíveis:

* agendada
* em_andamento
* finalizada
* cancelada

---

### ItemExecucao

Representa um item durante a compra.

Campos principais:

* nome
* categoria_id
* qtd_planejada
* qtd_comprada
* valor_unitario
* local
* observacoes
* concluido
* versao

---

## Regras de Negócio Críticas

### Template e execução são independentes.

Alterações no template afetam apenas execuções futuras.

Execuções existentes nunca devem ser alteradas retroativamente.

---

### Execuções podem ser avulsas.

Execuções avulsas não geram recorrência automática.

---

### Recorrência é baseada na data de finalização.

A próxima execução é calculada a partir da data de finalização da execução atual.

Adiantar ou adiar uma execução não altera o ciclo futuro.

---

### Itens adicionados durante a execução não alteram o template automaticamente.

Ao finalizar uma execução vinculada a um template, o sistema pode sugerir a incorporação manual dos novos itens.

A decisão final é sempre do usuário.

---

### Observações são copiadas do template para a execução.

Alterações nas observações durante a execução não modificam o template automaticamente.

O sistema pode sugerir salvar observações recorrentes.

---

### Concorrência é controlada por bloqueio otimista.

ItemExecucao.versao é obrigatório.

Atualizações concorrentes devem falhar explicitamente.

Nunca sobrescreva dados silenciosamente.

---

### Dados são isolados por grupo.

Toda consulta e mutação deve validar o vínculo entre usuário e grupo.

Nunca confie em IDs enviados pelo cliente sem validação de autorização.

---

## Estratégia Offline First

O produto está evoluindo para uma arquitetura offline first.

Atualizações em tempo real são desejáveis, mas não essenciais.

A fonte de verdade do usuário é:

1. Estado local
2. Fila de sincronização
3. API remota

WebSocket é apenas um mecanismo de atualização visual.

Nunca implemente funcionalidades que dependam exclusivamente de conexão contínua.

---

## Arquitetura

O Jaci utiliza uma arquitetura monolítica baseada em renderização híbrida no servidor, complementada por atualizações em tempo real.

### Backend

* Python 3.12+
* FastAPI
* Jinja2
* SQLAlchemy
* PostgreSQL
* Redis
* Pydantic

Responsabilidades:

* Regras de negócio
* Autenticação
* Autorização
* Renderização de páginas
* APIs REST
* Processamento de recorrências
* Sincronização offline
* Notificações

---

### Frontend

* Jinja2 Templates
* HTML
* Tailwind CSS
* JavaScript Vanilla

Responsabilidades:

* Renderização de interface
* Interações do usuário
* Consumo de APIs
* Atualizações em tempo real
* Gerenciamento offline

Evite adicionar frameworks frontend sem necessidade explícita.

Priorize JavaScript nativo e melhoria progressiva.

---

### Tempo Real

* Socket.IO

Responsabilidades:

* Atualização visual em tempo real
* Notificações
* Sincronização de estado entre usuários

WebSocket não deve ser utilizado como mecanismo de persistência.

---

### Banco de Dados

* PostgreSQL

---

### Cache e Mensageria

* Redis

Responsabilidades:

* Cache
* Sessões
* Tokens temporários
* Eventos em tempo real
* Filas de sincronização

---

## Diretrizes de Implementação

### Backend

* Utilizar tipagem estática sempre que possível.
* Utilizar Pydantic para validação de entrada e saída.
* Centralizar regras de negócio em serviços.
* Manter rotas enxutas.
* Evitar lógica de negócio em templates Jinja2.
* Utilizar SQLAlchemy ORM.
* Preferir migrações incrementais.

---

### Frontend

* Priorizar renderização no servidor.
* Utilizar JavaScript apenas quando necessário.
* Garantir funcionamento sem JavaScript sempre que possível.
* Implementar melhorias progressivas para recursos avançados.

---

### Offline First

A estratégia de evolução do produto é offline first.

Novas funcionalidades devem considerar:

1. Persistência local.
2. Sincronização assíncrona.
3. Resolução de conflitos.
4. Funcionamento com conexão intermitente.

Atualizações em tempo real são complementares, não obrigatórias.

---

## Estrutura Arquitetural Recomendada

```text
Cliente

├── Jinja2
├── JavaScript
├── IndexedDB
├── Service Worker
└── Cache API

          ↓

FastAPI

├── Rotas HTML
├── APIs REST
├── WebSocket / Socket.IO
├── Serviços
└── Repositórios

          ↓

PostgreSQL

          ↑

Redis
```

---

### O que evitar

* Lógica de negócio em templates Jinja2.
* Consultas SQL diretamente nas rotas.
* Dependência exclusiva de WebSocket.
* Estado crítico mantido apenas no navegador.
* Introdução de frameworks frontend complexos sem justificativa.
* Acoplamento entre interface e persistência.

---

## Estrutura do projeto
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
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Diretrizes para Implementação

Ao implementar novas funcionalidades:

1. Priorize compatibilidade com dispositivos móveis.
2. Considere cenários offline.
3. Evite múltiplas etapas durante a execução da compra.
4. Minimize a quantidade de campos obrigatórios.
5. Preserve compatibilidade com execuções existentes.
6. Evite migrações destrutivas.
7. Prefira alterações incrementais no modelo de dados.

---

## Ordem de Prioridade do Roadmap

1. PWA e funcionamento offline.
2. Sincronização e resolução de conflitos.
3. Unidades de medida.
4. Histórico de preços.
5. Aprendizado dos templates.
6. Inteligência de compras.
7. Dashboards financeiros.
8. Integrações externas.

---

## O que evitar

Não implementar:

* Dependência obrigatória de conexão ativa.
* Alterações automáticas em templates sem confirmação do usuário.
* Exclusão física de dados históricos.
* Lógica de negócio exclusiva no frontend.
* Acoplamento entre Socket.IO e persistência.
* Consultas sem filtro por grupo.
* Funcionalidades que aumentem significativamente a complexidade da execução da compra.

---

## Critério de Decisão

Ao propor alterações, responda internamente às perguntas:

* Isso reduz o esforço do usuário durante a compra?
* Isso funciona offline?
* Isso preserva o histórico?
* Isso respeita o isolamento por grupo?
* Isso evita retrabalho futuro?
* Isso mantém a separação entre template e execução?

Se qualquer resposta for negativa, reavalie a implementação.

