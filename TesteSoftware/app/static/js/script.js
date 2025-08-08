// Função para inicializar tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // Confirmação para ações importantes
    document.querySelectorAll('.confirm-action').forEach(item => {
        item.addEventListener('click', event => {
            if (!confirm('Tem certeza que deseja realizar esta ação?')) {
                event.preventDefault()
            }
        })
    })
})