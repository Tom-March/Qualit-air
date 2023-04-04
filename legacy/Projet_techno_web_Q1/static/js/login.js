$(document).ready($(function () {
    $('.error_msg').hide()
    $('#error-csrf_token').addClass('alert alert-danger')
    $('#login_form').submit(function (event) {
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
            data: form.serialize(),
            dataType: 'json',
            success: function (data, status, jqXHR) {
                console.log(data, status, jqXHR)
                if (data.redirect)
                    // window.location.href = data.redirect
                    window.location.replace(data.redirect)
                else {
                    $('#error_login').text('')
                    $('#error_login').attr('hidden', true)
                    $('.error_msg').hide()
                    $('#passwd').val('')
                    for (field in data.form) {
                        if (field === 'error_login') {
                            $('#error_login').text(data.form[field])
                            $('#error_login').removeAttr('hidden')
                        }
                        const error_field = '#error-' + field
                        console.log(error_field)
                        $(error_field).text(data.form[field])
                        $(error_field).css({ 'color': 'red' })
                        $(error_field).show()
                    }
                }
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log(xhr, textStatus, errorThrown)
            }
        })
    })
}))