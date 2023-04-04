$(document).ready($(function () {
    $('.error_msg').hide()
    $('#error-csrf_token').addClass('alert alert-danger')
    $('#register_form').submit(function (event) {
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
            processData: false,
            contentType: false,
            dataType: 'json',
            success: function (data, status, jqXHR) {
                console.log(data, status, jqXHR)
                if (data.redirect)
                    window.location.replace(data.redirect)
                else {
                    $('.error_msg').text('')
                    $('#passwd').val('')
                    $('#passwd_confirm').val('')
                    for (field in data.form) {
                        for (error of data.form[field]) {
                            const error_field = '#error-' + field
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