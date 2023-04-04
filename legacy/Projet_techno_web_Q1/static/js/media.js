$(document).ready(function () {
    $('#mediareviewtbody').find('tr').click(function (event) {
        window.location.href = $('#mediareviewtbody').attr('redirect')
    })
    $('#flagbtn').attr('disabled', true)
    check_url = $("#addlist").attr('check_url')
    $("#addlist").click(function (event) {
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
                    $.ajax({
                        type: 'POST',
                        url: hrefUrl,
                        success: function (data, status, jqXHR) {
                            console.log(data, status, jqXHR)
                            $('body').load($('#addlist').attr('reload_page'))
                        }
                    })
                }

            },
            error: function (xhr, textStatus, errorThrown) {
                console.log(xhr, textStatus, errorThrown)
            }

        })
    })
    $.ajax({
        type: 'POST',
        url: check_url,
        success: function (data, status, jqXHR) {
            console.log(data, status, jqXHR)
            for (id of data.id_media_user) {
                if ($("#addlist").attr("media_id") == id) {
                    $("#addlist").text('IN YOUR LIST ✔')
                }
            }

        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(xhr, textStatus, errorThrown)
        }
    })
    $("#flagbtn").click(function (event) {
        why = prompt("Why do you report this media?")
        if (why !== null) {
            actionUrl = $(this).attr("action")
            $.ajax({
                type: 'POST',
                url: actionUrl,
                data: { "message": why },
                datatype: "json",
                success: function (data, status, jqXHR) {
                    console.log(data, status, jqXHR)
                    alert("This page has successfully been reported.")
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr, textStatus, errorThrown)
                }
            })
        }
    })
    $("#deletebtn").click(function (event) {
        acc = confirm("Are you sure you want to delete this?")
        if (acc) {
            actionUrl = $(this).attr("action")
            $.ajax({
                type: 'POST',
                url: actionUrl,
                datatype: "json",
                success: function (data, status, jqXHR) {
                    console.log(data, status, jqXHR)
                    window.location.replace(data.redirect)
                },
                error: function (xhr, textStatus, errorThrown) {
                    console.log(xhr, textStatus, errorThrown)
                }
            })
        }
    })

});