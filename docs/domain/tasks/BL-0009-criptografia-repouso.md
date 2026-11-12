# Refinamento — BL-0009 — Criptografia em repouso — 1.5.0

> **Abortada pelo usuário em 2026-11-10.** O estado terminal do processo é
> `rejeitado`. As implementações e validações abaixo são histórico, sem entrega
> em produção. Mantido o dump PostgreSQL diário existente, sem criptografia,
> com retenção de 30 dias por padrão. Cópias externas são manuais, sob controle
> do usuário. O código das tasks não deve ser integrado à release.

## Rastreabilidade e objetivo

- Item: [BL-0009](../backlog/items/BL-0009-criptografia-repouso.md).
- Estado: rejeitado; responsável: Engenharia Jaci.
- Branch: feature/BL-0009-criptografia-repouso; base de implementação release/v1.5.0 1cedb61.
- Refinamento original versionado em 3660568, sobre develop 3377001.
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
  piso 60% aplicado por solicitação do usuário em 2026-10-30. Os dois FL-08 permanecem fora do escopo. Nenhum xfail
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

## Progresso histórico anterior ao aborto

| Etapa/ticket | Implementadas | Restantes | Estado |
| --- | --- | --- | --- |
| 1 — Implementação da task | 3/3 | 0 de implementação | em_validacao; suíte e age real informados aprovados; Oracle, recuperação PostgreSQL e publicação pendentes |

## Fechamento documental

No fechamento do refinamento original 3660568, implementação e testes ainda
não haviam começado. A execução autorizada posteriormente está registrada abaixo.
Nenhuma mudança de ambiente, infraestrutura ou dados reais foi efetuada.


## Base de release definida pelo usuário

Após o versionamento deste refinamento, o usuário solicitou sua integração à
develop e a criação de release/v1.5.0. A base de integração desta versão passa
a ser release/v1.5.0. Atualizar a branch da task com essa base antes de código;
subtarefas -nn retornam ao pai, que só retorna à release com liberação do usuário.
Trabalhar somente na worktree atual e mantê-la na branch correspondente à etapa;
não criar outras worktrees. A regra anterior de worktrees próprias foi substituída
por essa instrução explícita. A autorização aqui é de integração documental e
preparação de branches, não de testes/código.


## Execução autorizada — 2026-10-30

Pedido pós-versionamento: “Implemente a BL-009 também”, interpretado como BL-0009
pelo contexto da 1.5.0. Mantida a restrição da implementação anterior: sem executar
testes. Contratos são escritos antes do pipeline, mas nenhum pytest, age,
PostgreSQL, Docker ou migração será executado nesta entrega. A branch foi
avançada por fast-forward até release/v1.5.0 1cedb61, na worktree atual.

O contrato compartilhado scripts/backup_artifacts.py é a mesma versão entregue
na BL-0007 (e820626). Reutilizado isoladamente como biblioteca de schema/hash,
sem trazer replicador, agenda SFTP ou commits da outra task. O produtor não depende
da BL-0007 e mantém a interface python -m scripts.backup_pipeline esperada por ela.
Não há integração entre branches, release, develop ou main. Usuário mantém
controle de .env.test/.env.production, banco, chaves e instâncias Oracle.

Subtarefa 01: flags opt-in, destinatários públicos imutáveis, fingerprint do
conjunto de destinatários e contratos de fluxo/falha/recuperação escritos.
Conferência AST e diff somente; execução dos contratos permanece pendente.

Subtarefa 01: 83a00d0. Subtarefa 02 implementa pg_dump customizado em stdout,
tee não bloqueante para pg_restore --list e age, buffers limitados a 1 MiB por
consumidor, supervisão de todos os códigos e cleanup em falha/sinal. Chave pública
validada antes do banco, manifesto schema 1 por último, retenção exclusiva de
pares completos preservando o mais recente. Script legado despacha por flag;
Docker/cron recebem age e as duas variáveis permitidas. Nenhum backup executado.


## Entrega das três subtarefas — 2026-10-30

| Subtarefa | Implementação | Validação |
| --- | --- | --- |
| 01 | 83a00d0 — flags, destinatários públicos e contratos/schema compartilhado | AST/diff; testes escritos e não executados |
| 02 | 00d11c7 — pipeline supervisionado, publicação, retenção, Docker e entrypoint | AST/bash -n/diff; sem executar processos de backup |
| 03 | Verificação CLI, runbook de guarda/rotação/legados, política e ficha de ativação neste registro | Conferência estática; ensaios e evidência de volume pendentes |

- O contrato sem argumentos python -m scripts.backup_pipeline atende ao produtor
  esperado pelo coordenador BL-0007; --verify confere par local sem banco.
- A política de privacidade distingue backups opcionais, legados abertos e
  proteção do volume dependente de verificação, sem afirmar ativação inexistente.
- Sem acesso à Oracle: identificar volume e confirmar controles OCI é passo
  manual obrigatório, registrado como pendente na ficha de ativação. A referência
  técnica pública não constitui evidência do ambiente específico.
- Runbook cobre duas cópias privadas fora dos servidores, rotação/fingerprints,
  recuperação isolada cronometrada e conversão manual de legados sem exclusão
  automática. Backups históricos, chaves e dados do usuário não foram tocados.
- Validação desta entrega: AST dos seis Python afetados, bash -n dos dois shell,
  links locais, git diff --check e atualização graphify AST. Nenhum teste, age,
  PostgreSQL, Docker, migração, SSH, restauração ou build executado.
- Commits locais com hooks desativados para evitar testes indiretos; sem push/CI
  ou merge de task/release/develop/main. Mesma worktree, mantida no pai BL-0009.
- Sem xfail próprio. As 3/3 subtarefas de implementação estão entregues;
  em_validacao até execução autorizada, integração BL-0007, evidência de volume,
  recuperação, ativação e publicação. Nenhuma aprovação operacional foi presumida.

Documentos operacionais: [runbook](../../operations/backup-encryption.md) e
[ficha de ativação](../../operations/backup-encryption-activation.md).


## Validação informada pelo usuário e ajuste de piso — 2026-10-30

Após a entrega 0f3f0f7, o usuário forneceu o resultado de
`./scripts/run_tests.sh --coverage`: 332 itens coletados, **329 passed, 1 skipped,
2 xfailed e 19 warnings em 63,35s**; cobertura de `app` **60,04%**. O estado local
conferido para este registro estava limpo no candidato 0f3f0f7. A execução foi do
usuário; o Codex não repetiu a suíte nem instalou dependências.

- Skip: test_real_age_decryption_rotation_wrong_key_and_corruption, requer age e
  age-keygen reais. Os demais contratos de criptografia usam executáveis sintéticos.
- Xfails esperados: dois FL-08, fora desta demanda. Avisos de depreciação de
  datetime.utcnow são de python-jose; nenhuma falha de teste foi reportada.
- Cobertura medida com --cov=app e branches; não cobre os scripts operacionais
  nem representa execução UI. O teste de contratos Node passou via pytest.
- Na sequência, o usuário pediu explicitamente “Ajuste o mínimo de cobertura para
  60%”. Atualizados .coveragerc e orientação corrente; CI já consome esse arquivo.
  A evidência 60,04% atende numericamente ao novo piso, margem de 0,04 p.p.; não
  constitui uma nova execução após a mudança de configuração.
- Conferência deste ajuste: leitura estática do INI e diff. Sem novos testes ou
  alteração de ambiente. Os testes existentes do runner já exercitam aplicação
  do piso e propagação de falhas, sem valor de 56,18% fixado nos contratos.

Implementação permanece 3/3 e estado em_validacao. Integração BL-0007, ensaio age
real, PostgreSQL/recuperação cronometrada, evidência do volume OCI, build, ativação
e publicação continuam pendentes. Sem merge/push ou liberação operacional presumida.


## Teste age real informado pelo usuário — 2026-10-30

Comando fornecido:

```bash
./scripts/run_tests.sh tests/test_backup_encryption.py::test_real_age_decryption_rotation_wrong_key_and_corruption -v
```

Resultado: **1 passed em 1,08s**. O estado local conferido para este registro
estava limpo em 008f9a0. Evidência fornecida pelo usuário, sem reexecução pelo
Codex. O cenário anteriormente ignorado foi aprovado individualmente: age e
age-keygen reais, criptografia/descriptografia com duas identidades efêmeras,
rotação de destinatários, recusa de chave incorreta e detecção de corrupção.
PostgreSQL permanece simulado neste contrato; não foram usadas identidades de
recuperação do usuário ou dados de produção.

A pendência do contrato age real está resolvida. Esta execução não mede cobertura
e não comprova restauração PostgreSQL real, RPO/RTO, build, volume OCI,
integração SFTP/BL-0007, ativação ou publicação. Implementação 3/3, estado em_validacao e branch pai
preservados; sem merge ou mudança de ambiente pelo Codex.


## Aborto solicitado pelo usuário — 2026-11-10

O usuário encerrou a demanda: backups sem criptografia e cópias externas manuais.
As três subtarefas haviam sido implementadas, mas não foram publicadas; o código
não deve ser integrado. Evidências anteriores permanecem históricas. As pendências
de teste, integração, volume Oracle, recuperação e ativação deixam de ser trabalho
ativo destas demandas. Estado terminal rejeitado, sem reutilizar identificador.

Código atual de backup restaurado à base release/v1.5.0 1cedb61 na worktree
corrente, sem reescrever commits, apagar branches ou modificar ambientes, banco,
dumps e chaves. A alteração independente de cobertura mínima de 60% é mantida.
Nenhum teste ou job de backup executado. Conferência estática do script, agenda,
volume versionado e diff. A base já conserva dump customizado diário 02h30,
retenção padrão de 30 dias e volume /opt/jaci/backups:/var/backups/jaci.

A release 1.5.0 perde o escopo de criptografia/replicação. No pedido seguinte,
o usuário solicitou o roadmap refeito: acesso à conta/sessão passa à 1.5.0,
e versões seguintes são antecipadas uma posição. Não há autorização implícita
de merge, deploy ou implementação das próximas tasks.
