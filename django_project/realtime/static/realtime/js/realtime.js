/**
 * Author: Rizky Maulana Nugraha (lana.pcfre@gmail.com)
 * Description:
 * This file contains methods related directly to realtime.
 * It follows Airbnb Javascript style guide (https://github.com/airbnb/javascript)
 * and JSDoc for the documentation.
 */

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
        maxZoom: 18,
        continuousWorld: true
    });
    return base_map;
}

/**
 * Detect Safari browser
 *
 * @return {Object} to check the identity
 */
function browser_identity(){
    var is_chrome = navigator.userAgent.indexOf('Chrome') > -1;
    var is_explorer = navigator.userAgent.indexOf('MSIE') > -1;
    var is_firefox = navigator.userAgent.indexOf('Firefox') > -1;
    var is_safari = navigator.userAgent.indexOf("Safari") > -1;
    var is_opera = navigator.userAgent.toLowerCase().indexOf("op") > -1;
    if ((is_chrome)&&(is_safari)) {is_safari=false;}
    if ((is_chrome)&&(is_opera)) {is_chrome=false;}
    return {
        is_chrome: is_chrome,
        is_explorer: is_explorer,
        is_firefox: is_firefox,
        is_safari: is_safari,
        is_opera: is_opera
    };
}

/**
 * A script to download link to disk.
 * Source: http://stackoverflow.com/questions/3077242/force-download-a-pdf-link-using-javascript-ajax-jquery/29266135#29266135
 * @param fileURL {string} the file url
 * @param fileName {string} filename to save
 */
function SaveToDisk(fileURL, fileName) {
    if (!window.ActiveXObject) {
        // emulate button click on a element
        var save = document.createElement('a');
        save.href = fileURL;
        if(!browser_identity().is_safari){
            // doesn't work in safari
            save.target = '_blank';
        }
        save.download = fileName || 'unknown';

        var evt = new MouseEvent('click', {
            'view': window,
            'bubbles': true,
            'cancelable': false
        });
        save.dispatchEvent(evt);

        // (window.URL || window.webkitURL).revokeObjectURL(save.href);
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
                var markers;
                if($.isFunction(that.options.markers)){
                    markers = that.options.markers();
                }
                else {
                    markers = that.options.markers;
                }

                mapFitAll(map, markers);
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
