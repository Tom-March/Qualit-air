$(document).ready(function () {
    $("#myInput").on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $("#media-table tr").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
    check_url = $('#myInput').attr('check_url')
    var list_media_ids
    $.ajax({
        type: 'POST',
        url: check_url,
        async: !1,
        success: function (data, status, jqXHR) {
            console.log(data, status, jqXHR)
            list_media_ids = data.media_query
            for (id of data.id_media_user) {
                for (let media_id of list_media_ids) {
                    btn_id = "#addlist_" + media_id
                    if (media_id == id) {
                        $(btn_id).text('IN LIST ✔')
                        $(btn_id).attr('class', "btn btn-outline-success")
                    }
                }
            }
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(xhr, textStatus, errorThrown)
        }
    })
    $('#media-table').find('tr').click(function (event) {
        if (event.target.cellIndex < 5)
            window.location.href = $(this).attr('href')
    })
    for (let media_id of list_media_ids) {
        btn_id = "#addlist_" + media_id
        $(btn_id).click(function (event) {
            event.preventDefault()
            console.log(event)
            const btn = $(this)
            id_media = $(btn).attr('media_id')
            const hrefUrl = btn.attr('href')
            $.ajax({
                type: 'POST',
                url: check_url,
                success: function (data, status, jqXHR) {
                    console.log(data, status, jqXHR)
                    wrong = false
                    for (id of data.id_media_user) {
                        if (id_media == id) {
                            wrong = true
                            let confirm_rm = confirm("This is already in your list.\nDo you want to remove it from your list?")
                            if (confirm_rm) {
                                $.ajax({
                                    type: 'POST',
                                    url: $('#addlist').attr('rm_link'),
                                    success: function (data, status, jqXHR) {
                                        console.log(data, status, jqXHR)
                                        location.reload()
                                    },
                                })
                            }
                        }
                    }
                    if (!wrong) {
                        $(btn).text('IN LIST ✔')
                        $(btn).attr('class', "btn btn-outline-success")
                        $.ajax({
                            type: 'POST',
                            url: hrefUrl,
                        })
                    }

                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr, textStatus, errorThrown)
                }
            })
        })
    }
});