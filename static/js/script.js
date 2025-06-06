// static/js/script.js

// Garante que o script só rode depois que o DOM estiver completamente carregado
document.addEventListener('DOMContentLoaded', function() {
    // Lógica para o menu dropdown (manter aqui se já existia)
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.querySelector('.dropbtn').addEventListener('click', function() {
            this.nextElementSibling.classList.toggle('show');
        });
    });

    // Fechar o dropdown se o usuário clicar fora (manter aqui se já existia)
    window.addEventListener('click', function(event) {
        if (!event.target.matches('.dropbtn')) {
            const dropdowns = document.querySelectorAll('.dropdown-content');
            dropdowns.forEach(openDropdown => {
                if (openDropdown.classList.contains('show')) {
                    openDropdown.classList.remove('show');
                }
            });
        }
    });

    // --- Lógica comum para formulários de Crediário (Add e Edit) ---
    // (Manter a função initializeCrediarioForm aqui como foi feito anteriormente)
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

        crediarioForm.addEventListener('submit', function (event) {
            if (finalInput) {
                let finalValue = finalInput.value;
                finalInput.value = finalValue.padStart(4, '0');
            }
        });

        if (finalInput) {
            finalInput.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').slice(0, 4);
            });
        }

        if (modal && openModalBtn && closeButton && cancelAddTipoBtn && addTipoForm && tipoSelect && modalMessages) {
            openModalBtn.onclick = function () {
                modal.style.display = 'block';
                modalMessages.innerHTML = '';
                const modalNomeTipo = modal.querySelector('#modal_nome_tipo');
                if (modalNomeTipo) modalNomeTipo.value = '';
            };

            closeButton.onclick = function () {
                modal.style.display = 'none';
            };

            cancelAddTipoBtn.onclick = function () {
                modal.style.display = 'none';
            };

            window.onclick = function (event) {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            };

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
                        fetch('/tipos_crediario/')
                            .then(response => response.text())
                            .then(listHtml => {
                                const parser = new DOMParser();
                                const doc = parser.parseFromString(listHtml, 'text/html');
                                const newTipos = doc.querySelectorAll('table tbody tr');

                                while (tipoSelect.options.length > 1) {
                                    tipoSelect.remove(1);
                                }

                                newTipos.forEach(row => {
                                    const nome = row.querySelector('td:nth-child(2)') ? row.querySelector('td:nth-child(2)').textContent.trim() : '';
                                    if (nome) {
                                        const option = document.createElement('option');
                                        option.value = nome;
                                        option.textContent = nome;
                                        tipoSelect.appendChild(option);
                                    }
                                });

                                tipoSelect.value = nomeTipo;
                                modal.style.display = 'none';
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

    // Inicializa a lógica para o formulário de Adição de Crediário (se presente na página)
    initializeCrediarioForm('crediarioForm');

    // Inicializa a lógica para o formulário de Edição de Crediário (se presente na página)
    initializeCrediarioForm('crediarioEditForm');


    // --- Lógica do Modal de Senha para Confirmação de Exclusão (Extrato Bancário) ---
    let currentDeleteForm = null;

    const passwordModal = document.getElementById('passwordModal');
    if (passwordModal) {
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
    }

    // A função showPasswordModal precisa ser global para ser chamada pelo 'onsubmit'
    window.showPasswordModal = function(form) {
        currentDeleteForm = form;
        document.getElementById('passwordModal').style.display = 'block';
        document.getElementById('modalPasswordInput').value = '';
        document.getElementById('modalPasswordInput').focus();
        return false;
    };


    // --- Lógica para o Formulário de Lançamento Bancário (movimento/lancamento.html) ---
    function initializeLancamentoForm() {
        const lancamentoForm = document.querySelector('form[action*="/movimento/lancamento"]');
        if (!lancamentoForm) return; // Só executa se estiver na página de lançamento

        const dateInput = document.getElementById('data');
        const valorInput = document.getElementById('valor');
        const descricaoSelect = document.getElementById('descricao');
        // Pega as opções de transação, excluindo a primeira ("Selecione a Transação")
        const transacoesOptions = Array.from(descricaoSelect.options).slice(1);

        const isTransferCheckbox = document.getElementById('is_transfer');
        const targetAccountGroup = document.getElementById('target_account_group');
        const contaDestinoSelect = document.getElementById('conta_destino_id');
        const contaOrigemSelect = document.getElementById('conta_id');

        // Função para obter a data de hoje formatada
        function getTodayDate() {
            const today = new Date();
            const year = today.getFullYear();
            let month = today.getMonth() + 1;
            let day = today.getDate();
            if (day < 10) day = '0' + day;
            if (month < 10) month = '0' + month;
            return year + '-' + month + '-' + day;
        }

        // Define a data atual no campo de data
        if (dateInput) {
            dateInput.value = getTodayDate();
        }

        // Event listener para filtrar tipos de transação baseados no valor
        valorInput.addEventListener('input', function () {
            // Converte para número, tratando vírgula como ponto
            const valor = parseFloat(this.value.replace(',', '.'));

            if (isNaN(valor) || valor === 0) {
                // Se o valor não é um número ou é zero, mostra todas as opções
                transacoesOptions.forEach(option => option.style.display = '');
                descricaoSelect.value = ''; // Limpa a seleção
                descricaoSelect.required = true;
                return;
            }

            const tipoDesejado = valor > 0 ? 'Entrada' : 'Saída';

            // Filtra as opções visíveis
            transacoesOptions.forEach(option => {
                const tipoTransacao = option.dataset.tipo; // Pega o tipo de transação do data-attribute
                if (tipoTransacao === tipoDesejado) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });

            // Se a opção atualmente selecionada não é mais visível, reseta
            if (descricaoSelect.selectedOptions[0] && descricaoSelect.selectedOptions[0].style.display === 'none') {
                descricaoSelect.value = '';
            }
            descricaoSelect.required = true;
        });

        // Event listener para o checkbox de transferência
        isTransferCheckbox.addEventListener('change', function () {
            if (this.checked) {
                targetAccountGroup.style.display = 'block';
                contaDestinoSelect.required = true;
                descricaoSelect.required = false; // Transação não é obrigatória para transferência
                descricaoSelect.value = ''; // Limpa a seleção do tipo de transação

                // Garante que o valor da transferência seja positivo
                valorInput.value = Math.abs(parseFloat(valorInput.value.replace(',', '.')) || 0);

                // Tenta pré-selecionar o tipo de transação "Transferência"
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
                contaDestinoSelect.value = ''; // Limpa a seleção da conta destino
                descricaoSelect.required = true; // Transação volta a ser obrigatória
            }
            // Chama a função para filtrar as contas de destino (sempre que a transferência mudar)
            filterTargetAccounts();
        });

        // Event listener para filtrar contas de destino quando a conta de origem muda
        contaOrigemSelect.addEventListener('change', filterTargetAccounts);

        // Função para filtrar as contas de destino para transferência
        function filterTargetAccounts() {
            const selectedOriginAccountId = contaOrigemSelect.value;
            // Limpa todas as opções de destino, exceto a primeira ("Selecione a Conta Destino")
            while (contaDestinoSelect.options.length > 1) {
                contaDestinoSelect.remove(1);
            }

            // Se for transferência e uma conta de origem estiver selecionada
            if (isTransferCheckbox.checked && selectedOriginAccountId) {
                // Recupera os dados das contas diretamente do HTML (convertendo de JSON)
                // É fundamental que 'contas' seja passado corretamente para o template como JSON
                const allAccountsData = JSON.parse('{{ contas | tojson | safe }}');

                allAccountsData.forEach(conta => {
                    // Adiciona apenas as contas que não são a conta de origem
                    if (String(conta.id) !== String(selectedOriginAccountId)) {
                        const option = document.createElement('option');
                        option.value = conta.id;
                        option.textContent = `${conta.nome_banco} - ${conta.tipo_conta} (Saldo: R$ ${conta.saldo_atual.toFixed(2)})`;
                        contaDestinoSelect.appendChild(option);
                    }
                });
            }
        }

        // Dispara o evento 'input' no campo valor ao carregar a página
        // para aplicar o filtro de tipo de transação se já houver um valor
        if (valorInput.value) {
            valorInput.dispatchEvent(new Event('input'));
        }

        // Dispara o evento 'change' no checkbox de transferência ao carregar a página
        // para exibir/ocultar o campo de conta destino e filtrar
        if (isTransferCheckbox.checked) {
            filterTargetAccounts();
        }
    }

    // Inicializa a lógica para o formulário de Lançamento Bancário (se presente na página)
    initializeLancamentoForm();

});