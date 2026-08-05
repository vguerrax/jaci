# 0002 - Backup automático do PostgreSQL

## Status

Implementada e validada em `feature/backup-postgresql`.

## Contexto

O Jaci usa SQLite no desenvolvimento e PostgreSQL em produção, mas o container
de produção ainda não cria cópias de segurança persistentes. A aplicação precisa
de uma rotina simples e verificável que não dependa do processo web nem confunda
o banco local de desenvolvimento com o banco de produção.

## Decisão

O container servidor executará, via cron, um backup diário do PostgreSQL às
02:30 no fuso `America/Sao_Paulo`.

Regras obrigatórias:

- somente URLs PostgreSQL são aceitas; SQLite é ignorado explicitamente;
- o dump usa o formato customizado de `pg_dump`, sem proprietário nem ACL;
- o arquivo é publicado apenas depois de `pg_restore --list` validá-lo;
- o diretório usa permissão `0700` e os dumps usam `0600`;
- a retenção padrão é de 30 dias e remove somente `jaci_*.dump`;
- o cron recebe apenas as variáveis necessárias ao backup;
- processos auxiliares do container não iniciam o daemon cron;
- o host persiste os arquivos em `/opt/jaci/backups`;
- restauração continua sendo uma operação manual e documentada.

Esta entrega não cria restauração automática, replicação externa, mudanças no
modelo de dados, migrações, APIs ou regras do domínio.

## Plano refinado

1. Rotina de backup
   - contratos para desativação, SQLite, retenção, URLs, SSL, validação,
     publicação atômica e permissões;
   - implementação e validação de sintaxe.
2. Execução no container
   - contratos para dependências, cron, fuso, entrypoint, volume e isolamento
     dos processos auxiliares;
   - implementação no Dockerfile, entrypoint, agenda e Compose.
3. Configuração e operação
   - contrato de carregamento pelo `Settings`;
   - variáveis de exemplo, runbook, README e correção da política de
     privacidade;
   - testes focados, regressão completa, `docker compose config` e build.

## Progresso

- Rotina de backup: 2 de 2 fatias concluídas.
- Execução no container: 2 de 2 fatias concluídas.
- Configuração e operação: 3 de 3 fatias concluídas.
- Total: 7 de 7 fatias concluídas; nenhuma fatia pendente.

## Validação

- sintaxe dos dois scripts validada com `bash -n`;
- 21 contratos focados de backup aprovados;
- regressão completa com 172 testes aprovados e 5 contratos futuros em
  `xfail`;
- configuração de produção validada com `docker compose config`;
- imagem Docker construída com cron, cliente PostgreSQL e fuso configurados.

## Consequências

O volume local do host passa a ser a única cópia criada por esta entrega.
Replicação para armazenamento externo deve ser adicionada futuramente para
proteção contra perda do próprio servidor. Essa evolução é acompanhada no
[BL-0007](../domain/backlog/items/BL-0007-replicacao-externa-backups.md).
