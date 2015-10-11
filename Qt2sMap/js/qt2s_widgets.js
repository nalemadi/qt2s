
    // Read all table IDs:
    var map_table = '[REDACTED]';
    var timeline_table = '[REDACTED]';
    var hashtags_table = '[REDACTED]';
    var tweets_table = '[REDACTED]';
    var my_key = '[REDACTED]';

   	function drawVisualization() {
	google.visualization.drawChart({
        "containerId": "trends_content",
        "dataSourceUrl":"http://www.google.com/fusiontables/gvizdata?tq=",
        "query":"SELECT 'date', 'freq' FROM " +
                timeline_table,
        "refreshInterval": 5,
        "chartType": "LineChart",
        "options": {}
     });
    }
	google.load("visualization", "1.1", {packages:["corechart"]});
    google.setOnLoadCallback(drawVisualization);
</script>

<script type="text/javascript">
  function initialize() {
    google.maps.visualRefresh = true;
    var isMobile = (navigator.userAgent.toLowerCase().indexOf('android') > -1) ||
      (navigator.userAgent.match(/(iPod|iPhone|iPad|BlackBerry|Windows Phone|iemobile)/));
    if (isMobile) {
      var viewport = document.querySelector("meta[name=viewport]");
      viewport.setAttribute('content', 'initial-scale=1.0, user-scalable=no');
    }
     var mapDiv = document.getElementById('maps_content');
    mapDiv.style.width = isMobile ? '100%' : '1000px';
    mapDiv.style.height = isMobile ? '100%' : '490px';
    var map = new google.maps.Map(mapDiv, {
      center: new google.maps.LatLng(52.34616512555606, 15.81693150000001),
      zoom: 2,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    layer = new google.maps.FusionTablesLayer({
      map: map,
      heatmap: { enabled: false },
      query: {
        select: "col3",
        from: map_table,
        where: ""
      },
      options: {
        styleId: 2,
        templateId: 2
      }
    });

    if (isMobile) {
      var legend = document.getElementById('googft-legend');
      var legendOpenButton = document.getElementById('googft-legend-open');
      var legendCloseButton = document.getElementById('googft-legend-close');
      legend.style.display = 'none';
      legendOpenButton.style.display = 'block';
      legendCloseButton.style.display = 'block';
      legendOpenButton.onclick = function() {
        legend.style.display = 'block';
        legendOpenButton.style.display = 'none';
      }
      legendCloseButton.onclick = function() {
        legend.style.display = 'none';
        legendOpenButton.style.display = 'block';
      }
    }
  }

  google.maps.event.addDomListener(window, 'load', initialize);
</script>