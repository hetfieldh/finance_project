// static/js/script.js

/**
 * Função utilitária para obter a data de hoje formatada (YYYY-MM-DD).
 * @returns {string} A data atual formatada.
 */
function getTodayDate() {
    const today = new Date();
    const year = today.getFullYear();
    let month = today.getMonth() + 1;
    let day = today.getDate();

    // Adiciona zero à esquerda se for menor que 10
    if (day < 10) day = '0' + day;
    if (month < 10) month = '0' + month;

    return `${year}-${month}-${day}`;
}

/**
 * Inicializa a funcionalidade do menu dropdown.
 */
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const dropbtn = dropdown.querySelector('.dropbtn');
        if (dropbtn) {
            dropbtn.addEventListener('click', function () {
                this.nextElementSibling.classList.toggle('show');
            });
        }
    });

    // Fecha o dropdown se o usuário clicar fora
    window.addEventListener('click', function (event) {
        if (!event.target.matches('.dropbtn')) {
            const openDropdowns = document.querySelectorAll('.dropdown-content.show');
            openDropdowns.forEach(openDropdown => {
                openDropdown.classList.remove('show');
            });
        }
    });
}

/**
 * Inicializa a lógica para formulários de Crediário (Adicionar e Editar).
 * @param {string} formId O ID do formulário do crediário.
 */
function initializeCrediarioForm(formId) {
    const crediarioForm = document.getElementById(formId);
    if (!crediarioForm) return;

    const finalInput = crediarioForm.querySelector('#final');
    const modal = document.getElementById('addTipoModal');
    const openModalBtn = crediarioForm.querySelector('#openAddTipoModal');
    const closeButton = modal ? modal.querySelector('.close-button') : null;
    const cancelAddTipoBtn = modal ? modal.querySelector('#cancelAddTipo') : null;
    const addTipoForm = modal ? modal.querySelector('#addTipoForm') : null;
    const tipoSelect = crediarioForm.querySelector('#tipo');
    const modalMessages = modal ? modal.querySelector('#modal-messages') : null;

    // Lógica para o campo 'final'
    if (finalInput) {
        crediarioForm.addEventListener('submit', function () {
            let finalValue = finalInput.value;
            finalInput.value = finalValue.padStart(4, '0');
        });

        finalInput.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 4);
        });
    }

    // Lógica do Modal de Adição de Tipo de Crediário
    if (modal && openModalBtn && closeButton && cancelAddTipoBtn && addTipoForm && tipoSelect && modalMessages) {
        openModalBtn.addEventListener('click', function () {
            modal.style.display = 'block';
            modalMessages.innerHTML = '';
            const modalNomeTipo = modal.querySelector('#modal_nome_tipo');
            if (modalNomeTipo) modalNomeTipo.value = '';
        });

        closeButton.addEventListener('click', function () {
            modal.style.display = 'none';
        });

        cancelAddTipoBtn.addEventListener('click', function () {
            modal.style.display = 'none';
        });

        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });

        addTipoForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const formData = new FormData(addTipoForm);
            const nomeTipo = formData.get('nome_tipo');

            fetch(addTipoForm.action, {
                method: 'POST',
                body: formData
            })
                .then(response => response.text())
                .then(html => {
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    const newFlashes = tempDiv.querySelector('.flashes');

                    if (modalMessages) {
                        modalMessages.innerHTML = '';
                        if (newFlashes) {
                            modalMessages.innerHTML = newFlashes.innerHTML;
                        }
                    }

                    if (html.includes('success')) {
                        console.log('Tipo de crediário adicionado com sucesso via AJAX.');
                        // Rebusca a lista completa de tipos de crediário
                        fetch('/tipos_crediario/') // Assumindo que esta rota retorna uma lista HTML com os tipos
                            .then(response => response.text())
                            .then(listHtml => {
                                const parser = new DOMParser();
                                const doc = parser.parseFromString(listHtml, 'text/html');
                                const newTiposRows = doc.querySelectorAll('table tbody tr'); // Supondo que a tabela tenha tbody tr

                                // Limpa todas as opções existentes no select, exceto a primeira ("Selecione um Tipo")
                                while (tipoSelect.options.length > 1) {
                                    tipoSelect.remove(1);
                                }

                                // Adiciona as novas opções ao select
                                newTiposRows.forEach(row => {
                                    const nome = row.querySelector('td:nth-child(2)') ? row.querySelector('td:nth-child(2)').textContent.trim() : '';
                                    if (nome) {
                                        const option = document.createElement('option');
                                        option.value = nome;
                                        option.textContent = nome;
                                        tipoSelect.appendChild(option);
                                    }
                                });

                                tipoSelect.value = nomeTipo; // Seleciona o recém-adicionado
                                modal.style.display = 'none'; // Fecha o modal
                                setTimeout(() => { if (modalMessages) modalMessages.innerHTML = ''; }, 3000);
                            })
                            .catch(error => {
                                console.error('Erro ao recarregar tipos de crediário:', error);
                                if (modalMessages) modalMessages.innerHTML = '<li class="danger">Erro ao recarregar tipos de crediário.</li>';
                            });
                    }
                })
                .catch(error => {
                    console.error('Erro ao enviar formulário do modal:', error);
                    if (modalMessages) modalMessages.innerHTML = '<li class="danger">Ocorreu um erro ao adicionar o tipo.</li>';
                });
        });
    }
}

/**
 * Lógica do Modal de Senha para Confirmação de Exclusão (usado em Extrato Bancário).
 */
function initializePasswordModal() {
    let currentDeleteForm = null; // Variável para armazenar o formulário que acionou o modal

    const passwordModal = document.getElementById('passwordModal');
    if (!passwordModal) return;

    const confirmDeleteButton = document.getElementById('confirmDeleteButton');
    const cancelDeleteButton = document.getElementById('cancelDeleteButton');
    const modalPasswordInput = document.getElementById('modalPasswordInput');

    confirmDeleteButton.addEventListener('click', function () {
        const password = modalPasswordInput.value;
        if (password && currentDeleteForm) {
            const passwordInput = document.createElement('input');
            passwordInput.type = 'hidden';
            passwordInput.name = 'password';
            passwordInput.value = password;
            currentDeleteForm.appendChild(passwordInput);

            passwordModal.style.display = 'none';
            currentDeleteForm.submit();
        } else {
            console.error("Por favor, digite sua senha para confirmar a exclusão.");
        }
    });

    cancelDeleteButton.addEventListener('click', function () {
        passwordModal.style.display = 'none';
        currentDeleteForm = null;
    });

    window.addEventListener('click', function (event) {
        if (event.target === passwordModal) {
            passwordModal.style.display = 'none';
            currentDeleteForm = null;
        }
    });

    // Torna a função showPasswordModal global para ser chamada pelo 'onsubmit' no HTML
    window.showPasswordModal = function (form) {
        currentDeleteForm = form;
        passwordModal.style.display = 'block';
        modalPasswordInput.value = '';
        modalPasswordInput.focus();
        return false; // Previne a submissão padrão do formulário
    };
}

/**
 * Inicializa a lógica para o Formulário de Lançamento Bancário.
 * @param {object} accountsData Dados das contas, passados do Jinja2 para o JS.
 */
function initializeLancamentoForm(accountsData) {
    const lancamentoForm = document.querySelector('form[action*="/movimento/lancamento"]');
    if (!lancamentoForm) return;

    const dateInput = document.getElementById('data');
    const valorInput = document.getElementById('valor');
    const descricaoSelect = document.getElementById('descricao');
    const transacoesOptions = Array.from(descricaoSelect.options).slice(1);

    const isTransferCheckbox = document.getElementById('is_transfer');
    const targetAccountGroup = document.getElementById('target_account_group');
    const contaDestinoSelect = document.getElementById('conta_destino_id');
    const contaOrigemSelect = document.getElementById('conta_id');

    if (dateInput) {
        dateInput.value = getTodayDate();
    }

    valorInput.addEventListener('input', function () {
        const valor = parseFloat(this.value.replace(',', '.'));

        if (isNaN(valor) || valor === 0) {
            transacoesOptions.forEach(option => option.style.display = '');
            descricaoSelect.value = '';
            descricaoSelect.required = true;
            return;
        }

        const tipoDesejado = valor > 0 ? 'Entrada' : 'Saída';

        transacoesOptions.forEach(option => {
            const tipoTransacao = option.dataset.tipo;
            if (tipoTransacao === tipoDesejado) {
                option.style.display = '';
            } else {
                option.style.display = 'none';
            }
        });

        if (descricaoSelect.selectedOptions[0] && descricaoSelect.selectedOptions[0].style.display === 'none') {
            descricaoSelect.value = '';
        }
        descricaoSelect.required = true;
    });

    isTransferCheckbox.addEventListener('change', function () {
        if (this.checked) {
            targetAccountGroup.style.display = 'block';
            contaDestinoSelect.required = true;
            descricaoSelect.required = false;
            descricaoSelect.value = '';

            valorInput.value = Math.abs(parseFloat(valorInput.value.replace(',', '.')) || 0);

            const transferOption = transacoesOptions.find(opt =>
                opt.value.toLowerCase().includes('transferencia') || opt.value.toLowerCase().includes('transferência')
            );
            if (transferOption) {
                descricaoSelect.value = transferOption.value;
            } else {
                console.warn("Tipo de transação 'Transferência' não encontrado. Por favor, cadastre um.");
            }

        } else {
            targetAccountGroup.style.display = 'none';
            contaDestinoSelect.required = false;
            contaDestinoSelect.value = '';
            descricaoSelect.required = true;
        }
        filterTargetAccounts();
    });

    contaOrigemSelect.addEventListener('change', filterTargetAccounts);

    function filterTargetAccounts() {
        const selectedOriginAccountId = contaOrigemSelect.value;
        while (contaDestinoSelect.options.length > 1) {
            contaDestinoSelect.remove(1);
        }

        if (isTransferCheckbox.checked && selectedOriginAccountId) {
            // Usa accountsData passado como argumento
            accountsData.forEach(conta => {
                if (String(conta.id) !== String(selectedOriginAccountId)) {
                    const option = document.createElement('option');
                    option.value = conta.id;
                    option.textContent = `${conta.nome_banco} - ${conta.tipo_conta} (Saldo: R$ ${conta.saldo_atual.toFixed(2)})`;
                    contaDestinoSelect.appendChild(option);
                }
            });
        }
    }

    if (valorInput.value) {
        valorInput.dispatchEvent(new Event('input'));
    }

    if (isTransferCheckbox.checked) {
        filterTargetAccounts();
    }
}

// --- Ponto de Entrada Principal (Executado quando o DOM estiver carregado) ---
document.addEventListener('DOMContentLoaded', function () {
    initializeDropdowns();
    initializeCrediarioForm('crediarioForm');
    initializeCrediarioForm('crediarioEditForm');
    initializePasswordModal();

    // Para o formulário de lançamento, é preciso passar os dados das contas.
    // Isso ainda requer que o Flask renderize esses dados no HTML de forma que o JS possa pegá-los.
    // Exemplo: <script id="accounts-data" type="application/json">{{ contas | tojson | safe }}</script>
    // E então no JS:
    const accountsDataElement = document.getElementById('accounts-data');
    let accountsData = [];
    if (accountsDataElement) {
        try {
            accountsData = JSON.parse(accountsDataElement.textContent);
        } catch (e) {
            console.error('Erro ao parsear dados das contas:', e);
        }
    }
    initializeLancamentoForm(accountsData);
});