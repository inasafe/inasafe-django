/**
 * Author: Rizky Maulana Nugraha (lana.pcfre@gmail.com)
 * Description:
 * This file contains methods related directly to realtime.
 * It follows Airbnb Javascript style guide (https://github.com/airbnb/javascript)
 * and JSDoc for the documentation.
 */

/**
 * Global vars
 */

/**
 * A dictionary with shake_id as key and marker as its value
 * @type {object}
 */
var map_events = {};
/**
 * Leaflet map
 * @type {L.map}
 */
var map;

/**
 * Event geo json returned by realtime
 */
var event_json;

/**
 * Create basemap instance to be used.
 *
 * @param {string} url The URL for the tiles layer
 * @param {string} attribution The attribution of the layer
 * @property tileLayer
 * @returns {object} base_map
 */
function createBasemap(url, attribution) {
    var base_map;
    base_map = L.tileLayer(url, {
        attribution: attribution,
        maxZoom: 18
    });
    return base_map;
}

/**
 * Create IconMarkerBase that will be used for icon marker.
 *
 * @param {string} shadow_icon_path The path to shadow icon.
 * @returns {object} IconMarkerBase
 * @property Icon
 */
function createIconMarkerBase(shadow_icon_path) {
    var IconMarkerBase;
    IconMarkerBase = L.Icon.extend({
        options: {
            shadowUrl: shadow_icon_path,
            iconSize: [32, 32],
            shadowSize: [38, 24],
            iconAnchor: [16, 16],
            shadowAnchor: [9, 8],
            popupAnchor: [-2, -32]
        }
    });
    return IconMarkerBase;
}

/**
 * Create leaflet icon marker.
 *
 * @param {string} icon_path The icon path.
 * @param {string} shadow_path The shadow path.
 * @return {IconMarkerBase} icon_marker
 */
function createIconMarker(icon_path, shadow_path) {
    var IconMarkerBase = createIconMarkerBase(shadow_path);
    return new IconMarkerBase({iconUrl: icon_path});
}

/**
 * Closure to create handler for showEvent
 * @param {L.map} map Leaflet map
 * @param {{}} map_events dictionary of shake_id to marker object
 * @return {function} Show in the map a particular event based on shake_id
 */
function createShowEventHandler(map, markers, map_events) {
    var showEventHandler = function showEventHandler(shake_id) {
        var marker = map_events[shake_id];
        var map_id = $(map._container).attr("id");
        // scroll to map
        $('html, body').animate({
            scrollTop: $("#"+map_id).offset().top
        }, 500);
        markers.zoomToShowLayer(marker, function () {
            var fitBoundsOption = {
                maxZoom: 10,
                pan: {
                    animate: true,
                    duration: 0.5
                },
                zoom: {
                    animate: true,
                    duration: 0.5
                }
            };

            map.fitBounds([
                marker.getLatLng(),
                marker.getLatLng()
            ], fitBoundsOption);
            marker.openPopup();
        });
    };
    return showEventHandler;
}

/**
 * Closure to create handler for showReport
 * @param {string} report_url A report url that contains shake_id placeholder
 * @return {function} Download the report based on shake_id
 */
function createShowReportHandler(report_url) {
    var showReportHandler = function (shake_id) {
        var url = report_url;
        // replace magic number 000 with shake_id
        url = url.replace('000', shake_id);
        $.get(url, function (data) {
            if (data && data.report_pdf) {
                var pdf_url = data.report_pdf;
                window.location = pdf_url;
            }
        }).fail(function(e){
            console.log(e);
            if(e.status == 404){
                alert("No Report recorded for this event.");
            }
        });
    };
    return showReportHandler;
}

/**
 * Create update filter handler based on url and dataHandler
 * @param {string} url URL to send filtered data
 * @param {function} dataHandler Function to handle retrieved data
 * @return {Function} Update handler function
 */
function createUpdateFilterHandler(url, form_filter, location_filter, dataHandler) {
    var updateFilterHandler = function (e) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        var form_filter_query = form_filter.serialize();
        var location_filter_query = "";
        if (location_filter.isEnabled()) {
            location_filter_query += "&in_bbox=" + location_filter.getBounds().toBBoxString();
        }
        $.get(url + "?" + form_filter_query + location_filter_query, dataHandler);
    };
    return updateFilterHandler;
}

/**
 * filter a given geojson input in client side
 * @param data_input {{}} a geo json collections
 * @param min_date {string} date formattable string
 * @param max_date {string} date formattable string
 * @param min_magnitude {string} float string
 * @param max_magnitude {string} float string
 * @return {{features: Array, type: *}}
 */
function clientFilter(data_input, min_date, max_date, min_magnitude, max_magnitude){
    var filtered_features = [];
    var features = data_input.features;
    for(var i=0;i<features.length;i++){
        var feature = features[i];

        // time filter
        var time = new Date(Date.parse(feature.properties.time));
        if(min_date && time < new Date(Date.parse(min_date))){
            continue
        }

        if(max_date && time > new Date(Date.parse(max_date))){
            continue
        }

        // magnitude
        var magnitude = feature.properties.magnitude;
        if(min_magnitude && magnitude < parseFloat(min_magnitude)){
            continue
        }

        if(max_magnitude && magnitude > parseFloat(max_magnitude)){
            continue
        }

        // filtered
        filtered_features.push(feature);
    }
    return {
        features: filtered_features,
        type: data_input.type
    };
}

/**
 *
 * @param data_input {{}} geo json collections
 * @param bounds {L.latLngBounds}
 * @return {{features: Array, type: *}}
 */
function clientExtentFilter(data_input, bounds){
    var filtered_features = [];
    var features = data_input.features;
    if(bounds.isValid()){
        for(var i=0;i<features.length;i++){
            var feature = features[i];
            var point = L.latLng(
                feature.geometry.coordinates[1],
                feature.geometry.coordinates[0]);
            if(!bounds.contains(point)){
                continue
            }

            // filtered
            filtered_features.push(feature);
        }
    }
    else{
        filtered_features = features;
    }
    return {
        features: filtered_features,
        type: data_input.type
    };
}

/**
 * Create update filter handler based on url and dataHandler in the client
 * side
 * @param {string} url URL to send filtered data
 * @param {function} dataHandler Function to handle retrieved data
 * @return {Function} Update handler function
 */
function createClientUpdateFilterHandler(url, form_filter, location_filter, dataHandler) {
    var updateFilterHandler = function (e) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        // filter by bounds
        var filtered = clientExtentFilter(event_json, location_filter.getBounds());
        filtered = clientFilter(
            filtered,
            $("#id_start_date", form_filter).val(),
            $("#id_end_date", form_filter).val(),
            $("#id_minimum_magnitude", form_filter).val(),
            $("#id_maximum_magnitude", form_filter).val()
        );
        dataHandler(filtered);
    };
    return updateFilterHandler;
}

/**
 * Dynatable related functions
 */

/**
 * Create Action Writer based on button_templates
 *
 * @param {object} button_templates The list of dictionary containing name
 * and handler string
 * @return {function} a dynatable row function
 */
function createActionRowWriter(button_templates) {
    writer = function (rowIndex, record, columns, cellWriter) {
        var tr = '';

        // grab the record's attribute for each column
        for (var i = 0, len = columns.length; i < len; i++) {
            tr += cellWriter(columns[i], record);
        }
        // for action column
        $span = $('<span></span>');
        for (var i = 0; i < button_templates.length; i++) {
            var button = button_templates[i];
            $button = $('<button></button>');
            $button.addClass('btn btn-primary');
            $button.text(button.name);
            $button.attr('onclick', button.handler + "('" + record.shake_id + "')");
            $span.append($button);
        }
        tr += '<td>' + $span.html() + '</td>';

        return '<tr>' + tr + '</tr>';
    };
    return writer;
}

/**
 * Add custom dynatable header
 * @param {string} selector The selector of the table
 * @param {string} header_name The name of the new column header
 */
function addActionColumn(selector, header_name) {
    $container = $(selector);
    $header = $('thead tr', $container);
    $th = $('<th></th>');
    $a = $('<a></a>');
    $a.attr('href', '#');
    $a.text(header_name);
    $th.addClass('dynatable-head');
    $th.append($a);
    $header.append($th);
}
