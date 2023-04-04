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
        success: function (data, status, jqXHR) {
            console.log(data, status, jqXHR)
            list_media_ids = data.media_query
            for (id of data.person_plays_in) {
                for (let media_id of list_media_ids) {
                    btn_id = "#addlist_" + media_id
                    if (media_id == id) {
                        $(btn_id).text('PLAYS IN ✔')
                        $(btn_id).attr('class', "btn btn-outline-success")
                    }
                }
            }
            for (let media_id of list_media_ids) {
                btn_id = "#addlist_" + media_id
                $(btn_id).click(function (event) {
                    event.preventDefault()
                    console.log(event)
                    const btn = $(this)
                    media_id = $(btn).attr('media_id')
                    const hrefUrl = btn.attr('href')
                    $.ajax({
                        type: 'POST',
                        url: check_url,
                        success: function (data, status, jqXHR) {
                            console.log(data, status, jqXHR)
                            wrong = false
                            for (id of data.person_plays_in) {
                                if (media_id == id) {
                                    wrong = true
                                    $.ajax({
                                        type: 'POST',
                                        url: hrefUrl,
                                        data: media_id,
                                        success: function (data, status, jqXHR) {
                                            console.log(data, status, jqXHR)
                                            location.reload()
                                        }
                                    })
                                }
                            }
                            if (!wrong) {
                                $(btn).text('PLAYS IN ✔')
                                $(btn).attr('class', "btn btn-outline-success")
                                $.ajax({
                                    type: 'POST',
                                    url: hrefUrl,
                                    data: media_id,
                                })
                            }

                        },
                        error: function (xhr, textStatus, errorThrown) {
                            console.log(xhr, textStatus, errorThrown)
                        }
                    })
                })
            }
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(xhr, textStatus, errorThrown)
        }
    })
});