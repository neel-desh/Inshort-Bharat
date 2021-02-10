// custom date input
$('.date').bind('keyup',function(event){
 var key = event.keyCode || event.charCode || event.which;
  var dateVal = $(this).val();
  var dateVal__ = dateVal.slice(0, -1);
  var lastKey = dateVal.slice(-1);
  var length = dateVal.length;
  var daysInMonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  
  if ((key == 8 || key == 46) && (length == 5 || length == 2)) {// Deleting on a '/' deletes the '/'
    $(this).val(dateVal__);
  }
  if ((key >= 48 && key <= 57) || (key >= 96 && key <= 105)) {// If key is a number allow data input
    if ((length === 4 && lastKey > 3) || (length === 1 && lastKey > 1)) {
      dateVal = dateVal__ + '0' + lastKey;
      length++;
    }
    if (length === 2 && (dateVal.split('')[0] === '1' && lastKey > 2)) {
      dateVal = dateVal__ + '2';
    }
    if (length === 5) {// Checks to compare the month vs the day value
      var monthVal = dateVal.slice(0,2);
      var dayVal = dateVal.slice(-2);
      if (dayVal > daysInMonth[monthVal - 1]) {
        dayVal = daysInMonth[monthVal - 1];
        dateVal = dateVal.slice(0, -2).toString() + dayVal;
      }
    }
    if (length === 2 || length === 5) {
      dateVal += '/';
      $(this).val(dateVal);
    }
  }
  else if (key >= 65 && key <= 90 && key !== 86 || key > 105) {// Else if key is a non-numeric value, remove it
    $(this).val(dateVal__);
  }
});

$('.date').bind('blur',function(){
  $(this).attr('placeholder', '');
  var $element = $(this).val();
  var yyForToday = new Date().getFullYear().toString().substr(2,2);
  if ($element.length == 8) {
    var century = ($element.slice(-2) > yyForToday) ? 19 : 20;
    $element = $element.slice(0, -2) + century + $element.slice(-2);
    $(this).val($element);
  }
  // Add a span element describing the error for the user
  if ($element.length < 10 && $element.length !== 0) {
    $(this).parent().find('*').css({ 'border-color': 'red', 'color': 'red' });
    $(this).parent().parent().append('<span class="dateError" style="color:red">*dates are entered in mm/dd/yyyy format</span>');
  }
  if ($element.length == 6) {
    $(this).parent().parent().append('<br/><span class="dateError" style="color:red">*a year was not entered</span>');
  }
  $(this).on('focus', function () {
    $(this).parent().find('*').css({ 'border-color': '', 'color': '' });
    $(this).parent().parent().find('span.dateError').remove();
  })
});