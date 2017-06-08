Date.parseDate = function( input, format ){
  return moment(input,format).toDate();
};
Date.prototype.dateFormat = function( format ){
  return moment(this).format(format);
};



$(document).ready(function(){

  $('.datetimepicker').datetimepicker({
  });

  $('#checkout').datetimepicker({
    onShow: function(ct){
      this.setOptions({
        minDate: $('#checkin').val() ? $('#checkin').val() : new Date()
      });
    },
    format: 'DD.MM.YYYY',
    formatDate: 'DD.MM.YYYY',
    datepicker: true,
    timepicker: false
  });

});