/**
 * Created by lucernae on 7/18/16.
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
    var showEventHandler = function showEventHandler(id) {
        var marker = map_events[id];
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
 * use magic number for url placeholder
 *
 * @param {string} report_url A report url that contains event_id placeholder
 * @return {function} Open the report based on event_id in a new tab
 */
function createShowReportHandler(report_url) {
    var showReportHandler = function (id) {
        var url = report_url;
        // replace magic number
        function createFindWithId(id){
            return function (event) {
                return event.properties.id == id;
            }
        }
        var findWithId = createFindWithId(id);
        var feature = event_json.features.find(findWithId);
        var volcano_name = feature.properties.volcano.volcano_name;
        var event_time = feature.properties.event_time;
        var event_time_string = moment(event_time).format('YYYYMMDDHHmmssZZ');
        var task_status = feature.properties.task_status;
        if(task_status == 'PENDING'){
            alert("Report is currently being generated. Refresh this page later.");
            return;
        }
        else if(task_status == 'FAILED'){
            alert("Report failed to generate.");
            return;
        }
        url = url.replace('VOLCANOTEMPLATENAME', volcano_name)
            .replace('1234567890123456789', event_time_string);
        $.get(url, function (data) {
            if (data && data.report_map_url) {
                var pdf_url = data.report_map_url;
                OpenReportPDF(pdf_url);
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
 * Closure to create handler for downloadReport
 * use magic number for url placeholder
 *
 * @param {string} report_url A report url that contains event_id placeholder
 * @return {function} Open the report based on event_id in a new tab
 */
function createDownloadReportHandler(report_url) {
    var downloadReportHandler = function (id) {
        var url = report_url;
        // replace magic number 000 with shake_id
        function createFindWithId(id){
            return function (event) {
                return event.properties.id == id;
            }
        }
        var findWithId = createFindWithId(id);
        var feature = event_json.features.find(findWithId);
        var volcano_name = feature.properties.volcano.volcano_name;
        var event_time = feature.properties.event_time;
        var event_time_string = moment(event_time).format('YYYYMMDDHHmmssZZ');
        var report_filename = feature.properties.report_map_fileame;
        var task_status = feature.properties.task_status;
        if(task_status == 'PENDING'){
            alert("Report is currently being generated. Refresh this page later.");
            return;
        }
        else if(task_status == 'FAILED'){
            alert("Report failed to generate.");
            return;
        }
        url = url.replace('VOLCANOTEMPLATENAME', volcano_name)
            .replace('1234567890123456789', event_time_string);
        $.get(url, function (data) {
            if (data && data.report_map_url) {
                var pdf_url = data.report_map_url;
                SaveToDisk(pdf_url, report_filename);
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
        var time = record.event_time;
        var moment_time = moment(time).tz(record.event_time_zone_string);
        record = $.extend(true, {}, record);
        if(date_format === undefined){
            date_format = 'YYYY-MM-DD [at] HH:mm:ss ZZ';
        }
        record.event_time = moment_time.format(date_format);
        // record.event_time = moment_time.fromNow();

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
                $button.attr('onclick', button.handler + "('" + record.id + "')");
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
                        $action.attr('onclick', action.handler + "('" + record.id + "')");
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
