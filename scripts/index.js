$(document).ready(function() {
    $('.input-container input').keypress(function(e) {
        if (e.which == 13) {
            sendMessage();
        }
    });

    function sendMessage() {
        var message = $('.input-container input').val();
        if (message.trim() === '') return;

        $.ajax({
            url: '/chat',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: message }),
            success: function(response) {
                $('.notification').append('<p><strong>You:</strong> ' + response + '</p>');
                console.log(response);  
                $('.input-container input').val('');
                $('.notification').scrollTop($('.notification')[0].scrollHeight);
            }
        });
    }
});

   