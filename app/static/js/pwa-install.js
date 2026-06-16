(function () {
    'use strict';

    let installPrompt = null;
    const installButtons = document.querySelectorAll('[data-pwa-install]');

    function setInstallAvailable(available) {
        installButtons.forEach(function (button) {
            button.hidden = !available;
        });
    }

    window.addEventListener('beforeinstallprompt', function (event) {
        event.preventDefault();
        installPrompt = event;
        setInstallAvailable(true);
    });

    installButtons.forEach(function (button) {
        button.addEventListener('click', async function () {
            if (!installPrompt) return;
            installPrompt.prompt();
            await installPrompt.userChoice;
            installPrompt = null;
            setInstallAvailable(false);
        });
    });

    window.addEventListener('appinstalled', function () {
        installPrompt = null;
        setInstallAvailable(false);
    });

    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
            navigator.serviceWorker.register('/service-worker.js', { scope: '/' }).catch(function () {
                // A aplicação continua funcional online quando o registro não é suportado.
            });
        });
    }
})();
