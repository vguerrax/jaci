# Fundação PWA e Offline

## Objetivo

O Jaci pode ser instalado em dispositivos móveis e oferece acesso parcial aos
dados recentemente utilizados quando a conexão não está disponível.

## Instalação

O manifesto define:

* nome completo `Jaci - Compras Colaborativas` e nome curto `Jaci`;
* abertura em modo `standalone`;
* orientação prioritária em retrato;
* cores de tema e fundo;
* ícones Android de 192 e 512 pixels com área segura para máscara;
* atalho para acessar a compra prioritária pela Home.

Android pode apresentar o comando `Instalar aplicativo` quando os critérios do
navegador forem atendidos. No iOS, os metadados e o ícone permitem adicionar o
Jaci à Tela de Início pelo menu de compartilhamento do Safari.

## BL-004 — Estratégia de Cache

O service worker separa quatro tipos de conteúdo:

* app shell pré-cacheado: cache-first;
* recursos estáticos: stale-while-revalidate;
* APIs GET e respostas JSON: network-first;
* páginas visitadas: network-first com retorno à última versão armazenada.

Quando uma página nunca foi visitada e a rede está indisponível, uma tela offline
explica a limitação e permite tentar novamente. Requisições de mutação não são
interceptadas nem tratadas como persistidas.

Os caches são versionados com nomes `jaci-*-vN`. Durante a ativação, qualquer
cache do Jaci que não faça parte da versão atual é removido. Isso evita servir
assets antigos após uma publicação.

### Critérios de Aceitação do BL-004

* O service worker é registrado a partir do app shell.
* O app shell é pré-cacheado e usa cache-first.
* Recursos estáticos continuam disponíveis offline e são atualizados em segundo
  plano.
* APIs GET usam a rede como fonte preferencial e só retornam cache quando a rede
  falha.
* Caches antigos são invalidados na ativação de uma nova versão.

## Estado de Sincronização

## BL-026 — Indicador de Sincronização

O indicador global fica visível em todas as telas e informa:

* sincronizado;
* sincronizando;
* offline;
* erro de sincronização;
* quantidade de alterações pendentes registrada localmente.

As transições acontecem automaticamente:

* eventos `online` e `offline` do navegador atualizam conectividade;
* requisições HTMX colocam o estado em `sincronizando` e retornam para
  `sincronizado` quando concluídas;
* erros de HTMX colocam o estado em `erro de sincronização`;
* o cache local IndexedDB dispara eventos `jaci:sync-start`,
  `jaci:sync-success` e `jaci:sync-error` ao atualizar o snapshot offline.

A fila persistente de mutações, sincronização assíncrona e resolução de conflitos
continuam como evoluções futuras. A fundação atual não deve comunicar que uma
alteração offline foi salva sem que exista confirmação local.

## Feedback de Carregamento

O app shell inclui um indicador global de carregamento para reduzir cliques
repetidos no PWA instalado. Ele aparece em:

* navegação interna por links;
* envio de formulários tradicionais;
* requisições HTMX.

O indicador não é exibido para links externos, downloads, âncoras locais,
abertura em nova aba ou controles Bootstrap como dropdowns e modais. Enquanto
visível, ele cobre a tela e bloqueia novos toques até a resposta da navegação ou
requisição.

## BL-005 a BL-009 — Cache Local e Início Offline

O Jaci mantém um cache local em IndexedDB para consulta offline dos dados
essenciais:

* grupos;
* categorias;
* templates e seus itens;
* execuções recentes e seus itens.

Quando o usuário está online e autenticado, o app shell busca
`/api/offline/snapshot` e substitui os dados armazenados localmente. O snapshot é
sempre escopado aos grupos do usuário autenticado e nunca deve incluir dados de
grupos externos.

Quando o navegador entra em modo offline, a interface exibe um painel discreto
com a quantidade de dados disponíveis localmente e a data da última atualização.
Esse painel é uma indicação de consulta local, não uma confirmação de
sincronização remota.

Execuções agendadas podem ser iniciadas offline. O cliente persiste uma operação
`start_execution` na store `pending_operations`, atualiza a execução local para
`in_progress` e incrementa o indicador global de alterações pendentes. Quando a
conexão volta, a operação é enviada para
`/api/offline/operations/start-execution`; em caso de sucesso, a fila local é
limpa e o snapshot offline é atualizado.

### Fora do Escopo

O cache local não implementa:

* alterações offline de itens;
* resolução de conflitos;
* sobrescrita automática de dados remotos.

Demais operações de escrita continuam dependendo da API remota ou de evoluções
futuras da fila offline.

## Validação Manual

Validar em ambiente HTTPS:

1. Abrir a aplicação e confirmar a oferta de instalação no Android.
2. Adicionar à Tela de Início pelo Safari no iOS.
3. Abrir o aplicativo instalado e confirmar o modo standalone.
4. Visitar Home e uma compra, desativar a rede e reabrir ambas.
5. Confirmar que uma rota nunca visitada apresenta a tela offline.
6. Executar Lighthouse e verificar tempo de carregamento inferior a 2 segundos
   no perfil móvel acordado para o ambiente.
