document.addEventListener('DOMContentLoaded', function () {
    console.log('Projeto Flask com PostgreSQL carregado!');
    // Adicione seu JavaScript interativo aqui, se necessário.
    // Ex: validações de formulário, interações dinâmicas.
});

// Função para formatar o input com zeros à esquerda ao perder o foco (onblur)
function formatInput(inputElement, desiredLength) {
    let value = inputElement.value.replace(/\D/g, ''); // Remove qualquer caractere que não seja dígito

    // Se o valor for menor que o comprimento desejado, preenche com zeros à esquerda
    if (value.length < desiredLength) {
        value = value.padStart(desiredLength, '0');
    }
    // Se o valor for maior que o comprimento desejado, trunca
    else if (value.length > desiredLength) {
        value = value.substring(0, desiredLength);
    }
    inputElement.value = value;
}

// Função para formatar os campos ANTES de submeter o formulário
function formatBeforeSubmit() {
    const agenciaInput = document.getElementById('agencia');
    const numeroContaInput = document.getElementById('numero_conta');

    if (agenciaInput) {
        formatInput(agenciaInput, 4);
    }
    if (numeroContaInput) {
        formatInput(numeroContaInput, 20);
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
            formatInput(agenciaInput, 4);
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
        // Formata ao carregar se já houver um valor
        if (numeroContaInput.value) {
            formatInput(numeroContaInput, 20);
        }
        // Adiciona um listener para limitar a 20 caracteres e remover não-dígitos enquanto digita
        numeroContaInput.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 20) {
                value = value.substring(0, 20);
            }
            this.value = value;
        });
    }
});