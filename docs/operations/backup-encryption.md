# Criptografia de backups e proteção do volume — BL-0009

> **ARQUIVADO — BL-0009 abortada pelo usuário em 2026-11-10.** Este conteúdo
> descreve o trabalho descartado e não deve ser usado para ativação. Mantidos
> dumps diários sem criptografia, retenção padrão de 30 dias e cópias manuais.
> Ensaios/ativação abaixo não são mais trabalho pendente. Código e exemplo de
> implantação foram retirados da worktree; consulte os commits históricos.

## Entrega e limites

A implementação 1.5.0 acrescenta criptografia age opcional para novos backups
PostgreSQL. O processo roda na máquina local que hospeda o Jaci; banco e Caddy
continuam em instâncias Oracle separadas. A chave privada age fica com o usuário,
fora de todos os servidores. O Jaci recebe apenas destinatários públicos.

**Durante a implementação, testes não foram executados por solicitação do usuário.**
Depois da entrega, o usuário informou suíte aprovada (329 passes/1 skip/2 xfail)
e aprovou isoladamente o teste age real antes ignorado (1 passed em 1,08s), com
chaves efêmeras e PostgreSQL simulado. Os ensaios de restauração PostgreSQL
seguem pendentes. Configuração de
ambiente, Oracle, banco, Caddy, discos e backups existentes não foram alterados.
A ativação depende de validar a recuperação e registrar evidências do volume.
Não há novo serviço pago, LUKS, migração de hospedagem, criptografia de campos
ou alteração do IndexedDB. A proteção do volume não substitui a dos arquivos
copiados dele; os controles têm evidências separadas.

## Preparar e guardar a chave com o usuário

Executar somente em máquina/área privada de recuperação escolhida pelo usuário,
fora do repositório e dos servidores, com age/age-keygen instalados:

```bash
umask 077
age-keygen -o /AREA_PRIVADA/jaci-recovery.agekey
age-keygen -y /AREA_PRIVADA/jaci-recovery.agekey > /AREA_PRIVADA/jaci-recipients.txt
```

A geração imprime o destinatário público e grava a identidade privada no arquivo
agekey. Preparar duas cópias recuperáveis da identidade privada em locais separados
sob controle do usuário, com acesso restrito; validar descriptografia usando cada
cópia. Se uma cópia tiver proteção adicional por senha, ensaiar também essa etapa
e guardar o meio de recuperação separadamente. Perder todas
as identidades que atendem a um conjunto inviabiliza sua recuperação.

Transferir somente `jaci-recipients.txt` ao host Jaci. Esse arquivo contém uma ou
mais chaves públicas nativas `age1...`, uma por linha, podendo conter comentários
`#` e linhas vazias. Não usar a identidade privada, senha interativa, destinatário
SSH ou plugin. São aceitos até 32 destinatários públicos distintos. O age valida
os destinatários antes de qualquer dump. Cada destinatário pode recuperar o
conjunto; não é um esquema que exige aprovação de múltiplas chaves.

A chave SSH privada de automação da BL-0007 tem outra função e outro ciclo de
vida. Ela autentica SFTP e não deve ser usada como identidade age de recuperação.
Não coletar nenhuma chave privada em conversa, log, imagem Docker ou Git.

## Configuração e ativação explícita

Exemplo de configuração, sem editar ambientes automaticamente:

```dotenv
BACKUP_ENABLED=true
BACKUP_DIR=/var/backups/jaci
BACKUP_RETENTION_DAYS=30
BACKUP_ENCRYPTION_ENABLED=true
BACKUP_RECIPIENTS_FILE=/run/secrets/jaci-backup-recipients.txt
```

Usar o [.env.example](../../.env.example) e o
override histórico (`git show 0f3f0f7:deploy/compose.backup-encryption.example.yml`), ajustados
pelo operador. O arquivo de destinatários deve ser absoluto, regular, não vazio,
sem link e conter somente material público. Montá-lo somente para leitura. Não
montar a identidade de recuperação no Jaci.

Preparar BACKUP_DIR privado (0700), com espaço suficiente, antes de habilitar.
O produtor cria diretório ausente com 0700, mas recusa diretório existente com
acesso de grupo/outros, sem alterar silenciosamente permissões do ambiente.
Novos arquivos têm 0600. Não modificar ou remover dumps existentes para ativar.
O modo legado, com a flag false por padrão, mantém seu comportamento anterior.

O Dockerfile inclui age e clientes PostgreSQL. A instalação de pacotes só ocorre
na construção explicitamente feita pelo operador; esta entrega não construiu ou
subiu imagem. O entrypoint permite ao cron somente as duas novas variáveis além
das já necessárias para backup, sem identidade privada ou segredos da aplicação.

Após preparar uma implantação de validação isolada, o operador pode executar:

```bash
docker compose exec jaci /app/scripts/backup_database.sh
```

O script despacha para `python3 -m scripts.backup_pipeline` quando a criptografia
está ligada. Sem flag, mantém o backup legado; BACKUP_ENABLED=false e SQLite não
iniciam pg_dump, pg_restore ou age. Flag/arquivo inválido ou ferramenta ausente
impedem o backup criptografado, sem fallback para arquivo aberto. A API Python
não carrega dotenv ou aplicação: usa somente o ambiente exportado ao processo.

A interface sem argumentos `python -m scripts.backup_pipeline` é também a
esperada pelo coordenador da BL-0007. A integração das duas branches e a validação
conjunta continuam dependendo de liberação do usuário. A agenda desta base ainda
é o cron diário existente; a retentativa horária e SFTP pertencem à BL-0007.

## Fluxo, publicação e retenção

O produtor divide pg_dump customizado em dois consumidores: pg_restore --list
valida o catálogo e age criptografa todo o fluxo. Não há arquivo de dump aberto
intermediário no HD. Os buffers são limitados a 1 MiB por consumidor, além dos
pipes do kernel; backpressure impede crescimento proporcional ao banco.

pg_restore pode terminar após o catálogo. Seu fechamento de pipe é tratado sem
interromper o fluxo completo para age. O retorno de todos os processos deve ser
zero; falha tardia do dump, catálogo inválido, age encerrado, falta de espaço,
SIGTERM/SIGINT ou limite de uma hora impedem publicação. Filhos são encerrados e
recolhidos, e temporários próprios são removidos. Não existe garantia de cleanup
após SIGKILL/falha de energia; temporários que restarem são criptografados e não
constituem conjunto confirmado. Inventariá-los antes de qualquer remoção manual.

Publicação em nomes únicos UTC com UUID:

- `jaci_<YYYYMMDD_HHMMSS>_<uuid>.dump.age`, binário age.
- Mesmo ID com `.manifest.json`, schema_version=1, publicado por último.

O ciphertext é sincronizado e renomeado antes do manifesto atômico privado.
O manifesto contém backup_id, created_at UTC, postgresql_version (versão do
cliente pg_dump), filename, size_bytes, ciphertext_sha256 e recipient_id. O
fingerprint `sha256:` identifica a lista pública ordenada de destinatários
(distintos, separados por newline, incluindo newline final), sem armazenar a
identidade privada. O timestamp representa o início do dump, para não melhorar
artificialmente o RPO ao final de uma geração longa. Nenhum URL, nome de grupo,
catálogo ou credencial é gravado no manifesto/log de sucesso.

Verificação local, somente leitura e sem banco/ferramentas externas:

```bash
python -m scripts.backup_pipeline --verify /BACKUP/jaci_ID.manifest.json
```

Retorna JSON com os metadados após conferir schema, nomes, UTC, cabeçalho age,
tamanho e SHA-256. Código 0 significa conferência de arquivo íntegra; código 1
indica falha. Isso não comprova descriptografia nem restauração. O produtor sem
`--verify` retorna 0 para sucesso/desativado, 1 para falha e 2 para configuração
inválida. Erros externos são sanitizados; não imprime stderr de pg_dump/age.

Após publicação válida, retenção remove somente pares completos e reconhecidos
com idade maior que BACKUP_RETENTION_DAYS, preservando o mais recente íntegro.
Ignora links, subdiretórios, arquivos estranhos e pares inválidos/incompletos.
Modo criptografado não executa retenção sobre `.dump` legados. Falha de retenção
mantém o novo conjunto válido e sinaliza erro operacional. O volume local continua
sendo a cópia persistente mesmo quando SFTP estiver indisponível após integrar a
BL-0007. Nenhuma falha altera dados do produto ou readiness da aplicação.

## Recuperação isolada e RTO

Iniciar cronômetro antes de obter conjunto e identidade privada. Selecionar os
dois arquivos do mesmo ID, conferindo a origem e sua correspondência ao inventário.
Usar uma área nova 0700, `umask 077` e PostgreSQL vazio/isolado, sem volumes ou
endpoints de produção. A chave é fornecida pelo usuário na máquina de recuperação.

```bash
python -m scripts.backup_pipeline --verify /RECUPERACAO/jaci_ID.manifest.json
age --decrypt -i /AREA_PRIVADA/jaci-recovery.agekey \
    -o /RECUPERACAO/restore.dump /RECUPERACAO/jaci_ID.dump.age
pg_restore --list /RECUPERACAO/restore.dump > /RECUPERACAO/catalog.txt
```

Interromper na primeira falha; não prosseguir com saída parcial ou chave errada.
A descriptografia manual produz dump aberto somente na área privada de
recuperação. Conferir versão dos clientes compatível com o dump. Nenhum comando
usa DATABASE_URL de produção ou escolhe destino implicitamente.

Exemplo para PostgreSQL descartável já reservado em loopback na porta 55432,
com autenticação própria e nome conferido pelo operador:

```bash
createdb --host=127.0.0.1 --port=55432 --username=postgres jaci_recovery
pg_restore --exit-on-error --no-owner --no-acl \
    --host=127.0.0.1 --port=55432 --username=postgres \
    --dbname=jaci_recovery /RECUPERACAO/restore.dump
```

Não usar --clean ou banco existente. Conferir revisão Alembic, usuários/grupos,
vínculos e autorizações, categorias, templates/snapshots, execuções/itens/versões,
quantidades, valores e totais financeiros, estados, datas e recorrências com o
inventário anterior. Não recalcular ciclos ou propagar templates durante o ensaio.
Parar o cronômetro ao fim da conferência: alvo <=4h; RPO <=24h pela data do backup
válido recuperável. Testar ambas as cópias da chave, chave incorreta e corrupção
em cópias descartáveis. Registrar somente evidências sanitizadas.

Conferir também a restauração do conjunto obtido por SFTP e da redundância rsync
sob controle do usuário após integrar a BL-0007. O usuário mantém seu procedimento
manual de HD/pen drive; esta task não monta, formata ou sincroniza dispositivos.
A remoção da área aberta de recuperação é decisão explícita do operador após
registrar o resultado. Não restaurar estes ensaios sobre produção.

## Rotação de destinatários

Gerar nova identidade fora dos servidores, guardar duas cópias e validar a
recuperação. Atualizar somente a lista pública montada no Jaci; trocar arquivo
por rename no host pode exigir recriar o container para renovar o bind mount de
arquivo. Fazer isso explicitamente, conferindo o novo fingerprint nos manifestos.
Guardar a associação entre cada fingerprint e os aliases das identidades
necessárias no inventário privado de recuperação. O pipeline congela a lista em
memória antes do preflight, evitando rotação entre validação e criptografia da
mesma execução.

Pode-se manter destinatários antigo e novo temporariamente; qualquer um deles
poderá recuperar os novos conjuntos. Depois de validar o novo, remover o antigo
da lista pública para futuros backups. Conservar identidades antigas enquanto
houver qualquer conjunto correspondente, inclusive externo e rsync mantido além
de 30 dias. Não recriptografar ou remover conjuntos antigos automaticamente.

## Tratamento manual dos dumps legados

Inventariar `.dump` existentes, tamanho, data, local e permissões; registrá-los
como exceções de confidencialidade até conversão conferida. Não converter ou
apagar originais durante a implementação ou ativação automática.

Em área privada sob controle do operador, após conferir o catálogo do original:

```bash
pg_restore --list /LEGADO/original.dump > /RECUPERACAO/original-catalog.txt
age --encrypt -R /AREA_PRIVADA/jaci-recipients.txt \
    -o /RECUPERACAO/legacy-copy.dump.age /LEGADO/original.dump
age --decrypt -i /AREA_PRIVADA/jaci-recovery.agekey \
    -o /RECUPERACAO/legacy-roundtrip.dump /RECUPERACAO/legacy-copy.dump.age
cmp /LEGADO/original.dump /RECUPERACAO/legacy-roundtrip.dump
pg_restore --list /RECUPERACAO/legacy-roundtrip.dump > /RECUPERACAO/legacy-catalog.txt
```

Estes comandos não criam automaticamente um par elegível à BL-0007. Para esse
uso, o operador precisa preparar nomes/manifesto no schema 1 com criação original,
versão do cliente, fingerprint, tamanho/hash, e conferir o par; não alterar a data
antiga para aparentar backup novo. Validar restauração isolada e guarda das chaves
antes de decidir a remoção explícita do original e do roundtrip aberto. Até lá,
manter a exceção registrada. Nenhum rsync --delete ou rotina de exclusão legada
é introduzido por esta task.

## Verificação do volume PostgreSQL na Oracle

Não há acesso à infraestrutura autorizado nesta implementação. O operador deve:

1. Identificar o data_directory do PostgreSQL e mapear seu filesystem/volume real.
   Se rodar em container, conferir somente os mounts pertinentes, sem publicar
   ambiente ou credenciais. Distinguir o volume do banco, HD local e volume Caddy.
2. No console OCI, correlacionar esse caminho com boot/block volume e conferir
   proteção em repouso, tipo de chave e controles de acesso efetivamente usados.
3. Registrar alias sanitizado do recurso, data, operador e evidência de conferência.
   Não inferir o controle do volume do banco apenas da configuração do Jaci.

A [documentação OCI](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeencryption.htm)
descreve criptografia em repouso dos boot/block volumes com chaves gerenciadas
pelo provedor por padrão. Essa descrição não é evidência de qual volume hospeda
este PostgreSQL. Não criar Vault, chave paga, disco criptografado adicional ou
migração para preencher o registro. A [ficha de ativação](backup-encryption-activation.md)
permanece pendente até o operador confirmar os recursos reais.

Fontes: [age](https://github.com/FiloSottile/age/blob/main/doc/age.1),
[pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html).
