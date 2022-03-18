# coding=utf-8
"""Docstring here."""
from __future__ import print_function

from past.builtins import basestring
import os
import unittest

from django import test
from timeout_decorator import timeout_decorator

from realtime.app_settings import (
    ASH_EXPOSURES,
    ASH_REPORT_TEMPLATE_EN,
    ASH_LAYER_ORDER,
    FLOOD_EXPOSURE,
    FLOOD_REPORT_TEMPLATE_EN,
    FLOOD_LAYER_ORDER,
    REALTIME_GEONODE_ENABLE,
)
from realtime.tasks.headless.celery_app import app as headless_app
from realtime.tasks.headless.inasafe_wrapper import (
    get_keywords,
    run_analysis,
    generate_contour,
    run_multi_exposure_analysis,
    generate_report,
    get_generated_report,
    check_broker_connection,
    push_to_geonode,
)
from realtime.utils import celery_worker_connected

dir_path = os.path.dirname(os.path.realpath(__file__))

# Layers
earthquake_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'earthquake.asc')
shakemap_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'grid-use_ascii.tif')
ash_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'ash_fall.tif')
place_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'places.geojson')
aggregation_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'small_grid.geojson')
population_multi_fields_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'population_multi_fields.geojson')
buildings_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'buildings.geojson')
flood_layer_uri = os.path.join(
    dir_path, 'data', 'input_layers', 'flood_data.json')

# Map template
custom_map_template_basename = 'custom-inasafe-map-report-landscape'
custom_map_template = os.path.join(
    dir_path, 'data', custom_map_template_basename + '.qpt'
)


OUTPUT_DIRECTORY = os.environ.get(
    'INASAFE_OUTPUT_DIR', '/home/headless/outputs')


# minutes test timeout
LOCAL_TIMEOUT = 10 * 60


class TestHeadlessCeleryTask(test.SimpleTestCase):
    """Unit test for Headless Celery tasks."""

    def check_path(self, path):
        """Helper method to check a path."""
        message = 'Path %s is not exist' % path
        self.assertTrue(os.path.exists(path), message)

    def test_check_layer_exist(self):
        """Test if the layer exist."""
        self.check_path(dir_path)
        self.check_path(os.path.join(dir_path, 'data'))
        self.check_path(os.path.join(dir_path, 'data', 'input_layers'))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_get_keywords(self):
        """Test get_keywords task."""
        self.assertTrue(os.path.exists(place_layer_uri))
        result = get_keywords.delay(place_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(keywords['layer_purpose'], 'exposure')
        self.assertEqual(keywords['exposure'], 'place')

        self.assertTrue(os.path.exists(earthquake_layer_uri))
        result = get_keywords.delay(earthquake_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], 'hazard')
        self.assertEqual(keywords['hazard'], 'earthquake')
        time_zone = keywords['extra_keywords']['time_zone']
        self.assertEqual(time_zone, 'Asia/Jakarta')

        self.assertTrue(os.path.exists(aggregation_layer_uri))
        result = get_keywords.delay(aggregation_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], 'aggregation')

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_run_analysis(self):
        """Test run analysis."""
        # With aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in list(result['output'].items()):
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # No aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in list(result['output'].items()):
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    @unittest.skipIf(
        not all([os.path.exists(path) for path in ASH_EXPOSURES]),
        'Skip the unit test since there is no exposure data.')
    def test_exposure_data(self):
        """test_exposure_data for running real analysis.."""
        # Checking exposures for ash
        exposures = []
        for ash_exposure in ASH_EXPOSURES:
            exposure_keyword = get_keywords.delay(ash_exposure).get()
            self.assertEqual('exposure', exposure_keyword['layer_purpose'])
            message = (
                'There is duplicate exposure type in the ash exposures list: '
                '[%s]' % exposure_keyword['exposure'])
            self.assertNotIn(exposure_keyword['exposure'], exposures, message)
            exposures.append(exposure_keyword['exposure'])

        # Checking template and layer order for ash
        self.assertTrue(os.path.exists(ASH_REPORT_TEMPLATE_EN))
        for layer in ASH_LAYER_ORDER:
            if not layer.startswith('@'):
                self.assertTrue(
                    os.path.exists(layer), '%s is not exist' % layer)

        # Checking exposure for flood
        self.assertTrue(os.path.exists(FLOOD_EXPOSURE))
        # Checking template and layer order for flood
        self.assertTrue(os.path.exists(FLOOD_REPORT_TEMPLATE_EN))
        for layer in FLOOD_LAYER_ORDER:
            if not layer.startswith('@'):
                self.assertTrue(
                    os.path.exists(layer), '%s is not exist' % layer)

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_run_multi_exposure_analysis(self):
        """Test run multi_exposure analysis."""
        exposure_layer_uris = [
            place_layer_uri,
            buildings_layer_uri,
            population_multi_fields_layer_uri
        ]
        # With aggregation
        result_delay = run_multi_exposure_analysis.delay(
            earthquake_layer_uri, exposure_layer_uris, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        num_exposure_output = 0
        for key, layer_uri in list(result['output'].items()):
            if isinstance(layer_uri, basestring):
                self.assertTrue(os.path.exists(layer_uri))
                self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))
            elif isinstance(layer_uri, dict):
                num_exposure_output += 1
                for the_key, the_layer_uri in list(layer_uri.items()):
                    self.assertTrue(os.path.exists(the_layer_uri))
                    self.assertTrue(the_layer_uri.startswith(OUTPUT_DIRECTORY))
        # Check the number of per exposure output is the same as the number
        # of exposures
        self.assertEqual(num_exposure_output, len(exposure_layer_uris))

        # No aggregation
        result_delay = run_multi_exposure_analysis.delay(
            earthquake_layer_uri, exposure_layer_uris)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        num_exposure_output = 0
        for key, layer_uri in list(result['output'].items()):
            if isinstance(layer_uri, basestring):
                self.assertTrue(os.path.exists(layer_uri))
                self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))
            elif isinstance(layer_uri, dict):
                num_exposure_output += 1
                for the_key, the_layer_uri in list(layer_uri.items()):
                    self.assertTrue(os.path.exists(the_layer_uri))
                    self.assertTrue(the_layer_uri.startswith(OUTPUT_DIRECTORY))
        # Check the number of per exposure output is the same as the number
        # of exposures
        self.assertEqual(num_exposure_output, len(exposure_layer_uris))

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_generate_contour(self):
        """Test generate_contour task."""
        # Layer
        result_delay = generate_contour.delay(shakemap_layer_uri)
        result = result_delay.get()
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith(OUTPUT_DIRECTORY))
        self.assertTrue(os.path.exists(result), result + ' is not exist')

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_generate_report(self):
        """Test generate report for single analysis."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in list(result['output'].items()):
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['impact_analysis']

        # Generate reports
        async_result = generate_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(0, result['status'], result['message'])
        for key, products in list(result['output'].items()):
            for product_key, product_uri in list(products.items()):
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_generate_custom_report(self):
        """Test generate custom report for single analysis."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri,
            population_multi_fields_layer_uri,
            aggregation_layer_uri
        )
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in list(result['output'].items()):
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['impact_analysis']

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_map_template)
        result = async_result.get()
        self.assertEqual(0, result['status'], result['message'])
        product_keys = []
        for key, products in list(result['output'].items()):
            for product_key, product_uri in list(products.items()):
                product_keys.append(product_key)
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)
                if custom_map_template_basename == product_key:
                    print(product_uri)

        # Check if custom map template found.
        self.assertIn(custom_map_template_basename, product_keys)
        # Check if the default map reports are not found
        self.assertNotIn('inasafe-map-report-portrait', product_keys)
        self.assertNotIn('inasafe-map-report-landscape', product_keys)

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_get_generated_report(self):
        """Test get generated report task."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in list(result['output'].items()):
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['impact_analysis']

        # Get generated report (but it's not yet generated)
        async_result = get_generated_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(1, result['status'], result['message'])
        self.assertEqual({}, result['output'])

        # Generate reports
        async_result = generate_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(0, result['status'], result['message'])
        report_metadata = result['output']

        # Get generated report (now it's already generated)
        async_result = get_generated_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertDictEqual(report_metadata, result['output'])

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    def test_check_broker_connection(self):
        """Test check_broker_connection task."""
        async_result = check_broker_connection.delay()
        result = async_result.get()
        self.assertTrue(result)

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    @unittest.skipIf(
        not all([os.path.exists(path) for path in ASH_EXPOSURES]),
        'Skip the unit test since there is no exposure data.')
    def test_ash_analysis_real_exposures(self):
        """Test run ash analysis with real exposures."""
        result_delay = run_multi_exposure_analysis.delay(
            ash_layer_uri, ASH_EXPOSURES)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        num_exposure_output = 0
        for key, layer_uri in list(result['output'].items()):
            if isinstance(layer_uri, basestring):
                self.assertTrue(os.path.exists(layer_uri))
                self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))
            elif isinstance(layer_uri, dict):
                num_exposure_output += 1
                for the_key, the_layer_uri in list(layer_uri.items()):
                    self.assertTrue(os.path.exists(the_layer_uri))
                    self.assertTrue(the_layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['analysis_summary']

        # Generate reports
        layer_order = list(ASH_LAYER_ORDER)
        if 'ash_layer_path' in layer_order:
            hazard_index = layer_order.index('ash_layer_path')
            layer_order[hazard_index] = ash_layer_uri

        ash_report_template_basename = os.path.splitext(os.path.basename(
            ASH_REPORT_TEMPLATE_EN))[0]
        async_result = generate_report.delay(
            impact_analysis_uri, ASH_REPORT_TEMPLATE_EN, layer_order)
        result = async_result.get()
        self.assertEqual(0, result['status'], result['message'])
        product_keys = []
        for key, products in list(result['output'].items()):
            for product_key, product_uri in list(products.items()):
                product_keys.append(product_key)
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)
                if ash_report_template_basename == product_key:
                    print(product_uri)

        # Check if custom map template found.
        self.assertIn(ash_report_template_basename, product_keys)
        # Check if the default map reports are not found
        self.assertNotIn('inasafe-map-report-portrait', product_keys)
        self.assertNotIn('inasafe-map-report-landscape', product_keys)

    @timeout_decorator.timeout(LOCAL_TIMEOUT)
    @unittest.skipUnless(
        celery_worker_connected(headless_app, 'inasafe-headless'),
        'Headless Worker needs to be run')
    @unittest.skipIf(
        not os.path.exists(FLOOD_EXPOSURE),
        'Skip the unit test since there is no exposure data.')
    def test_flood_analysis_real_exposure(self):
        """Test run flood analysis with real exposures."""
        result_delay = run_analysis.delay(
            flood_layer_uri, FLOOD_EXPOSURE)
        result = result_delay.get()
        self.assertEqual(0, result['status'], result['message'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in list(result['output'].items()):
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['analysis_summary']

        # Generate reports
        layer_order = list(FLOOD_LAYER_ORDER)
        if 'flood_layer_path' in layer_order:
            hazard_index = layer_order.index('flood_layer_path')
            layer_order[hazard_index] = flood_layer_uri

        flood_report_template_basename = os.path.splitext(os.path.basename(
            FLOOD_REPORT_TEMPLATE_EN))[0]
        async_result = generate_report.delay(
            impact_analysis_uri, FLOOD_REPORT_TEMPLATE_EN, layer_order)
        result = async_result.get()
        self.assertEqual(0, result['status'], result['message'])
        product_keys = []
        for key, products in list(result['output'].items()):
            for product_key, product_uri in list(products.items()):
                product_keys.append(product_key)
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)
                if flood_report_template_basename == product_key:
                    print(product_uri)

        # Check if custom map template found.
        self.assertIn(flood_report_template_basename, product_keys)
        # Check if the default map reports are not found
        self.assertNotIn('inasafe-map-report-portrait', product_keys)
        self.assertNotIn('inasafe-map-report-landscape', product_keys)

    @unittest.skipIf(not REALTIME_GEONODE_ENABLE, 'GeoNode push is disabled.')
    def test_push_tif_to_geonode(self):
        """Test push tif layer to geonode functionality."""
        async_result = push_to_geonode.delay(shakemap_layer_uri)
        result = async_result.get()
        self.assertEqual(result['status'], 0, result['message'])

    @unittest.skipIf(not REALTIME_GEONODE_ENABLE, 'GeoNode push is disabled.')
    def test_push_geojson_to_geonode(self):
        """Test push geojson layer to geonode functionality."""
        async_result = push_to_geonode.delay(flood_layer_uri)
        result = async_result.get()
        self.assertEqual(result['status'], 0, result['message'])
