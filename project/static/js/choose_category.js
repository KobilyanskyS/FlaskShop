function chooseCategory() {
    category_id = $("#category option:selected").val();
    $.ajax({
        type: "POST",
        url: "/shop_admin/manage_index/_choose_category",
        data: {'category_id': category_id },
        success: function(response) {
            $('#cur_category').html(response);
        }
    })
}

$("#choose_category").click(chooseCategory);