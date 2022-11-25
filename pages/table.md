---
layout: page
title: hpc.social table
subtitle: The hpc.social Community HPC Resources Table
use-site-title: true
permalink: tabular/
---
    
<script src='https://code.jquery.com/jquery-3.5.1.js'></script>
<link rel='stylesheet' href='https://cdn.datatables.net/1.12.1/css/dataTables.bootstrap4.min.css'>

<style>
#software_filter, #software_length, #software_info {
 color: white;
}
td {
  color: white;
  background-color: #333;
}
thead {
  background-color: yellow;
}
.tag {
  margin-right: 2px !important;
}
</style>

<div class="container" style="padding-top:200px">
<a type="button" class="btn reset btn-theme filter-reset" onclick="$('#software').DataTable().search('').draw()" style='float:right;padding-bottom:5px' href="#">reset</a>

<table id="software"  class="table table-bordered" cellspacing="0" width="100%">
    <thead>
      <tr>
      <th>Location</th>
      <th>Type</th>
      <th>Count</th>
      <th>People</th>
      <th>Website</th>
     </tr>
  </thead>      
</table>
</div>


<script>
$(document).ready(function () {

$.getJSON("{{ site.baseurl }}/api/data.json", function(data) {
console.log(data)
$('#software').DataTable({
  data: data,
  pageLength: 50,
  columns: [
    { data: "address" },
    { data: "type"},
    { data: "count"},
    { data: "name"},
    { data: "website", 
      render: function ( data, type, row ) { 
         if (data != "") {
             return "<a target='_blank' type='button' class='btn btn-primary' href='" + data + "'>Website</a>"
         }
         return ""
      },
    },
  ]
});
});


// Ensure search is aligned to the right!
$('#software_filter').parent().attr("class", "col-md-12")
})
</script>
<script src='https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js'></script>
<script src='https://cdn.datatables.net/1.12.1/js/dataTables.bootstrap4.min.js'></script>
