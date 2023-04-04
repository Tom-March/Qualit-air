$(document).ready(function () {
    $('#tbody-media').find('tr').click(function (event) {
        if (event.target.cellIndex == 0)
            window.location.href = $(this).attr('media_action')
    })
    $('#tbody-people').find('tr').click(function (event) {
        if (event.target.cellIndex == 0)
            window.location.href = $(this).attr('media_action')
    })
})