function manage_cart(e) {
        product_id = $(e).data('product-id')
        btn_val = parseInt($(e).data('btn-val'))
        $.ajax({
                type: "POST",
                url: "/_add_item_to_cart",
                data: {'product_id': product_id,
                       'quantity': btn_val
                    },
                success: function(response) {

                    if (response.quantity == 1){
                        $(`#minus_${product_id}`).prop("disabled", true);
                    } else {
                        $(`#minus_${product_id}`).prop("disabled", false);
                    }

                    $(`#product_${product_id}`).html(response.quantity)
                    $('#total_price').html(response.total_value + " р.")
                    $('#cart_total_price').html(response.total_value + " р.")

                    product_price = Number($(`#product_${product_id}_price`).data('price'));

                    $(`#product_${product_id}_total_price`).html((product_price*response.quantity).toFixed(2) + " р.")
                }
        });
    }