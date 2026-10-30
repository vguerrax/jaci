# Refinamento — BL-0009 — Criptografia em repouso — 1.5.0

## Rastreabilidade e objetivo

- Item: [BL-0009](../backlog/items/BL-0009-criptografia-repouso.md).
- Estado: pronto_para_implementacao; responsável: Engenharia Jaci.
- Branch: feature/BL-0009-criptografia-repouso; base develop 3377001.
- Proteger novos backups antes da persistência e verificar a proteção do volume
  PostgreSQL. Preparar o artefato criptografado consumido pela BL-0007.

## Decisões da 1.5.0

- Jaci e backup executam na máquina local do usuário, que permanece ligada.
- PostgreSQL e Caddy ficam em instâncias Oracle distintas; destino externo é a
  instância já existente do Caddy. Nenhum serviço pago novo.
- Chave pública age no Jaci; chave privada guardada pelo usuário fora dos servidores.
- Dispositivo externo e rsync são administrados pessoalmente pelo usuário.
- RPO máximo de 24h, RTO-alvo de 4h e retenção local/remota de 30 dias; comprovar
  restauração e capacidade antes da ativação, sem prometer disponibilidade absoluta.

## Riscos e regras preservadas

- Segurança: dump agrega todos os grupos; criptografia, permissões privadas,
  transporte autenticado e logs sem credenciais/tokens/dados do banco.
- LGPD: fixtures e evidências sintéticas, retenção delimitada e descarte controlado.
- Grupo: backup e restauração preservam pertencimentos e filtros de autorização;
  artefato nunca é exposto por rota web ou pelo conteúdo público do Caddy.
- Offline/sincronização: falha do backup/cópia não interrompe aplicação ou fila local.
- Histórico financeiro: restaurar valores, estados e registros completos; nunca
  restaurar testes sobre produção ou excluir a última cópia válida por engano.
- Recorrência: preservar datas/ciclos existentes, sem recalcular durante restauração.
- Template/execução: preservar snapshots e vínculos, sem propagação retroativa.

## Contrato funcional e interfaces

1. Acrescentar BACKUP_ENCRYPTION_ENABLED (false por padrão para compatibilidade)
   e BACKUP_RECIPIENTS_FILE. Exigir arquivo válido de destinatários públicos age
   quando a criptografia estiver ligada; nunca exigir chave privada no container.
2. Manter BACKUP_ENABLED, tratamento de SQLite, SSL, cron e contratos existentes.
   Com criptografia habilitada, nenhuma falha pode cair silenciosamente no modo
   sem criptografia. Ativação em produção é explícita e posterior à validação.
3. Implementar orquestração supervisionada de pg_dump customizado, pg_restore
   --list e age: duplicar o fluxo em memória limitada para validação e criptografia,
   sem temporário de dump aberto no HD. Tratar fechamento antecipado do consumidor
   de catálogo, pipe quebrado e cancelamento sem deadlock. Usar age, não criar
   algoritmo criptográfico próprio. Esperar sucesso de todos antes de publicar.
4. Artefatos: jaci_<timestamp-UTC>_<identificador>.dump.age e manifesto JSON
   schema_version=1 com backup_id, created_at UTC, postgresql_version, filename,
   size_bytes, ciphertext_sha256 e recipient_id. Não incluir URL, e-mail, grupos
   ou segredo. Diretório 0700; arquivos 0600; temporários privados e nomes únicos.
5. Publicar ciphertext por rename atômico e manifesto por último como marcador
   de conjunto completo. O consumidor ignora artefatos sem manifesto íntegro.
   Remover temporários próprios em falha/sinal; não publicar sucesso parcial.
6. Aplicar retenção de 30 dias só aos conjuntos reconhecidos e completos do Jaci;
   ignorar links e arquivos alheios e preservar o conjunto válido mais recente.
   Não alterar a retenção legada de *.dump fora de seu modo/namespace.
7. Não converter ou apagar dumps antigos automaticamente. Documentar conversão,
   conferência e decisão de remoção dos originais pelo usuário. Exceções de
   legados em texto aberto devem constar da evidência de ativação.
8. Documentar geração/guarda de duas cópias recuperáveis da chave privada pelo
   usuário, fingerprint público e rotação: novos dumps usam novo destinatário;
   manter chaves antigas até expirar seus backups. Não coletar chaves na conversa.
9. Verificar qual volume contém os dados PostgreSQL. Confirmar controles reais
   OCI e registrar evidência sanitizada. Não propor LUKS, migração de hospedagem,
   criptografia de campos ou IndexedDB nesta entrega. A política de privacidade
   deve distinguir proteção do volume, backups habilitados e legados, sem afirmar
   proteção que ainda não foi ativada ou verificada.

Fontes técnicas: [age](https://github.com/FiloSottile/age) e
[criptografia de volumes OCI](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/blockvolumeencryption.htm).

## Etapa 1 / Ticket 1 — Três subtarefas sequenciais

| Subtarefa | Resultado | Arquivos esperados | Validação focal |
| --- | --- | --- | --- |
| 01 | Contratos e configuração | app/config.py, exemplos sintéticos, tests/test_postgresql_backup.py | Flags, chave ausente/inválida, modo legado/SQLite, manifesto |
| 02 | Pipeline e publicação criptografada | scripts/backup_database.sh, scripts/backup_pipeline.py, Dockerfile e entrypoint | age e PostgreSQL reais descartáveis; falhas, sinais e streams grandes |
| 03 | Recuperação, guarda e evidência | docs/operations/postgresql-backups.md, README, política de privacidade e matriz de testes | Descriptografia/restauração isolada, rotação e revisão documental |

A correção de dependências e manifesto permanece nesta task. A BL-0007 só pode
consumir o contrato pronto; integrar código compartilhado à base dela apenas
pelo fluxo liberado pelo usuário, sem cherry-pick ou merge silencioso entre tasks.

## Cenários TDD após aprovação

- Desabilitado/SQLite não chama age/pg_dump; modo legado mantém comportamento.
- Chave inválida falha antes de produzir dados; ferramenta ausente falha explicitamente.
- Dump ou catálogo inválido, falha age, SIGTERM e falta de espaço não publicam
  conjunto completo nem removem backup válido anterior.
- Fluxo maior que os buffers e pg_dump falhando depois do catálogo não geram
  deadlock nem falso sucesso; nenhum dump aberto é persistido no filesystem.
- SHA-256, tamanho, permissões e campos do manifesto são verificáveis; ciphertext
  corrompido/chave errada não pode ser aceito como restauração bem-sucedida.
- Retenção ignora arquivos e links alheios, par incompleto e preserva último válido.
- Chaves nova/antiga recuperam os dumps correspondentes sem expor segredos.
- PostgreSQL restaurado preserva usuários/grupos, totais, snapshots e recorrências.
- Não criar contratos UI sem necessidade; futuros da task usam xfail(strict=True)
  somente depois da aprovação e são retirados por subtarefa antes do fechamento.

## Git Flow e aprovação

Cada task mantém sua branch própria, derivada da develop, e worktree nela.
Subtarefas opcionais usam sufixos -01, -02 e -03, derivam do pai atualizado e
retornam somente ao pai após validar. Não criar demanda nova para corrigir uma
entrega não publicada; registrar como subtarefa da própria demanda.
Manter a worktree no pai até o usuário liberar develop ou fazer o merge.
Preservar feature/BL-0026-ferramentas-ambiente-testes e seus commits de fechamento
da 1.4.0, ainda sem integração; não misturá-los nem integrá-los automaticamente.

Este refinamento precisa ser aprovado depois do versionamento antes de testes,
código, Dockerfile, cron, templates ou scripts executáveis. A solicitação de
implementar o plano anterior não dispensa esse checkpoint do AGENTS.md.

## Validação e fechamento

- Focal por subtarefa: testes de comportamento do processo/artefatos, sintaxe shell
  e lint configurado; não instalar/usar serviços ou credenciais de produção.
- Final da task: bash scripts/run_tests.sh --coverage, incluindo contratos Node;
  piso 56,18% preservado. Os dois FL-08 permanecem fora do escopo. Nenhum xfail
  próprio pode permanecer ao fechar a implementação.
- PostgreSQL e SSH/SFTP reais somente em containers descartáveis, sem volumes
  do usuário. Gerar chaves efêmeras de teste e removê-las junto dos recursos próprios.
- Validar build Docker e Compose somente com configuração sintética. Não executar
  docker compose que carregue implicitamente .env.production.
- UI não será executada automaticamente: mudanças são operacionais; eventual
  smoke da página legal exige solicitação de execução de navegador.
- Atualizar grafo AST após código. Registrar comandos, hashes e resultados novos;
  contagens da 1.4.0 são referência histórica, não evidência desta versão.
- Não editar .env.test/.env.production, acessar/configurar Oracle, tocar Caddy,
  guardar chaves privadas, montar/formatar dispositivos ou apagar dumps existentes.
  Entregar configurações de exemplo e runbook para ativação explícita pelo usuário.
- Concluir somente após validação operacional, ativação e publicação registradas;
  registrar evidência sanitizada da infraestrutura e resultado da recuperação.

## Progresso

| Etapa/ticket | Concluídas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Implementação da task | 0/3 | 3 | Aguarda aprovação do refinamento versionado |

## Fechamento documental

Implementação e testes executáveis não iniciados. Validações desta etapa são
links locais, escopo e diff documental. Commit e branch identificam a versão
para aprovação. Nenhuma mudança de ambiente, infraestrutura ou dados reais.


## Base de release definida pelo usuário

Após o versionamento deste refinamento, o usuário solicitou sua integração à
develop e a criação de release/v1.5.0. A base de integração desta versão passa
a ser release/v1.5.0. Atualizar a branch da task com essa base antes de código;
subtarefas -nn retornam ao pai, que só retorna à release com liberação do usuário.
Trabalhar somente na worktree atual e mantê-la na branch correspondente à etapa;
não criar outras worktrees. A regra anterior de worktrees próprias foi substituída
por essa instrução explícita. A autorização aqui é de integração documental e
preparação de branches, não de testes/código.
