$(document).ready($(function () {
    $("#sortable").sortable({
        revert: true,
        placeholder: "ui-state-highlight"
    });
    $("ul, li").disableSelection();
}))