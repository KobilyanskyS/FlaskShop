function isReady(e) {
    order_id = $(e).data('order-id')
    $.ajax({
        type: "POST",
        url: "/_switch_order_status_to_ready",
        data: {'order_id': order_id },
        success: function(response) {
            status_span = $('<span>', {class: 'text-warning fw-bold', text: 'Заказ готов' })
            action = $('<button>', {class: 'btn btn-danger', text: 'Выдать заказ', 'data-order-id': order_id, 'onclick': 'isIssued(this)'})
            $(`#status_${order_id}`).html(status_span);
            $(`#actions_${order_id}`).html(action);
        }
    })
}