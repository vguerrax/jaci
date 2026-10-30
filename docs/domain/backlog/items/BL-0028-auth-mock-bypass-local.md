# BL-0028 — Usar AUTH_MOCK como bypass do Tupã para usuários locais

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0028` |
| Título | Usar AUTH_MOCK como bypass do Tupã para usuários locais |
| Versão-alvo | `1.4.0` |
| Tipo | `ajuste` |
| Estado | `em_validacao` |
| Severidade | `N/A` |
| Prioridade | `P1` |
| Data de entrada | `2026-10-29` |
| Origem | Correção explícita do contrato pelo usuário após testar o AUTH_MOCK |
| Ambiente/versão | develop após a integração da BL-0026; 1.4.0 não publicada |
| Responsável | Engenharia Jaci |
| Atualizado em | `2026-10-29` |

### Comportamento observado

O AUTH_MOCK da BL-0026 exige arquivo chamado .env.test, banco SQLite em diretório
marcado, três contas sintéticas e senha fixa. Essas restrições impedem usar a
base de desenvolvimento já existente. O usuário esclareceu que deseja um bypass
do Tupã que apenas confirme a existência do usuário na base configurada.

### Comportamento esperado

APP_ENV=test e AUTH_MOCK=true bastam para ativar o bypass. O login usa um usuário
local existente e ativo, sem consultar o Tupã nem validar senha nesse modo.
Não há restrição ao nome do arquivo de ambiente, tipo/caminho do banco ou contas
do seed. A autorização por grupo continua sendo aplicada.

### Impacto e abrangência

- Impacto: habilitar testes manuais com usuários da base de desenvolvimento.
- Abrangência: configuração, login, identidade HTTP/WebSocket e sessões do mock.
- Frequência: todo uso de AUTH_MOCK fora do cenário sintético da BL-0026.

### Passos de reprodução

1. Configurar APP_ENV=test e AUTH_MOCK=true com uma base local existente.
2. Iniciar o servidor usando um arquivo de ambiente de nome arbitrário.
3. Observar bloqueio de configuração antes do login por arquivo/diretório/banco.
4. Mesmo no banco marcado, um usuário ativo fora das três contas é rejeitado.

### Evidências sanitizadas

- [Validação atual](../../../../app/config.py): validate_mock_environment.
- [Adaptador atual](../../../../app/services/test_auth_service.py): contas fixas,
  senha fixa e conexão SQLite derivada do diretório marcado.
- [Autenticação local](../../../../app/services/auth_service.py) e
  [dependências](../../../../app/dependencies.py) ainda resolvem identidade por Tupã.
- Solicitação explícita: dispensar .env.test explícito e banco especial, verificando
  somente usuário existente na base quando o modo de testes estiver ativo.

### Workaround

O setup sintético permite testar as três contas pré-definidas, mas não satisfaz
o uso solicitado com os usuários da base de desenvolvimento.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | confirmado por leitura do fluxo e relato do usuário |
| Classificação | Ajuste do contrato funcional do AUTH_MOCK após esclarecimento do usuário |
| Domínio afetado | Configuração, autenticação, sessões, identidade HTTP/WebSocket e ferramentas de teste |
| Regras de negócio afetadas | Vínculo por grupo, identidade local e preservação das identidades Tupã |
| Risco de segurança | Sim — bypass de senha intencional em test; manter bloqueio em production/development e recusa de tokens mock no caminho real |
| Risco de LGPD | Sim — usar apenas dados sintéticos nas evidências; não ler/expor base ou credenciais do usuário |
| Risco de isolamento por grupo | Sim — selecionar usuário local não dispensa autorização por grupo em consulta/mutação |
| Risco offline/sincronização | Sim — cookies, renovação e logout devem continuar funcionando com a fila existente |
| Risco ao histórico financeiro | Baixo — sem alteração das compras; garantir que login não crie nem modifique registros financeiros |
| Risco à recorrência | Baixo — regras e dados de recorrência não mudam |
| Risco à separação template/execução | Baixo — sem propagação ou mudança de domínio |
| Dependências | BL-0026, serviços de autenticação, middleware e suítes BL-0011 |
| Duplicidades | Complementa e altera o contrato implementado da BL-0026; preservar seu histórico |
| Responsável pela próxima etapa | Engenharia Jaci |
| Próximo passo | Registrar publicação e aceite da 1.4.0; integração executável autorizada e realizada na develop |

## Acompanhamento até produção

- Documento refinado: [BL-0028](../../tasks/BL-0028-auth-mock-bypass-local.md).
- Branch: feature/BL-0028-auth-mock-bypass-local, criada da develop.
- Implementação: 2/2 fatias entregues na feature/BL-0028-auth-mock-bypass-local; commits 10931df e 98c788d; PR de revisão https://github.com/vguerrax/jaci/pull/45. Bypass por usuário ativo na conexão ORM configurada, senha ignorada, sem alterar identidade Tupã.
- Validações: 307 passes/2 xfail FL-08, cobertura 60,02%, dez Chromium aprovados; smoke PostgreSQL 17 com development.env, login sem senha, isolamento, reinício, logout e identidade preservada. CI 40952438864 aprovado nos jobs Python/Chromium em 98c788d.
- Publicação: pendente; alvo 1.4.0.
- Itens relacionados: BL-0026 e BL-0011.

### Impedimentos

- Publicação e aceite da 1.4.0 pendentes; integração na develop realizada em e7bf602.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-10-29` | Usuário/Codex | Criado em recebido, a_triar e a_definir | Usuário esclareceu o comportamento desejado do AUTH_MOCK |
| `2026-10-29` | Codex | recebido → em_triagem → pronto_para_refinamento; N/A/P1 | Divergência de contrato confirmada, riscos e dependências delimitados |
| `2026-10-29` | Codex | em_refinamento → pronto_para_implementacao | Refinamento documental concluído; aprovação pós-versionamento pendente |
| `2026-10-29` | Usuário/Codex | Refinamento 1ef2a8f aprovado; em_implementacao | Correção e testes Python/UI autorizados; merge documental 2543931, sem autorização de merge executável |
| `2026-10-29` | Codex | em_implementacao → em_validacao; 2/2 fatias | 307 passes/2 xfail, cobertura 60,02%, dez UI e PostgreSQL 17 aprovados; merge executável/publicação pendentes |
| `2026-10-29` | Codex | CI remoto aprovado | PR 45; candidato 98c788d e run 40952438864 com Python/Chromium success; integração executável aguarda autorização |
| `2026-10-29` | Usuário/Codex | Integração executável autorizada e realizada na develop | Merge e7bf602 da feature/BL-0028-auth-mock-bypass-local; commit do usuário 00a7bc9 preservado; sem alteração do ambiente ou deploy |
