/**
* Jaci - Execution Sync Client
* Gerencia conexão WebSocket e atualizações em tempo real na tela de compra.
*/
(function () {
    'use strict';

    const ExecutionSync = {
        ws: null,
        executionId: null,
        token: null,
        reconnectTimer: null,
        maxReconnectDelay: 10000, // 10 segundos
        reconnectDelay: 1000,      // começa com 1 segundo
        isConnecting: false,

        /**
         * Inicializa a conexão WebSocket.
         * @param {string} executionId - ID da execução
         * @param {string} token - JWT de sessão
         */
        init: function (executionId, token) {
            if (!executionId || !token) {
                console.error('[Jaci WS] executionId e token são obrigatórios');
                return;
            }
            
            console.log('[Jaci WS] Inicializando para execução', executionId);
            this.executionId = parseInt(executionId);
            this.token = token;
            this.connect();
        },

        /**
         * Conecta ao WebSocket.
         */
        connect: function () {
            if (this.isConnecting || !this.executionId || !this.token) {
                return;
            }

            this.isConnecting = true;

            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const url = `${protocol}//${host}/ws/executions/${this.executionId}?token=${encodeURIComponent(this.token)}`;

            console.log(url);
            console.log(`[Jaci WS] Conectando a ${url}`);

            this.ws = new WebSocket(url);

            this.ws.onopen = () => {
                console.log('[Jaci WS] Conectado');
                this.isConnecting = false;
                this.reconnectDelay = 1000;
                this._sendPing();
            };

            this.ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    this._handleMessage(msg);
                } catch (e) {
                    console.error('[Jaci WS] Erro ao parsear mensagem:', e);
                }
            };

            this.ws.onclose = (event) => {
                console.log(`[Jaci WS] Desconectado (código: ${event.code})`);
                this.isConnecting = false;
                this.ws = null;

                // Reconecta se não foi fechamento intencional
                if (event.code !== 1000 && event.code !== 1001) {
                    this._scheduleReconnect();
                }
            };

            this.ws.onerror = (error) => {
                console.error('[Jaci WS] Erro:', error);
                this.isConnecting = false;
            };
        },

        /**
         * Envia ping periódico para manter a conexão viva.
         */
        _sendPing: function () {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ event: 'ping' }));
            }
            setTimeout(() => this._sendPing(), 30000); // a cada 30s
        },

        /**
         * Agenda reconexão com backoff exponencial.
         */
        _scheduleReconnect: function () {
            if (this.reconnectTimer) {
                clearTimeout(this.reconnectTimer);
            }

            console.log(`[Jaci WS] Reconectando em ${this.reconnectDelay}ms...`);

            this.reconnectTimer = setTimeout(() => {
                this.reconnectDelay = Math.min(
                    this.reconnectDelay * 2,
                    this.maxReconnectDelay
                );
                this.connect();
            }, this.reconnectDelay);
        },

        /**
         * Processa mensagens recebidas do servidor.
         */
        _handleMessage: function (msg) {
            console.log('[Jaci WS] Mensagem recebida:', msg);

            switch (msg.event) {
                case 'pong':
                    // Conexão ativa, nada a fazer
                    break;

                case 'item_completed':
                    // Outro usuário marcou um item como comprado
                    this._onItemCompleted(msg.data);
                    break;

                case 'item_updated':
                    // Outro usuário editou ou desmarcou um item
                    this._onItemUpdated(msg.data);
                    break;

                case 'item_added':
                    // Outro usuário adicionou um item
                    this._onItemAdded(msg.data);
                    break;

                case 'item_removed':
                    // Outro usuário removeu um item
                    this._onItemRemoved(msg.data);
                    break;

                case 'budget_alert':
                    // Alerta de orçamento
                    this._onBudgetAlert(msg.data);
                    break;

                case 'execution_status_changed':
                    // Status da execução mudou
                    this._onStatusChanged(msg.data);
                    break;

                case 'execution_updated':
                    // Dados da execução agendada mudaram
                    this._onExecutionUpdated(msg.data);
                    break;

                case 'version_conflict':
                    // Conflito de versão: recarrega o item
                    this._onVersionConflict(msg.data);
                    break;

                case 'user_active':
                    // Outro usuário está online
                    console.log(`[Jaci WS] Usuário ativo: ${msg.data.email}`);
                    break;

                default:
                    console.log('[Jaci WS] Evento desconhecido:', msg.event);
            }
        },

        /**
         * Recarrega parcial da página usando HTMX.
         * Fallback: recarrega a página inteira.
         */
        _refreshItems: function () {
            if (typeof htmx !== 'undefined') {
                htmx.ajax('GET', `/executions/${this.executionId}/items-fragment`, {
                    target: '#items-container',
                    swap: 'innerHTML',
                });
                htmx.ajax('GET', `/executions/${this.executionId}/sidebar-fragment`, {
                    target: '#sidebar-container',
                    swap: 'innerHTML'
                });
            } else {
                window.location.reload();
            }
        },

        _onItemCompleted: function (data) {
            console.log(`[Jaci WS] Item ${data.item_id} concluído por outro usuário`);
            this._refreshItems();
        },

        _onItemUpdated: function (data) {
            console.log(`[Jaci WS] Item ${data.item_id} atualizado por outro usuário`);
            this._refreshItems();
        },

        _onItemAdded: function (data) {
            console.log(`[Jaci WS] Item "${data.item_name}" adicionado por outro usuário`);
            this._refreshItems();
        },

        _onItemRemoved: function (data) {
            console.log(`[Jaci WS] Item ${data.item_id} removido por outro usuário`);
            this._refreshItems();
        },

        _onBudgetAlert: function (data) {
            this._refreshItems();
        },

        _onStatusChanged: function (data) {
            console.log(`[Jaci WS] Status alterado para: ${data.new_status}`);
            window.location.reload();
        },

        _onExecutionUpdated: function (data) {
            console.log(`[Jaci WS] Execução alterada: ${data.name}`);
            window.location.reload();
        },

        _onVersionConflict: function (data) {
            alert(data.message || 'Este item foi alterado por outro usuário. Recarregando...');
            this._refreshItems();
        },

        /**
         * Lê cookie por nome.
         */
        _getCookie: function (name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) {
                return parts.pop().split(';').shift();
            }
            return null;
        },

        /**
         * Desconecta intencionalmente (sem reconectar).
         */
        disconnect: function () {
            if (this.reconnectTimer) {
                clearTimeout(this.reconnectTimer);
                this.reconnectTimer = null;
            }
            if (this.ws) {
                this.ws.close(1000, 'Navegação');
                this.ws = null;
            }
        },
    };

    // Expõe globalmente
    window.JaciExecutionSync = ExecutionSync;
})();
