# BL-0011 — Ampliar cobertura automatizada e testes de UI

## Identificação e entrada

| Campo | Valor |
| --- | --- |
| ID | `BL-0011` |
| Título | Ampliar cobertura automatizada e testes de UI |
| Tipo | `melhoria` |
| Estado | `recebido` |
| Severidade | `a_triar` |
| Prioridade | `a_definir` |
| Data de entrada | `2026-07-24` |
| Origem | Solicitação do usuário |
| Ambiente/versão | Estado de `develop` (`e062249`) em `2026-07-24` |
| Responsável | `a_definir` |
| Atualizado em | `2026-07-24` |

### Comportamento observado

A suíte automatizada possui 177 testes coletados pelo Pytest e rastreia regras
de negócio e fluxos do usuário, mas não há medição de cobertura configurada,
suíte de testes executada em navegador real nem automação de CI versionada para
aplicar continuamente testes de UI.

### Comportamento esperado

A qualidade automatizada deve ter cobertura mensurável e evolutiva, validar em
navegador os fluxos críticos da interface com prioridade mobile-first e aplicar
esses testes automaticamente de forma confiável e reproduzível.

### Impacto e abrangência

- Impacto: lacunas de cobertura e regressões de interface podem permanecer sem
  detecção objetiva antes da publicação.
- Abrangência: suíte de testes, fluxos críticos da interface, documentação de
  rastreabilidade e automação de validação.
- Frequência: em toda alteração que afete comportamento, integração ou
  experiência do usuário.

### Passos de reprodução

1. Coletar a suíte atual com `venv/bin/pytest --collect-only -q`.
2. Inspecionar a configuração do Pytest e observar que não há medição de
   cobertura.
3. Procurar uma suíte de navegador e sua execução automatizada no repositório.
4. Observar que esses recursos ainda não estão versionados.

### Evidências sanitizadas

- [Rastreabilidade dos testes](../../../../tests/README.md).
- [Configuração do Pytest](../../../../pytest.ini).
- [Dependências de desenvolvimento](../../../../requirements-dev.txt).

### Workaround

Executar manualmente `venv/bin/pytest` e validar os fluxos críticos diretamente
no navegador antes de cada publicação.

## Triagem

| Campo | Valor |
| --- | --- |
| Confirmação | `a_triar` |
| Classificação | `a_triar` |
| Domínio afetado | `a_triar` |
| Regras de negócio afetadas | `a_triar` |
| Risco de segurança | `a_avaliar` |
| Risco de LGPD | `a_avaliar` |
| Risco de isolamento por grupo | `a_avaliar` |
| Risco offline/sincronização | `a_avaliar` |
| Risco ao histórico financeiro | `a_avaliar` |
| Risco à recorrência | `a_avaliar` |
| Risco à separação template/execução | `a_avaliar` |
| Dependências | Ambiente de navegador e automação de execução; detalhamento `a_triar` |
| Duplicidades | Sobreposição parcial com a cobertura offline do [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md); demais lacunas `a_triar` |
| Responsável pela próxima etapa | `a_definir` |
| Próximo passo | Inventariar lacunas, definir métricas, priorizar fluxos críticos e delimitar a automação durante a triagem |

## Acompanhamento até produção

- Documento refinado: ainda não criado.
- Implementação (commits/PRs): ainda não iniciada.
- Validações: somente diagnóstico documental; cobertura e testes de UI ainda
  não implementados.
- Publicação: ainda não publicada.
- Itens relacionados: [BL-0001](BL-0001-operacao-offline-cobertura-rastreabilidade.md).

### Impedimentos

- Nenhum registrado; metas, ferramentas e fluxos prioritários dependem da
  triagem.

## Histórico

| Data/hora | Autor | Mudança | Motivo/evidência |
| --- | --- | --- | --- |
| `2026-07-24 01:11 -03` | Codex | Item criado em `recebido` | Solicitação do usuário |
