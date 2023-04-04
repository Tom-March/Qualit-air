$(document).ready($(function () {
    $('.error_msg').hide()
    for (let i of [1, 2, 3, 4, 5]) {
        $('#' + i).click(function (event) {
            $('#rating').val(event.currentTarget.defaultValue)
        })
    }
    ratingVal = $('#error-rating').attr('defaultValue')
    if (ratingVal)
        $('#' + ratingVal).trigger('click')
    stateVal = $('#error-state').attr('defaultValue')
    if (stateVal != 4) {
        $('#selectFieldForState4').removeAttr('selected')
        $('#selectFieldForState' + stateVal).attr('selected', true)
    }
    $('#clear_stars').click(function () {
        $('#rating').val(null)
        for (i = 1; i < 6; i++) {
            $('#' + i).prop('checked', false)
        }
    })
    $('#blog_form').submit(function (event) {
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