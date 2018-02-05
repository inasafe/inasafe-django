# coding=utf-8
"""Task for InaSAFE Headless."""
import logging

from realtime.tasks.headless.celery_app import app

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE Headless')

@app.task(name='inasafe.headless.tasks.get_keywords', queue='inasafe-headless')
def get_keywords(layer_uri, keyword=None):
    """Get keywords from a layer.

    :param layer_uri: Uri to layer.
    :type layer_uri: basestring

    :param keyword: The key of keyword that want to be read. If None, return
        all keywords in dictionary.
    :type keyword: basestring

    :returns: Dictionary of keywords or value of key as string.
    :rtype: dict, basestring
    """
    LOGGER.info('proxy tasks')
    pass


@app.task(name='inasafe.headless.tasks.run_analysis', queue='inasafe-headless')
def run_analysis(
        hazard_layer_uri,
        exposure_layer_uri,
        aggregation_layer_uri=None,
        crs=None
):
    """Run analysis.

    :param hazard_layer_uri: Uri to hazard layer.
    :type hazard_layer_uri: basestring

    :param exposure_layer_uri: Uri to exposure layer.
    :type exposure_layer_uri: basestring

    :param aggregation_layer_uri: Uri to aggregation layer.
    :type aggregation_layer_uri: basestring

    :param crs: CRS for the analysis (if the aggregation is not set).
    :param crs: QgsCoordinateReferenceSystem

    :returns: A dictionary of output's layer key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'outputs': {
            'output_layer_key_1': 'output_layer_path_1',
            'output_layer_key_2': 'output_layer_path_2',
        }
    }
    """
    LOGGER.info('proxy tasks')
    pass


@app.task(
    name='inasafe.headless.tasks.run_multi_exposure_analysis',
    queue='inasafe-headless')
def run_multi_exposure_analysis(
        hazard_layer_uri,
        exposure_layer_uris,
        aggregation_layer_uri=None,
        crs=None
):
    """Run analysis for multi exposure.

    :param hazard_layer_uri: Uri to hazard layer.
    :type hazard_layer_uri: basestring

    :param exposure_layer_uris: List of uri to exposure layers.
    :type exposure_layer_uris: list

    :param aggregation_layer_uri: Uri to aggregation layer.
    :type aggregation_layer_uri: basestring

    :param crs: CRS for the analysis (if the aggregation is not set).
    :param crs: QgsCoordinateReferenceSystem

    :returns: A dictionary of output's layer key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'outputs': {
            'exposure_1': {
                'output_layer_key_11': 'output_layer_path_11',
                'output_layer_key_12': 'output_layer_path_12',
            },
            'exposure_2': {
                'output_layer_key_21': 'output_layer_path_21',
                'output_layer_key_22': 'output_layer_path_22',
            },
            'multi_exposure_output_layer_key_1':
                'multi_exposure_output_layer_path_1',
            'multi_exposure_output_layer_key_2':
                'multi_exposure_output_layer_path_2',
        }
    }
    """
    LOGGER.info('proxy tasks')
    pass


@app.task(
    name='inasafe.headless.tasks.generate_report', queue='inasafe-headless')
def generate_report(impact_layer_uri, custom_report_template_uri=None):
    """Generate report based on impact layer uri.

    :param impact_layer_uri: The uri to impact layer (one of them).
    :type impact_layer_uri: basestring

    :param custom_report_template_uri: The uri to report template.
    :type custom_report_template_uri: basestring

    :returns: A dictionary of output's report key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'output': {
            'html_product_tag': {
                'action-checklist-report': u'path',
                'analysis-provenance-details-report': u'path',
                'impact-report': u'path',
            },
            'pdf_product_tag': {
                'action-checklist-pdf': u'path',
                'analysis-provenance-details-report-pdf': u'path',
                'impact-report-pdf': u'path',
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            },
            'qpt_product_tag': {
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            }
        },
    }

    """
    LOGGER.info('proxy tasks')
    pass


@app.task(
    name='inasafe.headless.tasks.get_generated_report',
    queue='inasafe-headless')
def get_generated_report(impact_layer_uri):
    """Get generated report for impact layer uri

    :param impact_layer_uri: The uri to impact layer (one of them).
    :type impact_layer_uri: basestring

    :returns: A dictionary of output's report key and Uri with status and
        message.
    :rtype: dict

    The output format will be:
    output = {
        'status': 0,
        'message': '',
        'output': {
            'html_product_tag': {
                'action-checklist-report': u'path',
                'analysis-provenance-details-report': u'path',
                'impact-report': u'path',
            },
            'pdf_product_tag': {
                'action-checklist-pdf': u'path',
                'analysis-provenance-details-report-pdf': u'path',
                'impact-report-pdf': u'path',
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            },
            'qpt_product_tag': {
                'inasafe-map-report-landscape': u'path',
                'inasafe-map-report-portrait': u'path',
            }
        },
    }

    """
    LOGGER.info('proxy tasks')
    pass


@app.task(
    name='inasafe.headless.tasks.generate_contour', queue='inasafe-headless')
def generate_contour(layer_uri):
    """Create contour from raster layer_uri to output_uri

    :param layer_uri: The shakemap raster layer uri.
    :type layer_uri: basestring

    :returns: The output layer uri if success
    :rtype: basestring

    It will put the contour layer to
    contour_[input_file_name]_[current_datetime]/[input_file_name].shp

    current_datetime format: 25January2018_09h25-17.597909
    """
    LOGGER.info('proxy tasks')
    pass


@app.task(
    name='inasafe.headless.tasks.check_broker_connection',
    queue='inasafe-headless')
def check_broker_connection():
    """Only returns true if broker is connected

    :return: True
    """
    LOGGER.info('proxy tasks')
    return True
