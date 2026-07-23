# Backups do PostgreSQL

## Visão geral

O container servidor do Jaci agenda um backup diário às 02:30 no fuso
`America/Sao_Paulo`. A rotina atende somente PostgreSQL; quando `DATABASE_URL`
aponta para SQLite, ela registra que o banco foi ignorado e termina sem criar
arquivo.

Cada backup:

- usa o formato customizado do `pg_dump`;
- omite proprietário e ACL para facilitar a restauração em outro ambiente;
- é escrito como temporário e validado com `pg_restore --list`;
- só recebe o nome final `jaci_YYYYMMDD_HHMMSS.dump` após a validação;
- fica em diretório `0700`, com permissão `0600`;
- participa da retenção somente se o nome terminar em `jaci_*.dump`.

No Compose de produção, `/var/backups/jaci` no container corresponde a
`/opt/jaci/backups` no host. Esse volume local é a única cópia criada por esta
entrega. Replicar os dumps para um armazenamento externo, com criptografia e
política de acesso própria, é uma evolução recomendada.

## Configuração

As variáveis aceitas são:

```env
BACKUP_ENABLED=true
BACKUP_DIR=/var/backups/jaci
BACKUP_RETENTION_DAYS=30
DATABASE_SSL_MODE=require
```

`BACKUP_RETENTION_DAYS` deve ser um inteiro positivo. O padrão é 30. Os valores
`false`, `0`, `no` e `off` em `BACKUP_ENABLED`, sem diferença entre maiúsculas e
minúsculas, desabilitam a rotina.

`DATABASE_SSL_MODE`, quando preenchida, é encaminhada ao cliente PostgreSQL como
`PGSSLMODE`. Use o modo exigido pelo provedor, por exemplo `require` ou
`verify-full`.

O script aceita `postgres://`, `postgresql://` e
`postgresql+psycopg://`. A variante específica do Psycopg é normalizada antes de
chamar as ferramentas nativas do PostgreSQL.

## Execução manual

Para criar um backup com as mesmas variáveis do container:

```bash
docker compose exec jaci /app/scripts/backup_database.sh
```

O comando retorna código diferente de zero se o dump ou sua validação falhar. Em
caso de falha, o arquivo temporário é removido e nenhum dump final é publicado.

Confira os arquivos persistidos no host:

```bash
sudo ls -lah /opt/jaci/backups
```

## Agenda e logs

O cron roda apenas no processo servidor padrão do container. Comandos auxiliares
como migrações e criação do banco não iniciam outro daemon.

Consulte o log:

```bash
docker compose exec jaci tail -n 100 /var/log/backup.log
docker compose exec jaci tail -f /var/log/backup.log
```

Uma execução bem-sucedida termina com `Backup PostgreSQL concluído` e o caminho
do arquivo. Credenciais da URL não são escritas no log.

## Retenção

Depois de publicar um backup válido, a rotina remove arquivos regulares com nome
`jaci_*.dump` cuja idade ultrapasse `BACKUP_RETENTION_DAYS`. Outros dumps,
subdiretórios e temporários com nomes diferentes não são removidos pela
retenção.

Alterar a retenção afeta a limpeza realizada nas próximas execuções. A remoção
não é executada quando a criação ou a validação do novo dump falha.

## Restauração manual em banco isolado

> A restauração altera o banco de destino. Nunca aponte estes comandos para o
> banco de produção. Crie um banco isolado e confirme nome, host e credenciais
> antes de continuar.

Use uma URL aceita pelas ferramentas PostgreSQL, sem o sufixo
`+psycopg`. Primeiro valide o catálogo do dump:

```bash
export DUMP_FILE=/opt/jaci/backups/jaci_YYYYMMDD_HHMMSS.dump
pg_restore --list "$DUMP_FILE"
```

Crie um banco vazio por meio da ferramenta ou painel do provedor. Exemplo com
acesso administrativo:

```bash
export POSTGRES_ADMIN_URL='postgresql://usuario:senha@host:5432/postgres'
psql "$POSTGRES_ADMIN_URL" \
  --set ON_ERROR_STOP=1 \
  --command 'CREATE DATABASE jaci_restore;'
```

Restaure somente no banco isolado:

```bash
export RESTORE_DATABASE_URL='postgresql://usuario:senha@host:5432/jaci_restore'
pg_restore \
  --dbname="$RESTORE_DATABASE_URL" \
  --no-owner \
  --no-acl \
  --exit-on-error \
  "$DUMP_FILE"
```

Depois da restauração:

1. configure temporariamente o Jaci para o banco isolado;
2. execute `python -m scripts.apply_migrations` para aplicar revisões posteriores
   ao dump, se existirem;
3. confira a revisão com `alembic current`;
4. valide usuários, grupos, templates, execuções e totais por amostragem;
5. descarte o banco de teste somente após registrar o resultado da validação.

Não há script de restauração automática. Essa decisão mantém explícita a escolha
do destino e reduz o risco de sobrescrever dados de produção.
