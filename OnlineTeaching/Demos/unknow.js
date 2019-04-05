var EdTable = function() {
    // 给单元格绑定事件
    function initBindGridEvent() {
        $("td.editable").unbind();
        // 添加单元格双击事件
        addGridDbClickEvent();
    }

    //给单元格添加双击事件
    function addGridDbClickEvent() {
        $("td.simpleInput").bind("dblclick", function() {
            $('.simpleInput').each(function() {
                $(this).removeClass("selectCell");
            });
            var val = $(this).html();
            var width = $(this).css("width");
            var height = $(this).css("height:8px");
            $(this).html("<input type='text' onblur='EdTable.saveEdit(this)' style='width:" + width + ";height:" + height + "; padding:0px; margin:0px;' value='" + val + "' >");
            $(this).children("input").select();
        });
    }

    // 单元格失去焦点后保存表格信息
    function saveEdit(gridCell) {
        var pnt = $(gridCell).parent();
        $(pnt).html($(gridCell).attr("value"));
        $(gridCell).remove();
    }
    return {
        initBindGridEvent: initBindGridEvent,
        saveEdit: saveEdit
    }
}();
