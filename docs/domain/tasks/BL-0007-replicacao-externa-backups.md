# Refinamento — BL-0007 — Cópia externa por SSH/SFTP — 1.5.0

## Rastreabilidade e objetivo

- Item: [BL-0007](../backlog/items/BL-0007-replicacao-externa-backups.md).
- Estado: pronto_para_implementacao; responsável: Engenharia Jaci.
- Branch: feature/BL-0007-replicacao-externa-backups; base develop 3377001.
- Replicar artefatos criptografados da BL-0009 na instância do Caddy e comprovar
  recuperação independente do HD local. Sequência da versão: BL-0009 → BL-0007.

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

1. BACKUP_REMOTE_ENABLED=false por padrão. Quando habilitado, exigir host, porta
   (padrão 22), usuário, diretório remoto, arquivo de chave SSH e known_hosts em
   configuração BACKUP_SFTP_*. Usar autenticação de serviço dedicada, separada da
   chave age. Nenhuma senha interativa, chave privada age ou serviço pago novo.
2. Usar OpenSSH SFTP em batch, StrictHostKeyChecking=yes, BatchMode=yes e chave
   do host previamente verificada pelo operador. Conta SFTP exclusiva, confinada
   ao diretório dos backups, sem shell/forwarding nem acesso ao conteúdo do Caddy.
   Entregar instruções de provisionamento; não configurar a instância por conta própria.
3. Consumir somente conjunto age completo da BL-0009, com manifesto schema 1,
   tamanho e SHA-256 local conferidos. Rejeitar dump aberto, link, manifesto inválido,
   caminho com travessia e arquivo fora do namespace. Não reler o banco para enviar.
4. Enviar ciphertext e manifesto com nomes temporários únicos; ler novamente o
   ciphertext remoto em fluxo e comparar tamanho/hash. Renomear artefato para
   definitivo e publicar manifesto por último. Somente então registrar réplica
   concluída. Repetir backup_id existente confere e não duplica; conteúdo diferente
   sob o mesmo identificador é erro, nunca overwrite silencioso.
5. Conservar cron diário 02h30 America/Sao_Paulo. Job horário retenta geração
   falha e envio pendente, com trava compartilhada que impede concorrência com
   o job diário. Contar geração diária concluída para não criar outro dump horário
   desnecessariamente. Conexão indisponível/falha de envio preserva a cópia local.
6. Processar pendências por criação. Limitar tentativas por execução, timeout de
   conexão 30s e execução de transferência 30min; reenfileirar no próximo horário.
   Falhas de backup não afetam processo web, filas ou disponibilidade do produto.
7. Retenção remota 30 dias por rotina própria do servidor: somente conjuntos
   reconhecidos no diretório dedicado, preservando o mais recente válido. Não dar
   acesso administrativo à aplicação nem executar limpeza remota via shell arbitrário.
   Entregar script/runbook ao operador. Temporários abandonados têm limpeza própria
   após 24h, respeitando a janela de execução e sem tocar conjuntos completos.
8. Estado persistente local, atômico e privado: último backup local, última réplica
   confirmada, pendências e erro sanitizado. Comando de status em JSON retorna 0
   saudável, 1 para atraso/falha (inclusive nenhuma réplica ou idade >24h), 2 para
   configuração inválida. Informar modo desativado explicitamente. Não acoplar esse
   estado ao health/readiness web nem adicionar serviço de notificações nesta versão.
9. Inventariar tamanho/espaço disponível antes da ativação; não remover backups
   úteis para esconder falta de espaço. RPO é medido pela última cópia remota válida;
   cron configurado sozinho não comprova RPO. Requisições não usam credenciais do Caddy.
10. Runbook: obter conjunto remoto e conferir hash; usuário fornece sua chave age
    fora dos servidores, descriptografa e valida/restaura somente em PostgreSQL
    vazio e isolado. Validar histórico/grupos e tempo de recuperação <=4h antes
    de ativar. Produção nunca é destino implícito. Documentar também recuperação
    da cópia rsync gerida pelo usuário, sem automatizar dispositivos ou rsync --delete.

Referência: [OpenSSH SFTP](https://man.openbsd.org/sftp).

## Etapa 1 / Ticket 1 — Três subtarefas sequenciais

| Subtarefa | Resultado | Arquivos esperados | Validação focal |
| --- | --- | --- | --- |
| 01 | Contratos e configuração SFTP | app/config.py, exemplos sintéticos, testes de replicação | Flags, credenciais em arquivo, host conhecido, artefatos elegíveis |
| 02 | Envio, retentativa e retenção | scripts de replicação/estado, entrypoint, cron e exemplo de retenção remota | SFTP descartável, interrupção, concorrência, readback e idempotência |
| 03 | Monitoramento e recuperação | runbook, README, matriz de testes e histórico da task | Status atrasado, restauração PostgreSQL cronometrada e evidências |

A BL-0009 é dependência funcional para enviar; preparar contratos e simuladores
é possível antes, mas não declarar integração criptografada aprovada sem testar
artefatos reais da dependência. Trazer dependência pela base liberada pelo usuário;
não misturar task ou integrar à develop automaticamente.

## Cenários TDD após aprovação

- Desativado não acessa rede; configuração incompleta/host desconhecido é recusado
  sem prompt, vazamento de segredo ou fallback inseguro.
- Rejeitar dump aberto, corrupção, par incompleto e caminhos não autorizados.
- Upload parcial, conexão caída, rename falhando e hash divergente nunca confirmam
  réplica nem removem backup local; nova tentativa retoma com o mesmo identificador.
- Conjunto já confirmado não duplica; conflito de conteúdo é explícito.
- Duas execuções não enviam/processam o mesmo conjunto simultaneamente.
- Rotina horária retenta pendência e geração falha, sem novo dump se o diário já
  foi concluído. Falha externa não impede funcionamento da aplicação.
- Retenção ignora arquivos alheios/links e preserva último conjunto completo;
  rotina de temporários não remove upload ainda dentro da janela de execução.
- Status passa a atraso acima de 24h e volta a saudável somente após readback
  confirmado; nunca computar arquivo local como cópia externa.
- Recuperar da instância remota e da cópia rsync em destino descartável; medir RTO
  e conferir isolamento, totais, snapshots e recorrência, sem tocar produção.
- Contratos próprios futuros usam xfail(strict=True) só após aprovação e não
  permanecem pendentes ao fim da task. Não criar serviços pagos ou testes sobre Oracle real.

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
