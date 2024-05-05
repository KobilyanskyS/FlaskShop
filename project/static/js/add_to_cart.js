function add_to_cart(e) {
        product_id = $(e).data('product-id')
        btn_type = $(e).data('btn-type')
        btn_val = parseInt($(e).data('btn-val'))
        $.ajax({
                type: "POST",
                url: "/_add_item_to_cart",
                data: {'product_id': product_id,
                       'quantity': btn_val
                    },
                success: function(response) {
                    if (btn_type == "default"){
                        var counterGroup = $('<div>', {class: 'btn-group', role: 'group', 'aria-label': 'Basic outlined example'});
                        var minusButton = $('<button>', {type: 'button', class: 'btn btn-outline-danger add_to_cart', text: '-', 'data-product-id': product_id, 'data-btn-val': '-1', 'data-btn-type': 'counter', 'onclick': 'add_to_cart(this)'});
                        var countDisplay = $('<button>', {type: 'button', class: 'btn btn-outline-danger', text: '1', id: `product_${product_id}`});
                        var plusButton = $('<button>', {type: 'button', class: 'btn btn-outline-danger add_to_cart', text: '+', 'data-product-id': product_id, 'data-btn-val': '1', 'data-btn-type': 'counter', 'onclick': 'add_to_cart(this)'});
                        counterGroup.append(minusButton, countDisplay, plusButton);
                        $(`#product_btns_${product_id}`).html(counterGroup);
                    }
                    $(`#product_${product_id}`).html(response.quantity)
                    if (response.quantity == 0){
                        var addButton = $('<button>', {type: 'button', class: 'btn btn-outline-danger btn-sm mt-2 add_to_cart', text: 'Добавить в корзину', 'data-product-id': product_id, 'data-btn-val': '1', 'data-btn-type': 'default', 'onclick': 'add_to_cart(this)'});
                        $(`#product_btns_${product_id}`).html(addButton);
                    }
                    if (response.total_value == 0){
                        $('#total_price').html("")
                    }
                    else {
                        $('#total_price').html(response.total_value)
                    }

                }
        });
    }