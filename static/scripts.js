// script.js
function handleLogin(event) {
    event.preventDefault(); // Prevent the default form submission
    // var username = document.getElementById('username').value;
    // var password = document.getElementById('password').value;

    // Send an AJAX request to the Flask route
    $.ajax({
        type: "POST",
        url: '/login', // The Flask route
        data: {
            //username: username,
            //password: password
        },
        success: function(response) {
            // Manually redirect to the dashboard page
            window.location.href = "/dashboard";
        },
        error: function(error) {
            // Handle any errors
            console.log(error);
        }
    });
    
}
