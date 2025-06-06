// static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    console.log('Projeto Flask com PostgreSQL carregado!');
});

function formatInput(inputElement, desiredLength) {
    let value = inputElement.value.replace(/\D/g, '');

    if (value.length > desiredLength) {
        value = value.substring(0, desiredLength);
    }
    if (inputElement.id === 'agencia' && value.length < desiredLength) {
        value = value.padStart(desiredLength, '0');
    }
    inputElement.value = value;
}

function formatBeforeSubmit() {
    const agenciaInput = document.getElementById('agencia');
    const numeroContaInput = document.getElementById('numero_conta');

    if (agenciaInput) {
        formatInput(agenciaInput, 4);
    }
    if (numeroContaInput) {
        let value = numeroContaInput.value.replace(/\D/g, '');
        if (value.length > 50) {
            value = value.substring(0, 50);
        }
        numeroContaInput.value = value;
    }
    return true;
}


document.addEventListener('DOMContentLoaded', function () {
    const agenciaInput = document.getElementById('agencia');
    if (agenciaInput) {
        if (agenciaInput.value) {
            formatInput(agenciaInput, 4);
        }
        agenciaInput.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 4) {
                value = value.substring(0, 4);
            }
            this.value = value;
        });
    }

    const numeroContaInput = document.getElementById('numero_conta');
    if (numeroContaInput) {
        if (numeroContaInput.value) {
            let value = numeroContaInput.value.replace(/\D/g, '');
            if (value.length > 50) {
                value = value.substring(0, 50);
            }
            numeroContaInput.value = value;
        }
        numeroContaInput.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 50) {
                value = value.substring(0, 50);
            }
            this.value = value;
        });
    }
});
