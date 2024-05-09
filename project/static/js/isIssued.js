function isIssued(e) {
    order_id = $(e).data('order-id')
    $.ajax({
        type: "POST",
        url: "/_switch_order_status_to_issued",
        data: {'order_id': order_id },
        success: function(response) {
            status_span = $('<span>', {class: 'fw-bold', text: 'Заказ выдан' })
            $(`#status_${order_id}`).html(status_span);
            $(`#actions_${order_id}`).html('');
        }
    })
}