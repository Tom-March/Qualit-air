$(document).ready(function () {
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