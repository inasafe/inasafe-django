# coding=utf-8
"""Docstring here."""

import os
import unittest
from realtime.tasks.headless.inasafe_wrapper import (
    get_keywords,
    run_analysis,
    generate_contour,
    run_multi_exposure_analysis,
    generate_report,
    get_generated_report,
    check_broker_connection,
)


common_test_data_path = os.environ.get('COMMON_TEST_DATA')

dir_path = common_test_data_path

# Layers
earthquake_layer_uri = os.path.join(
    dir_path, 'input_layers', 'earthquake.asc')
shakemap_layer_uri = os.path.join(
    dir_path, 'input_layers', 'grid-use_ascii.tif')
place_layer_uri = os.path.join(
    dir_path, 'input_layers', 'places.geojson')
aggregation_layer_uri = os.path.join(
    dir_path, 'input_layers', 'small_grid.geojson')
population_multi_fields_layer_uri = os.path.join(
    dir_path, 'input_layers', 'population_multi_fields.geojson')
buildings_layer_uri = os.path.join(
    dir_path, 'input_layers', 'buildings.geojson')

# Map template
custom_map_template_basename = 'custom-inasafe-map-report-landscape'
custom_map_template = os.path.join(
    dir_path, custom_map_template_basename + '.qpt'
)

OUTPUT_DIRECTORY = os.environ.get('INASAFE_OUTPUT_DIR')


class TestHeadlessCeleryTask(unittest.TestCase):
    """Unit test for Headless Celery tasks."""

    def test_get_keywords(self):
        """Test get_keywords task."""
        self.assertTrue(os.path.exists(place_layer_uri))
        result = get_keywords.delay(place_layer_uri)
        keywords = result.get()
        self.assertIsNotNone(keywords)
        self.assertEqual(
            keywords['layer_purpose'], 'exposure')
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

    def test_run_analysis(self):
        """Test run analysis."""
        # With aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # No aggregation
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

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
        self.assertEqual(0, result['status'])
        self.assertLess(0, len(result['output']))
        num_exposure_output = 0
        for key, layer_uri in result['output'].items():
            if isinstance(layer_uri, basestring):
                self.assertTrue(os.path.exists(layer_uri))
                self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))
            elif isinstance(layer_uri, dict):
                num_exposure_output += 1
                for the_key, the_layer_uri in layer_uri.items():
                    self.assertTrue(os.path.exists(the_layer_uri))
                    self.assertTrue(the_layer_uri.startswith(OUTPUT_DIRECTORY))
        # Check the number of per exposure output is the same as the number
        # of exposures
        self.assertEqual(num_exposure_output, len(exposure_layer_uris))

        # No aggregation
        result_delay = run_multi_exposure_analysis.delay(
            earthquake_layer_uri, exposure_layer_uris)
        result = result_delay.get()
        self.assertEqual(0, result['status'])
        self.assertLess(0, len(result['output']))
        num_exposure_output = 0
        for key, layer_uri in result['output'].items():
            if isinstance(layer_uri, basestring):
                self.assertTrue(os.path.exists(layer_uri))
                self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))
            elif isinstance(layer_uri, dict):
                num_exposure_output += 1
                for the_key, the_layer_uri in layer_uri.items():
                    self.assertTrue(os.path.exists(the_layer_uri))
                    self.assertTrue(the_layer_uri.startswith(OUTPUT_DIRECTORY))
        # Check the number of per exposure output is the same as the number
        # of exposures
        self.assertEqual(num_exposure_output, len(exposure_layer_uris))

    def test_generate_contour(self):
        """Test generate_contour task."""
        # Layer
        result_delay = generate_contour.delay(shakemap_layer_uri)
        result = result_delay.get()
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith(OUTPUT_DIRECTORY))
        self.assertTrue(os.path.exists(result), result + ' is not exist')

    def test_generate_report(self):
        """Test generate report for single analysis."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['impact_analysis']

        # Generate reports
        async_result = generate_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(0, result['status'])
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)

    def test_generate_custom_report(self):
        """Test generate custom report for single analysis."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri,
            population_multi_fields_layer_uri,
            aggregation_layer_uri
        )
        result = result_delay.get()
        self.assertEqual(0, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['impact_analysis']

        # Generate reports
        async_result = generate_report.delay(
            impact_analysis_uri, custom_map_template)
        result = async_result.get()
        self.assertEqual(0, result['status'])
        product_keys = []
        for key, products in result['output'].items():
            for product_key, product_uri in products.items():
                product_keys.append(product_key)
                message = 'Product %s is not found in %s' % (
                    product_key, product_uri)
                self.assertTrue(os.path.exists(product_uri), message)
                if custom_map_template_basename == product_key:
                    print product_uri

        # Check if custom map template found.
        self.assertIn(custom_map_template_basename, product_keys)
        # Check if the default map reports are not found
        self.assertNotIn('inasafe-map-report-portrait', product_keys)
        self.assertNotIn('inasafe-map-report-landscape', product_keys)

    def test_get_generated_report(self):
        """Test get generated report task."""
        # Run analysis first
        result_delay = run_analysis.delay(
            earthquake_layer_uri, place_layer_uri, aggregation_layer_uri)
        result = result_delay.get()
        self.assertEqual(0, result['status'])
        self.assertLess(0, len(result['output']))
        for key, layer_uri in result['output'].items():
            self.assertTrue(os.path.exists(layer_uri))
            self.assertTrue(layer_uri.startswith(OUTPUT_DIRECTORY))

        # Retrieve impact analysis uri
        impact_analysis_uri = result['output']['impact_analysis']

        # Get generated report (but it's not yet generated)
        async_result = get_generated_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(1, result['status'])
        self.assertEqual({}, result['output'])

        # Generate reports
        async_result = generate_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(
            0, result['status'])
        report_metadata = result['output']

        # Get generated report (now it's already generated)
        async_result = get_generated_report.delay(impact_analysis_uri)
        result = async_result.get()
        self.assertEqual(0, result['status'])
        self.assertDictEqual(report_metadata, result['output'])

    def test_check_broker_connection(self):
        """Test check_broker_connection task."""
        async_result = check_broker_connection.delay()
        result = async_result.get()
        self.assertTrue(result)
