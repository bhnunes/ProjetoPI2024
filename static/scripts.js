// Função para atualizar as ruas com base no bairro selecionado
function atualizarRuas() {
    const bairroSelect = document.getElementById('bairro');
    const ruaSelect = document.getElementById('rua');

    bairroSelect.addEventListener('change', () => {
        const bairro = bairroSelect.value;
        fetch(`/buscar_ruas?bairro=${bairro}`)
            .then(response => response.json())
            .then(ruas => {
                ruaSelect.innerHTML = ''; 
                ruas.forEach(rua => {
                    const option = document.createElement('option');
                    option.value = rua;
                    option.text = rua;
                    ruaSelect.appendChild(option);
                });
            });
    });
}

// Função para enviar o formulário com AJAX
function enviarFormulario() {
    $('form').submit(function(event) {
        event.preventDefault(); 
        var formData = $(this).serialize(); 
        $.ajax({
            type: "POST",
            url: "/submeter",
            data: formData,
            dataType: "json",
            success: function(response) {
                $("#mensagem-sucesso").text(response.mensagem).show();
                setTimeout(function() {
                    $("#mensagem-sucesso").fadeOut();
                }, 2000);
                $('form')[0].reset();
            }
        });
    });
}


// Função para definir o valor da cidade
function definirCidade() {
    const cidadeInput = document.getElementById('cidade');
    cidadeInput.value = 'Americana/SP';
}

// Chamar as funções quando o documento estiver pronto
$(document).ready(function() {
    atualizarRuas();
    enviarFormulario();
    definirCidade();
});