$(document).ready($(function () {
    const editForm = $('#editForm')
    editForm.on('input', function () {
        window.onbeforeunload = function () {
            return true;
        };
    });
    $('.error_msg').hide()
    $('#csrf_token_error').addClass('alert alert-danger')
    editForm.submit(function (event) {
        event.preventDefault()
        console.log(event)
        const actionUrl = editForm.attr('action')
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
            data: editForm.serialize(),
            dataType: 'json',
            success: function (data, status, jqXHR) {
                console.log(data, status, jqXHR)
                if (data.redirect) {
                    window.onbeforeunload = null;
                    window.location.replace(data.redirect)
                }
                else {
                    $('.error_msg').text('')
                    $('#current_passwd').val('')
                    $('#new_passwd').val('')
                    $('#new_passwd_confirm').val('')
                    for (field in data.form) {
                        for (error of data.form[field]) {
                            const error_field = '#' + field + '_error'
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