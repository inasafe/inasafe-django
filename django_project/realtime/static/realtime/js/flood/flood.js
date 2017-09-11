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
 * Event layer being displayed on the map
 */
var event_layer;

/**
 * Layer grouping control on map
 */
var layer_control;

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
 * Show hazard features on the map for clicked event id
 * @param event_features_url Url pattern for the event
 * @returns {showFeaturesHandler} handler function
 */
function createShowFeaturesHandler(event_features_url){
    var showFeaturesHandler = function (event_id) {
        var url = event_features_url;
        // replace placeholder 0000000000-6-rw with event_id
        url = url.replace('0000000000-6-rw', event_id);
        var map_id = $(map._container).attr("id");
        $.get(url, function (data) {
            if(data){
                var layer_control_id = 'flood-event-overlay';
                if(event_layer){
                    // programmatically disable active layer
                    $("#"+layer_control_id).parent().siblings('input:checked').click();
                    layer_control.removeLayer(event_layer);
                }
                var style_classes = {
                    1: {
                        stroke: true,
                        color: "#000",
                        weight: 2,
                        fillColor: "#bdc5f7",
                        fillOpacity: 0.8
                    },
                    2: {
                        stroke: true,
                        color: "#000",
                        weight: 2,
                        fillColor: "#fffe73",
                        fillOpacity: 0.8
                    },
                    3: {
                        stroke: true,
                        color: "#000",
                        weight: 2,
                        fillColor: "#fea865",
                        fillOpacity: 0.8
                    },
                    4: {
                        stroke: true,
                        color: "#000",
                        weight: 2,
                        fillColor: "#da6c7b",
                        fillOpacity: 0.8
                    }
                };
                event_layer = L.geoJson(data,{
                    style: function(feature){
                        return style_classes[feature.properties.hazard_data];
                    },
                    filter: function(feature){
                        if(feature.properties){
                            var props = feature.properties;
                            var hazard_data = props.hazard_data;
                            return hazard_data >= 1;
                        }
                        else {
                            return false;
                        }
                    },
                    onEachFeature: function(feature, layer) {
                        // Set popup content
                        if (feature.properties) {
                            var props = feature.properties;
                            var popup_content = window.JST.popup_content(props);
                            layer.bindPopup(popup_content);
                        }
                    }
                });
                layer_control.addOverlay(
                    event_layer, '<span id="'+layer_control_id+'"></span>Flood Event');
                // programmatically enable the layer
                event_layer.addTo(map);

                var fitBoundsOption = {
                    maxZoom: 15,
                    pan: {
                        animate: true,
                        duration: 0.5
                    },
                    zoom: {
                        animate: true,
                        duration: 0.5
                    }
                };
                map.fitBounds(event_layer.getBounds(), fitBoundsOption);

                // Deselect row in table
                var $table = $("#realtime-table");
                $table.find("tr.success").removeClass('success');
                // Select row
                $table.find("td:contains("+event_id+")").closest('tr').addClass('success');
            }
        }).fail(function(e){
            console.log(e);
            if(e.status == 404){
                alert("No features for this event.");
            }
        });
    };
    return showFeaturesHandler;
}

/**
 * Closure to create handler for showReport
 * use url placeholder
 *
 * @param {string} report_url A report url that contains event_id placeholder
 * @return {function} Open the report based on event_id in a new tab
 */
function createShowReportHandler(report_url) {
    var showReportHandler = function (event_id) {
        var url = report_url;
        // replace placeholder with event_id
        url = url.replace('0000000000-6-rw', event_id);
        $.get(url, function (data) {
            if (data && data.impact_report) {
                var pdf_url = data.impact_report;
                var $a = $("<a></a>");
                $a.attr('href', pdf_url);
                if(!browser_identity().is_safari){
                    // it doesn't work in safari
                    $a.attr('target', '_blank');
                }
                $a.attr('rel', 'nofollow');
                $a[0].click();
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
 * Closure to create handler for showImpactMap
 * use magic number 000 for url placeholder
 *
 * @param {string} report_url A report url that contains shake_id placeholder
 * @return {function} Open the report based on shake_id in a new tab
 */
function createShowImpactMapHandler(report_url) {
    var showImpactMapHandler = function (event_id) {
        var url = report_url;
        // replace placeholder with event_id
        url = url.replace('0000000000-6-rw', event_id);
        $.get(url, function (data) {
            if (data && data.impact_map) {
                var pdf_url = data.impact_map;
                var $a = $("<a></a>");
                $a.attr('href', pdf_url);
                if(!browser_identity().is_safari){
                    // it doesn't work in safari
                    $a.attr('target', '_blank');
                }
                $a.attr('rel', 'nofollow');
                $a[0].click();
            }
        }).fail(function(e){
            console.log(e);
            if(e.status == 404){
                alert("No Report recorded for this event.");
            }
        });
    };
    return showImpactMapHandler;
}

/**
 * Closure to create handler for downloadReport
 * @param {string} report_url A report url that contains shake_id placeholder
 * @return {function} Download the impact map based on event_id
 */
function createDownloadImpactMapHandler(report_url) {
    var downloadImpactMapHandler = function (event_id) {
        var url = report_url;
        // replace magic number 0000000000-6-rw with event_id
        url = url.replace('0000000000-6-rw', event_id);
        $.get(url, function (data) {
            if (data && data.impact_map) {
                var pdf_url = data.impact_map;
                SaveToDisk(pdf_url, data.event_id+'-'+data.language+'.pdf');
            }
        }).fail(function(e){
            console.log(e);
            if(e.status == 404){
                alert("No Report recorded for this event.");
            }
        });
    };
    return downloadImpactMapHandler;
}

/**
 * Closure to create handler for downloadHazardLayer
 * @return {function} Download the hazard layer based on event_id
 */
function createDownloadHazardLayerHandler() {
    var downloadHazardLayerHandler = function (event_id) {
        var event = undefined;
        for(var i=0;i < event_json.length;i++){
            event = event_json[i];
            if(event_id == event.event_id){
                break;
            }
        }

        if(event == undefined){
            alert("Event not found");
            return;
        }

        var url = event.hazard_layer;
        SaveToDisk(url, event.event_id + '-hazard.zip');
    };
    return downloadHazardLayerHandler;
}

/**
 * Create update filter handler based on url and dataHandler
 * @param {string} url URL to send filtered data
 * @param {function} dataHandler Function to handle retrieved data
 * @return {Function} Update handler function
 */
function createUpdateFilterHandler(url, form_filter, dataHandler) {
    var updateFilterHandler = function (e, reset) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        var form_filter_query = form_filter.serialize();
        $.get(url + "?" + form_filter_query, dataHandler);
    };
    return updateFilterHandler;
}

/**
 * filter a given geojson input in client side
 * @param data_input {{}} a geo json collections
 * @param min_date {string} date formattable string
 * @param max_date {string} date formattable string
 * @param min_people_affected {string} float string
 * @param max_people_affected {string} float string
 * @return {{features: Array, type: *}}
 */
function clientFilter(data_input, min_date, max_date, min_people_affected, max_people_affected, min_boundary_flooded, max_boundary_flooded){
    var filtered_features = [];
    var features = data_input;
    for(var i=0;i<features.length;i++){
        var feature = features[i];

        // time filter
        var time = new Date(Date.parse(feature.time));
        if(min_date && time < new Date(Date.parse(min_date))){
            continue
        }

        if(max_date && time > new Date(Date.parse(max_date))){
            continue
        }

        // people affected
        var people_affected = feature.total_affected;
        if(min_people_affected && people_affected < parseFloat(min_people_affected)){
            continue
        }

        if(max_people_affected && people_affected > parseFloat(max_people_affected)){
            continue
        }

        // boundary flooded
        var boundary_flooded = feature.boundary_flooded;
        if(min_boundary_flooded && boundary_flooded < parseFloat(min_boundary_flooded)){
            continue
        }

        if(max_boundary_flooded && boundary_flooded > parseFloat(max_boundary_flooded)){
            continue
        }

        // filtered
        filtered_features.push(feature);
    }
    return filtered_features;
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
function createClientUpdateFilterHandler(url, form_filter, dataHandler) {
    var updateFilterHandler = function (e, reset) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        // filter by bounds
        var filtered = event_json;
        filtered = clientFilter(
            filtered,
            $("#id_start_date", form_filter).val(),
            $("#id_end_date", form_filter).val(),
            $("#id_min_people_affected", form_filter).val(),
            $("#id_max_people_affected", form_filter).val(),
            $("#id_min_boundary_flooded", form_filter).val(),
            $("#id_max_boundary_flooded", form_filter).val()
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

    var people_affected_string = "";
    var min_people_affected = $("#id_min_people_affected").val();
    var max_people_affected = $("#id_max_people_affected").val();
    var boundary_flooded_string = "";
    var min_boundary_flooded = $("#id_min_boundary_flooded").val();
    var max_boundary_flooded = $("#id_max_boundary_flooded").val();
    if(min_people_affected && max_people_affected){
        people_affected_string = 'with people affected between '+min_people_affected+' and '+max_people_affected;
    }
    else if(min_people_affected){
        people_affected_string = 'with people affected greater or equal than '+min_people_affected;
    }
    else if(max_people_affected){
        people_affected_string = 'with people affected less or equal than '+max_people_affected;
    }

    if(min_boundary_flooded && max_boundary_flooded){
        boundary_flooded_string = 'with RW flooded between '+min_boundary_flooded+' and '+max_boundary_flooded;
    }
    else if(min_boundary_flooded){
        boundary_flooded_string = 'with RW flooded greater or equal than '+min_boundary_flooded;
    }
    else if(max_boundary_flooded){
        boundary_flooded_string = 'with RW flooded less or equal than '+max_boundary_flooded;
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
    var description = 'Flood events';
    if(people_affected_string){
        description+=' '+people_affected_string;
    }
    if(boundary_flooded_string){
        description+=' '+boundary_flooded_string;
    }
    if(date_string){
        description+=' '+date_string;
    }
    $target.text(description);
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
        record.time = moment_time.format(date_format);

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
                $button.attr('onclick', button.handler + "('" + record.event_id + "')");
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
                $inner_button.attr('title', button.name);
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
                        $action.attr('onclick', action.handler + "('" + record.event_id + "')");
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

