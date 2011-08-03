if (typeof($j) === "undefined" && typeof(jQuery) !== "undefined") {
  var $j = jQuery.noConflict();
}


function hideSidebar()
{
    $j('#sidebar').hide();
    $j('#main').width('100%');
    $j('#toggle_img').attr("src", $j("#show-icon")[0].href);
    $j('#toggle_img').attr("title", "Show Sidebar");
    $j.cookie('hide-sidebar', 'yes', { expires: 30, path: '/'  });
}

function showSidebar()
{
    $j('#sidebar').show();
    $j('#main').width('77%');
    $j('#toggle_img').attr("src", $j("#hide-icon")[0].href);
    $j('#toggle_img').attr("title", "Hide Sidebar");
    $j.cookie('hide-sidebar', null, { expires: 30, path: '/'  });
}

function toggle_sidebar() {
  if( $j("#sidebar").is(":visible") )
      hideSidebar();
  else
      showSidebar();
}

$j(document).ready(function($){
  // accordeon
  $("#nav .more:not(.active) ul").hide();
  $("#nav .more a").live('click', function() {
    $(this).siblings('ul').toggle('slide');
  });

  $("table.table tr.link").live('click', function(e) {
    // trs and tds are things that we want to link to the edit page
    // if the click's target is a button for instance, we don't want to move the user.
    if ($(e.target).is('tr') || $(e.target).is('td') || $(e.target).is('div.bar')) {
      window.location.href = $(this).attr("data-link");
    };
  });

  // On the list page, the checkbox in th table's header toggles all the checkboxes underneath it.
  $("table.table input.checkbox.toggle").live('click', function() {
    var checked_status = $(this).is(":checked");
    $("td.action.select input.checkbox[name='bulk_ids']").each(function() {
      $(this).attr('checked', checked_status);

      if (checked_status) {
        $(this).parent().addClass("checked");
      } else {
        $(this).parent().removeClass("checked");
      }

    });
  });

  // Hide Flash messages after 10 seconds.
  $('.flash').delay(10000).fadeOut();

  // Toggle sidebar
  //$('#toggle').toggle(showSidebar, hideSidebar);
  if ( $.cookie('hide-sidebar') == null )
  {
    showSidebar();
  }
  else
  {
    hideSidebar();
  }

  // Widgets for Date, Time and DateTime fields
  $(".date").datepicker({
      changeMonth: true,
      changeYear: true,
      dateFormat: "yy-mm-dd"
  });
  $(".time").timepicker({
      timeFormat: "hh:mm:ss"
  });
  $(".datetime").datetimepicker({
      changeMonth: true,
      changeYear: true,
      dateFormat: "yy-mm-dd",
      timeFormat: "hh:mm:ss"
  });

  // Apply Chosen theme for select and multi-select boxes
  $(".w2p_fw select").chosen();
});
