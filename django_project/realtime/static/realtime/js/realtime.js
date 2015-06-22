/**
 * Add events to the respective layer based on role.
 *
 * @param {string} url The url view to get events.
 * @param {object} event The role object.
 * @name L The Class from Leaflet.
 * @property geoJson Property of L class.
 * @property users Property of response object.
 * @function addTo add child element to the map.
 * @property properties Property of a feature.
 * @property popupContent Property of properties.
 * @function bindPopup Bind popup to marker
 */
function addEvents(url, event) {
  $.ajax({
    type: 'GET',
    url: url,
    dataType: 'json',
    data: {
      project: event['name']
    },
    success: function (response) {
      L.geoJson(
          response.events,
          {
            onEachFeature: onEachFeature,
            pointToLayer: function (feature, latlng) {
              return L.marker(latlng,{icon: event['icon'] });
            }
          }).addTo(event['layer']);
    }});

  function onEachFeature(feature, layer) {
    // Set the popup content if it does have the content
    if (feature.properties && feature.properties.popupContent) {
      layer.bindPopup(feature.properties.popupContent);
    }
  }
}