$(document).ready(function() {
    $('form').submit(function(event) {
        event.preventDefault(); // Impedir o envio padrão do formulário

        var formData = $(this).serialize(); // Obter os dados do formulário

        $.ajax({
            type: "POST",
            url: "/submeter",
            data: formData,
            dataType: "json",
            success: function(response) {
                // Exibir a mensagem de sucesso
                $("#mensagem-sucesso").text(response.mensagem).show();
                // Ocultar a mensagem após 5 segundos
                setTimeout(function() {
                    $("#mensagem-sucesso").fadeOut();
                }, 2000);

                    // Limpar o formulário
                    $('form')[0].reset();
            }
        });
    });
});
