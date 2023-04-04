const showSpeed = 200
const hideSpeed = showSpeed

$(document).ready($(function () {
    $('.error_msg').hide()
    $('form').hide(0)
    $('#hiding_before_ready').removeAttr('hidden')
    $('#add_film').click(function () {
        $('#SeriesForm').hide(hideSpeed)
        $('#FilmForm').delay(hideSpeed).show(showSpeed)
    })
    $('#add_series').click(function () {
        $('#FilmForm').hide(hideSpeed)
        $('#SeriesForm').delay(hideSpeed).show(showSpeed)
    })
    $('#FilmForm').submit(function (event) {
        event.preventDefault()
        console.log(event)
        const form = $(this)
        const actionUrl = form.attr('action')
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', $('#csrf_token').attr('value'))
                }
            }
        })
        $.ajax({
            type: 'POST',
            url: actionUrl,
            enctype: 'multipart/form-data',
            data: new FormData(this),
            dataType: 'json',
            processData: false,
            contentType: false,
            success: function (data, status, jqXHR) {
                console.log(data, status, jqXHR)
                if (data.redirect)
                    window.location.replace(data.redirect)
                else {
                    $('.error_msg').text('')
                    for (field in data.form) {
                        for (error of data.form[field]) {
                            const error_field = '#film-error-' + field
                            console.log(error_field)
                            $(error_field).append(error + '<br>')
                            $(error_field).css({ 'color': 'red' })
                            $(error_field).show()
                        }
                    }
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log(xhr, textStatus, errorThrown)
            }
        })
    })
    $('#SeriesForm').submit(function (event) {
        event.preventDefault()
        console.log(event)
        const form = $(this)
        const actionUrl = form.attr('action')
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', $('#csrf_token').attr('value'))
                }
            }
        })
        $.ajax({
            type: 'POST',
            url: actionUrl,
            data: new FormData(this),
            dataType: 'json',
            processData: false,
            contentType: false,
            success: function (data, status, jqXHR) {
                console.log(data, status, jqXHR)
                if (data.redirect)
                    window.location.replace(data.redirect)
                else {
                    $('.error_msg').text('')
                    for (field in data.form) {
                        for (error of data.form[field]) {
                            const error_field = '#series-error-' + field
                            console.log(error_field)
                            $(error_field).append(error + '<br>')
                            $(error_field).css({ 'color': 'red' })
                            $(error_field).show()
                        }
                    }
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log(xhr, textStatus, errorThrown)
            }
        })
    })
}))