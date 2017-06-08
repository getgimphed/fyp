;(function($){
ListFilterCollapsePrototype = {
    bindToggle: function(){
        var that = this;
        this.$filterEl.click(function(){
            that.$filterList.slideToggle();
        });
    },
    init: function(filterEl) {
        this.$filterEl = $(filterEl).css('cursor', 'pointer');
        this.$filterList = this.$filterEl.next('ul').hide();
        this.bindToggle();
    }
}
function ListFilterCollapse(filterEl) {
    this.init(filterEl);
}
ListFilterCollapse.prototype = ListFilterCollapsePrototype;

$(document).ready(function(){
    var  list = document.createElement("LI");
    var   btn = document.createElement("BUTTON");  
    var t = document.createTextNode("Edit");
    btn.setAttribute("id","editbtn");       
    btn.appendChild(t);      
    var lis = document.getElementsByClassName("object-tools");
    btn.style.display = "block";
    btn.style.float   = "left";
    btn.style.padding = "3px 12px";
    btn.style.background = "#999";
    btn.style.fontWeight="400";
    btn.style.fontSize      ="11px";
    btn.style.textTransform ="uppercase";
    btn.styleletterSpacing  ="0.5px";
    btn.style.borderRadius ="15px";
    btn.color = "#fff";
    list.appendChild(btn);
    lis[0].appendChild(list); 
    $('#changelist-filter').children('h3').each(function(){
        var collapser = new ListFilterCollapse(this);
    });
    var editpanel = document.getElementsByClassName("module");
    $(".aligned ").toggle();
    console.log("readched");
    $("#editbtn").click(function(){
        console.log("clicked");
        $(".aligned ").toggle();
    });
});

    $("#editbtn").trigger();
})(django.jQuery);