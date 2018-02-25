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
 * Dynatable to store shake list
 */
var dynaTable;

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
        markers.zoomToShowLayer(marker, function () {
            var fitBoundsOption = {
                /*
                If we set the max zoom, we can limit the function so
                it doesn't get zoomed to maximum level.
                set this in combination with 'disableClusteringAtZoom'
                option when creating markerClusterGroup
                 */
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
 * use magic number 000 for url placeholder
 *
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
                var $a = $("<a></a>");
                $a.attr('href', pdf_url);
                if(!browser_identity().is_safari){
                    // it doesn't work in safari
                    $a.attr('target', '_blank');
                }
                $a.attr('rel', 'nofollow');
                if(browser_identity().is_firefox){
                    // preferred way to click a link programatically in
                    // firefox
                    // http://stackoverflow.com/questions/809057/how-do-i-programmatically-click-on-an-element-in-firefox
                    var clickEvent = new MouseEvent("click", {
                        "view": window,
                        "bubbles": true,
                        "cancelable": false
                    });
                    $a[0].dispatchEvent(clickEvent);
                }
                else{
                    $a[0].click();
                }
            }
        }).fail(function(e){
            if(e.status == 404){
                alert("No Report recorded for this event.");
            }
        });
    };
    return showReportHandler;
}

/**
 * Closure to create handler for downloadReport
 * @param {string} report_url A report url that contains shake_id placeholder
 * @return {function} Download the report based on shake_id
 */
function createDownloadReportHandler(report_url, language) {
    var downloadReportHandler = function (shake_id) {
        var url = report_url;
        // replace magic number 000 with shake_id
        url = url.replace('000', shake_id);
        SaveToDisk(url, shake_id+'-'+language+'.pdf');
    };
    return downloadReportHandler;
}

/**
 * Closure to create handler for downloadGrid
 * @param {string} grid_url A report url that contains shake_id placeholder
 * @return {function} Download the grid.xml based on shake_id
 */
function createDownloadGridHandler(grid_url) {
    var downloadGridHandler = function (shake_id) {
        var url = grid_url;
        // replace magic number 000 with shake_id
        url = url.replace('000', shake_id);
        var shake_list = dynaTable.settings.dataset.originalRecords;
        var shake_grid_exists;
        for(var i=0;i < shake_list.length;i++){
            if(shake_id == shake_list[i].shake_id){
                shake_grid_exists = shake_list[i].shake_grid_exists;
                break;
            }
        }
        if(shake_grid_exists){
            SaveToDisk(url, shake_id + '-grid.xml');
        }
        else{
            $.get(url);
            alert("Shake Grid doesn't exists. Trying to fetch it.");
        }
    };
    return downloadGridHandler;
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
        var form_filter_clone = form_filter.clone();
        var felt_input = form_filter_clone.find("#id_felt");
        if(felt_input.prop('checked') != true){
            felt_input.parent().empty();
        }
        var form_filter_query = form_filter_clone.serialize();
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
function clientFilter(data_input, min_date, max_date, min_magnitude, max_magnitude, felt_toggle){
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

        // felt
        var felt = feature.properties.felt;
        if(felt_toggle == true && felt != true){
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
            $("#id_maximum_magnitude", form_filter).val(),
            $("#id_felt", form_filter).prop("checked")
        );
        dataHandler(filtered);
    };
    return updateFilterHandler;
}

/**
 * Modify a given target text with relevant map filters descriptions
 * @param target {string} Jquery selector string for target element
 */
function modifyMapDescriptionsHandler(
        message_prefix,
        min_max_magnitude_message, min_magnitude_message, max_magnitude_message,
        start_end_date_message, start_date_message, end_date_message){
    return function(target) {
        var $target = $(target);

        var magnitude_string = "";
        var min_magnitude = $("#id_minimum_magnitude").val();
        var max_magnitude = $("#id_maximum_magnitude").val();
        var magnitude_map = {
            'min_magnitude': min_magnitude,
            'max_magnitude': max_magnitude
        };
        if (min_magnitude && max_magnitude) {
            magnitude_string = sprintf(min_max_magnitude_message, magnitude_map);
        }
        else if (min_magnitude) {
            magnitude_string = sprintf(min_magnitude_message, magnitude_map);
        }
        else if (max_magnitude) {
            magnitude_string = sprintf(max_magnitude_message, magnitude_map);
        }

        var date_string = '';
        var start_date = $("#id_start_date").val();
        var end_date = $("#id_end_date").val();
        if (start_date && end_date) {
            var start_moment = moment(start_date).format('LL');
            var end_moment = moment(end_date).format('LL');
            var moment_map = {
                'start_moment': start_moment,
                'end_moment': end_moment
            };
            date_string = sprintf(start_end_date_message, moment_map);
        }
        else if (start_date) {
            var start_moment = moment(start_date).format('LL');
            var moment_map = {
                'start_moment': start_moment
            };
            date_string = sprintf(start_date_message, moment_map);
        }
        else if (end_date) {
            var end_moment = moment(end_date).format('LL');
            var moment_map = {
                'end_moment': end_moment
            };
            date_string = sprintf(end_date_message, moment_map);
        }

        var description_map = {
            'magnitude': magnitude_string,
            'date': date_string
        };
        var description = sprintf(message_prefix, description_map);

        $target.text(description);
    }
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
 * Removes ':' from the text
 */
function modifySearchAndShowLabels(){
    $(".dynatable-per-page-label").text("Show");
    var $search_container = $(".dynatable-search");
    var $children = $search_container.children().detach();
    $search_container.text("Search").append($children);
}


/**
 * Dynatable related functions
 *
 */


/**
 * Create Action Writer based on button_templates
 *
 * @param {object} button_templates The list of dictionary containing name
 * and handler string
 * @return {function} a dynatable row function
 */
function createActionRowWriter(button_templates, date_format) {
    writer = function (rowIndex, record, columns, cellWriter) {
        var tr = '';
        // reformat 'time' column
        var time = record.time;
        var moment_time = moment(time);
        record = $.extend(true, {}, record);
        if(date_format === undefined){
            date_format = 'YYYY-MM-DD [at] HH:mm:ss';
        }
        //record.time = moment_time.format(date_format);
        record.time = moment_time.fromNow();

        // grab the record's attribute for each column
        for (var i = 0, len = columns.length; i < len; i++) {
            tr += cellWriter(columns[i], record);
        }
        // for action column
        var $span = $('<span></span>');
        for (var i = 0; i < button_templates.length; i++) {
            var button = button_templates[i];
            if(button.type == 'simple-button') {
                var $inner_button = $('<span></span>');
                $inner_button.addClass('row-action-icon');
                $inner_button.addClass(button.css_class);
                $inner_button.attr('title', button.name);
                var $button = $('<button></button>');
                $button.addClass('btn btn-primary row-action-container');
                $button.attr('title', button.name);
                $button.attr('onclick', button.handler + "('" + record.shake_id + "')");
                $button.append($inner_button);
                $span.append($button);
            }
            else if(button.type == 'dropdown'){
                var $button = $('<button></button>');
                $button.addClass('btn btn-primary dropdown-toggle row-action-container');
                $button.attr('title', button.name);
                $button.attr('data-toggle', 'dropdown');
                $button.attr('aria-haspopup', 'true');
                $button.attr('aria-expanded', 'false');
                var $inner_button = $('<span></span>');
                $inner_button.addClass('row-action-icon');
                $inner_button.addClass(button.css_class);
                $inner_button.attr(button.name);
                $button.append($inner_button);
                var $menu = $('<ul></ul>');
                $menu.addClass('dropdown-menu');
                for(var j=0;j < button.actions.length;j++){
                    var action = button.actions[j];
                    if(action.active && $.isFunction(action.active) && !action.active(record)){
                        continue;
                    }
                    var $li = $('<li></li>');
                    var $action = $('<a></a>');
                    if(action.href == undefined){
                        $action.attr('href', '#');
                    }
                    else if($.isFunction(action.href)){
                        $action.attr('href', action.href(record));
                    }

                    if(action.download && $.isFunction(action.download)){
                        $action.attr('download', action.download(record));
                    }

                    if(action.handler){
                        $action.attr('onclick', action.handler + "('" + record.shake_id + "')");
                    }

                    $action.text(action.text);
                    $li.append($action);
                    $menu.append($li);
                }
                var $group = $('<div></div>');
                $group.addClass('btn-group');
                $group.append($button);
                $group.append($menu);
                $span.append($group);
            }
        }
        tr += '<td>' + $span.html() + '</td>';

        return '<tr>' + tr + '</tr>';
    };
    return writer;
}


/**
 * Filter shake table to show only shake with 5.0 MMI for the previous month
 */
function filterRecentBigShake(){
    var $min_magnitude = $("#id_minimum_magnitude");
    var $start_date = $("#id_start_date");
    var now = moment();
    var start = now.clone().subtract(1, 'month');
    var format = 'YYYY-MM-DD';

    $("#event-filter .clear-filter").click();
    $min_magnitude.val(5);
    $start_date.val(start.format(format));
    $("#event-filter .submit-filter").click();
}


/**
 * Filter shake table to show only shake with 5.0 MMI below for the previous month
 */
function filterRecentSmallShake(){
    var $max_magnitude = $("#id_maximum_magnitude");
    var $start_date = $("#id_start_date");
    var now = moment();
    var start = now.clone().subtract(1, 'month');
    var format = 'YYYY-MM-DD';

    $("#event-filter .clear-filter").click();
    $max_magnitude.val(5);
    $start_date.val(start.format(format));
    $("#event-filter .submit-filter").click();
}

/**
 * Filter shake table to show only felt shake for the previous month
 */
function filterRecentFeltShake(){
    var $felt = $("#id_felt");
    $("#event-filter .clear-filter").click();
    $felt.prop("checked", true);
    $("#event-filter .submit-filter").click();
}
