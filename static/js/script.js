document.addEventListener('DOMContentLoaded', function () {
    console.log('Projeto Flask com PostgreSQL carregado!');
});

function formatInput(inputElement, desiredLength) {
    let value = inputElement.value.replace(/\D/g, '');

    // Se o valor for maior que o comprimento desejado, trunca
    if (value.length > desiredLength) {
        value = value.substring(0, desiredLength);
    }
    // Para 'agencia', ainda podemos preencher com zeros se for menor que 4,
    // mas para 'numero_conta', não faremos isso.
    if (inputElement.id === 'agencia' && value.length < desiredLength) {
        value = value.padStart(desiredLength, '0');
    }
    inputElement.value = value;
}

// Função para formatar os campos ANTES de submeter o formulário
function formatBeforeSubmit() {
    const agenciaInput = document.getElementById('agencia');
    const numeroContaInput = document.getElementById('numero_conta');

    if (agenciaInput) {
        formatInput(agenciaInput, 4); // Agência ainda preenche com zeros
    }
    if (numeroContaInput) {
        // Para numero_conta, apenas remove não-dígitos e trunca, NÃO preenche com zeros
        let value = numeroContaInput.value.replace(/\D/g, '');
        if (value.length > 50) { // Usando 50 como max length, ajuste se necessário
            value = value.substring(0, 50);
        }
        numeroContaInput.value = value;
    }
    return true; // Retorna true para permitir que o formulário seja submetido
}


// Listener para formatar quando a página carrega, útil para campos que já vêm com valores (como na edição)
document.addEventListener('DOMContentLoaded', function () {
    // Para agência
    const agenciaInput = document.getElementById('agencia');
    if (agenciaInput) { // Verifica se o elemento existe na página atual
        // Formata ao carregar se já houver um valor
        if (agenciaInput.value) {
            formatInput(agenciaInput, 4); // Agência ainda preenche com zeros
        }
        // Adiciona um listener para limitar a 4 caracteres e remover não-dígitos enquanto digita
        agenciaInput.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 4) {
                value = value.substring(0, 4);
            }
            this.value = value;
        });
    }

    // Para número da conta
    const numeroContaInput = document.getElementById('numero_conta');
    if (numeroContaInput) { // Verifica se o elemento existe na página atual
        // Formata ao carregar se já houver um valor (APENAS remove não-dígitos e trunca)
        if (numeroContaInput.value) {
            let value = numeroContaInput.value.replace(/\D/g, '');
            if (value.length > 50) { // Usando 50 como max length, ajuste se necessário
                value = value.substring(0, 50);
            }
            numeroContaInput.value = value;
        }
        // Adiciona um listener para limitar a 50 caracteres e remover não-dígitos enquanto digita
        numeroContaInput.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 50) { // Usando 50 como max length, ajuste se necessário
                value = value.substring(0, 50);
            }
            this.value = value;
        });
    }
});
