var start = ee.Date('2022-01-01');
var start = ee.Date('2022-01-01');
var finish = ee.Date('2022-12-31');

 

var roi = ee.Geometry.Rectangle(138, 34, 140, 36);

 

var images = ee.ImageCollection("COPERNICUS/S2_SR")
    .filterDate(start, finish);

 


function calc_MODIS_NDVI(image) {
  // (NIR - R) / (NIR + R)
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');

  var elev = ee.Image('USGS/GTOPO30');
  var land = elev.gte(0); // if elevation is greater than 0 m, then true (land) else false (sea).  

  return image.addBands(ndvi).updateMask(land);
}

 

var ndvi_land = images.map(calc_MODIS_NDVI);
var ndvi_max_land = ndvi_land.max(); // from 2005 to 2010

 

var visParams = {
  bands: ['NDVI'], 
  min:0.0, max:1.0, 
  palette: ['0000FF', 'FFFF00', 'FF0000']
};

 

// Create and style widgets.
var intro = ui.Panel([
  ui.Label({
    value: 'NDVI Inspector',
    style: {fontSize: '20px', fontWeight: 'bold'}
  }),
  ui.Label('Click a point on the map to inspect NDVI over time.')
]);

 

var lon = ui.Label();
var lat = ui.Label();

 

// Add the widgets to a new panel.
var panel = ui.Panel();
panel.add(intro);
panel.add(lon);
panel.add(lat);

 

// Add the new panel to the root panel.
ui.root.insert(0, panel);

 

// Setup the map.
Map.setCenter(139.37915755785914, 35.63951106416023, 20);
Map.addLayer(ndvi_max_land, visParams);

 

Map.onClick(function(coords) {
  lon.setValue('lon: ' + coords.lon);
  lat.setValue('lat: ' + coords.lat);

  // Add a red point to the map wherever the user clicks.
  var point = ee.Geometry.Point(coords.lon, coords.lat);
  var dot = ui.Map.Layer(point, {color: 'red'});
  Map.layers().set(1, dot);

  // Add an NDVI chart.
  var chart = ui.Chart.image.series({
    imageCollection: ndvi_land.select('NDVI'), 
    region: point, 
    reducer: ee.Reducer.mean(), 
    scale: 250
  });
  chart.setOptions({
    title: 'NDVI Over Time',
    vAxis: {title: 'NDVI'},
    hAxis: {title: 'date', format: 'MM-yy', gridlines: {count: 7}},
    interpolateNulls: true
  });
  panel.widgets().set(3, chart);
});

 

Map.style().set('cursor', 'crosshair');