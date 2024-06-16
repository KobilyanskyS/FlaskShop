function switchBannerActivity(e) {
    banner_id = $(e).data('banner-id')

    is_active = false

    if ($(e).data('is-active') == 'False' || $(e).data('is-active') == false)
        is_active = false
    else
        is_active = true

    console.log(banner_id)
    console.log(is_active)
    $.ajax({
        type: "POST",
        url: "/shop_admin/manage_index/_switch_banner_activity",
        data: {'banner_id': banner_id, 'is_active': is_active },
        success: function(response) {
            if (is_active == false){
                action = $('<button>', {class: 'btn btn-outline-danger', text: 'Сделать неактивным', 'data-banner-id' : banner_id,  'data-is-active' : response.is_active, 'onclick': 'switchBannerActivity(this)'})
                $(`#btn_${banner_id}`).html(action)
            }
            else{
                action = $('<button>', {class: 'btn btn-danger', text: 'Сделать активным', 'data-banner-id' : banner_id, 'data-is-active' : response.is_active, 'onclick': 'switchBannerActivity(this)'})
                $(`#btn_${banner_id}`).html(action)
            }

        }
    })
}