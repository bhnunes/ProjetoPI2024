// Função para enviar o formulário encerrar ticket com AJAX
function EncerrarTicket() {
    $('form').submit(function(event) {
        event.preventDefault(); 
        var formData = $(this).serialize(); 
        $.ajax({
            type: "POST",
            url: "/encerrarTicket",
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


// Chamar as funções quando o documento estiver pronto
$(document).ready(function() {
    EncerrarTicket();
});