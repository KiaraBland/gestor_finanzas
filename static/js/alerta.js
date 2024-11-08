document.addEventListener("DOMContentLoaded", function() {
    // Verifica si hay mensajes flash para mostrar
    if (typeof flashMessages !== 'undefined' && flashMessages.length > 0) {
        flashMessages.forEach(function(flashMessage) {
            Swal.fire({
                icon: flashMessage.category === "success" ? "success" : "error",
                title: flashMessage.category === "success" ? "Éxito" : "Error",
                text: flashMessage.message,
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Aceptar"
            });
        });
    }
});
