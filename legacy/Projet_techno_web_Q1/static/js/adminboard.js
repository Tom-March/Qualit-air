function jq(myid) {
    return myid.replace(/(:|\.|\[|\]|,|=|@)/g, "\\$1");
}

$(document).ready($(function () {
    user_list = $('#data').children()
    urlpost = $('#data').attr('link')
    length = user_list.length
    id_list = []
    for (i = 0; i < length; i++) {
        id_list.push(user_list[i].getAttribute('id'))
    }

    for (i = 0; i < length; i++) {
        jqIdList = jq(id_list[i])
        id_block = '#block_' + jqIdList
        id_change_group = '#change_group_' + jqIdList
        $(id_block).click(function () {
            this_button = this
            user_id = $(this_button).attr('user_id')
            $.ajax({
                type: 'POST',
                url: urlpost,
                data: { 'id': user_id, 'action': 'block' },
                dataType: 'json',
                success: function (data, status, jqXHR) {
                    console.log(data, status, jqXHR)
                    $('body').load($(this_button).attr('reload'))
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr, textStatus, errorThrown)
                }
            })
        })
        $(id_change_group).click(function () {
            this_button = this
            user_id = $(this_button).attr('user_id')
            $.ajax({
                type: 'POST',
                url: urlpost,
                data: { 'id': user_id, 'action': 'change_group' },
                dataType: 'json',
                success: function (data, status, jqXHR) {
                    console.log(data, status, jqXHR)
                    $('body').load($(this_button).attr('reload'))
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr, textStatus, errorThrown)
                }
            })
        })
    }
    $('#admintbody').find('tr').click(function (event) {
        if (event.target.cellIndex < 3)
            window.location.href = $(this).attr('admin_link')
    })
    $('#adminbody').find('tr').click(function (event) {
        if (event.target.cellIndex < 3)
            window.location.href = $(this).attr('admin_link')
    })

}))