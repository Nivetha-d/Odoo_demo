$(document).ready(function() {
    $('#search_button').click(function() {
        var origin = $('#origin').val();
        var destination = $('#destination').val();
        var cabin = $('#cabin').val();

        // Make API request
        $.ajax({
            type: 'POST',
            url: '/your_api_endpoint_url_here',  // Replace with your actual API endpoint URL
            contentType: 'application/json',
            data: JSON.stringify({
                origin: origin,
                destination: destination,
                cabinSelection: [cabin],
                // Add other parameters as needed
            }),
            success: function(response) {
                // Handle API response
                console.log(response);  // Log response to console (for debugging)
                // Update UI or render results as needed
            },
            error: function(xhr, status, error) {
                // Handle errors
                console.error('Error:', error);
            }
        });
    });
});
