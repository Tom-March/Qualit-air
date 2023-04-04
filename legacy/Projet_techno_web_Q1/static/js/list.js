$(document).ready(function () {
    $("#myInput").on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $("#myTable tr").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) >= 0)
        });
    });
    $('#myTable').find('tr').click(function (event) {
        if (event.target.cellIndex < 2)
            window.location.href = $(this).attr('link')
    })
});
