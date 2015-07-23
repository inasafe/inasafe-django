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
function createBasemap(url, subdomains, attribution) {
    var base_map;
    base_map = L.tileLayer(url, {
        attribution: attribution,
        subdomains: subdomains,
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
 * @return {function} Open the report based on shake_id in a new tab
 */
function createShowReportHandler(report_url) {
    var showReportHandler = function (shake_id) {
        var url = report_url;
        // replace magic number 000 with shake_id
        url = url.replace('000', shake_id);
        $.get(url, function (data) {
            if (data && data.report_pdf) {
                var pdf_url = data.report_pdf;
                window.open(pdf_url, '_blank');
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
 * A script to download link to disk.
 * Source: http://stackoverflow.com/questions/3077242/force-download-a-pdf-link-using-javascript-ajax-jquery/29266135#29266135
 * @param fileURL {string} the file url
 * @param fileName {string} filename to save
 */
function SaveToDisk(fileURL, fileName) {
    if (!window.ActiveXObject) {
        var save = document.createElement('a');
        save.href = fileURL;
        save.target = '_blank';
        save.download = fileName || 'unknown';

        var evt = new MouseEvent('click', {
            'view': window,
            'bubbles': true,
            'cancelable': false
        });
        save.dispatchEvent(evt);

        (window.URL || window.webkitURL).revokeObjectURL(save.href);
    }

    // for IE < 11
    else if ( !! window.ActiveXObject && document.execCommand)     {
        var _window = window.open(fileURL, '_blank');
        _window.document.close();
        _window.document.execCommand('SaveAs', true, fileName || fileURL)
        _window.close();
    }
}

/**
 * Closure to create handler for downloadReport
 * @param {string} report_url A report url that contains shake_id placeholder
 * @return {function} Download the report based on shake_id
 */
function createDownloadReportHandler(report_url) {
    var downloadReportHandler = function (shake_id) {
        var url = report_url;
        // replace magic number 000 with shake_id
        url = url.replace('000', shake_id);
        $.get(url, function (data) {
            if (data && data.report_pdf) {
                var pdf_url = data.report_pdf;
                SaveToDisk(pdf_url, data.shake_id+'-'+data.language+'.pdf');
            }
        }).fail(function(e){
            console.log(e);
            if(e.status == 404){
                alert("No Report recorded for this event.");
            }
        });
    };
    return downloadReportHandler;
}

/**
 * Create update filter handler based on url and dataHandler
 * @param {string} url URL to send filtered data
 * @param {function} dataHandler Function to handle retrieved data
 * @return {Function} Update handler function
 */
function createUpdateFilterHandler(url, form_filter, location_filter, dataHandler) {
    var updateFilterHandler = function (e, reset) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        var form_filter_query = form_filter.serialize();
        var location_filter_query = "";
        if (location_filter.isEnabled() && reset!==true) {
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
    var updateFilterHandler = function (e, reset) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        // filter by bounds
        var filtered = event_json;
        if(reset !== true){
            filtered = clientExtentFilter(event_json, location_filter.getBounds());
        }
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
 * Modify a given target text with relevant map filters descriptions
 * @param target {string} Jquery selector string for target element
 */
function modifyMapDescriptions(target){
    var $target = $(target);

    var magnitude_string = "";
    var min_magnitude = $("#id_minimum_magnitude").val();
    var max_magnitude = $("#id_maximum_magnitude").val();
    if(min_magnitude && max_magnitude){
        magnitude_string = 'with magnitudes between '+min_magnitude+' and '+max_magnitude;
    }
    else if(min_magnitude){
        magnitude_string = 'with magnitudes greater or equal than '+min_magnitude;
    }
    else if(max_magnitude){
        magnitude_string = 'with magnitudes less or equal than '+max_magnitude;
    }

    var date_string = '';
    var start_date = $("#id_start_date").val();
    var end_date = $("#id_end_date").val();
    if(start_date && end_date){
        var start_moment = moment(start_date);
        var end_moment = moment(end_date);
        date_string = 'over the period '+start_moment.format('LL')+' and '+end_moment.format('LL');
    }
    else if(start_date){
        var start_moment = moment(start_date);
        date_string = 'after '+start_moment.format('LL');
    }
    else if(end_date){
        var end_moment = moment(end_date);
        date_string = 'before '+end_moment.format('LL');
    }
    var description = 'Earthquake events';
    if(magnitude_string){
        description+=' '+magnitude_string;
    }
    if(date_string){
        description+=' '+date_string;
    }
    $target.text(description);
}

/**
 * Modify location filter plugin styles.
 * This function is used to overrides original styles
 */
function modifyLocationFilterStyle(){
    var $location_filter_container = $(".location-filter");
    $location_filter_container.removeClass('button-container').addClass('leaflet-bar');
    var $enable_button = $(".enable-button", $location_filter_container);
    $enable_button.text("");
    $enable_button.click(function(){
        // disable text
        $("a", $location_filter_container).text("");
        var $toggle_button = $(".enable-button", $location_filter_container);
        $toggle_button.toggleClass("remove-button");
    });
}

/**
 * Modify default search and show labels of dynatable
 */
function modifySearchAndShowLabels(){
    $(".dynatable-per-page-label").text("Show");
    var $search_container = $(".dynatable-search");
    var $children = $search_container.children();
    $search_container.text("Search").append($children);
}

/**
 * Fit all the markers in the map, so every markers is seen.
 * @param map {L.map} leaflet map
 * @param markers {L.LayerGroup} leaflet layer
 * @param padding {Array} padding options of fitBounds method in map object
 */
function mapFitAll(map, markers, padding){
    var padding = padding | [100, 100];
    map.fitBounds(markers.getBounds(), {
        padding: padding
    });
}

/**
 * Create FitAll control using Leaflet Control Extend
 */
L.Control.FitAll = L.Control.extend({
    options: {
        position: 'topleft',
        title: 'Fit All',
        markers: undefined,
    },
    onAdd: function(map){
        this._container = L.DomUtil.create('div', 'control-fit-all' +
            ' leaflet-bar');
        this._button = L.DomUtil.create('a', 'fit-all-button glyphicon glyphicon-globe', this._container);
        this._button.href = '#';
        this._button.title = this.options.title;
        var that = this;
        L.DomEvent.on(this._button, 'click', function(event){
            L.DomEvent.stopPropagation(event);
            L.DomEvent.preventDefault(event);
            if(that.options.markers){
                mapFitAll(map, that.options.markers);
            }
        });
        return this._container;
    }
});

L.control.fitAll = function(options){
    return new L.Control.FitAll(options);
};

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
        // reformat 'time' column
        var time = record.time;
        var moment_time = moment(time);
        record = $.extend(true, {}, record);
        record.time = moment_time.format('YYYY-MM-DD [at] HH:mm:ss');

        // grab the record's attribute for each column
        for (var i = 0, len = columns.length; i < len; i++) {
            tr += cellWriter(columns[i], record);
        }
        // for action column
        var $span = $('<span></span>');
        for (var i = 0; i < button_templates.length; i++) {
            var button = button_templates[i];
            var $inner_button = $('<span></span>');
            $inner_button.addClass('row-action-icon')
            $inner_button.addClass(button.css_class);
            $inner_button.attr('title', button.name);
            var $button = $('<button></button>');
            $button.addClass('btn btn-primary row-action-container');
            $button.attr('title', button.name);
            $button.attr('onclick', button.handler + "('" + record.shake_id + "')");
            $button.append($inner_button);
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
    var $container = $(selector);
    var $header = $('thead tr', $container);
    var $th = $('<th></th>');
    var $a = $('<a></a>');
    $a.attr('href', '#');
    $a.text(header_name);
    $th.addClass('dynatable-head');
    $th.append($a);
    $header.append($th);
}
