function delete_item_from_cart(e) {
        product_id = $(e).data('product-id')
        $.ajax({
                type: "POST",
                url: "/_delete_item_from_cart",
                data: {'product_id': product_id},
                success: function(response) {
                    $('#total_price').html(response)
                    $('#cart_total_price').html(response)
                    $(`#item_${product_id}`).remove()
                    if (response == 0){
                        $('#create_order').html('')
                    }
                }
        });
    }