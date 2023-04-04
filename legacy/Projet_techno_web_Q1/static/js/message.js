$(document).ready(function () {
    $('#usertbody').find('tr').click(function () {
        window.location.href = $(this).attr('media_link')
    })
})