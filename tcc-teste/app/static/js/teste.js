var vals;
$('#bt-ok').click(function() {
    vals = [];
    $("input[type='checkbox']:checked").each(function(){
        vals.push($(this).prop('name'));
    });
    $("#text").val(vals.join(', '));
});
