
# Copyright (C) 2019-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# esp-service Software in commercial settings.
#
# END COPYRIGHT
"""
Tests for RepresentationServiceAdapters
"""

from unittest import TestCase

from leaf_common.candidates.representation_types import RepresentationType

from esp_service.adapters.factory.representation_service_adapter_factory import RepresentationServiceAdapterFactory


class TestAdapters(TestCase):
    """
    Tests for RepresentationServiceAdapters
    """

    def test_valid_file_types(self):
        """
        Verify valid file extensions for each representation and ensure invalid ones rejected
        """
        adapter = RepresentationServiceAdapterFactory.create_adapter_from_type(RepresentationType.KerasNN)
        self.assertTrue(adapter.is_valid_file_type('test.h5'))
        self.assertFalse(adapter.is_valid_file_type('test.rules'))
        self.assertFalse(adapter.is_valid_file_type('test.pickle'))

        adapter = RepresentationServiceAdapterFactory.create_adapter_from_type(RepresentationType.NNWeights)
        self.assertTrue(adapter.is_valid_file_type('test.json'))
        self.assertFalse(adapter.is_valid_file_type('test.h5'))

        adapter = RepresentationServiceAdapterFactory.create_adapter_from_type(RepresentationType.RuleBased)
        self.assertTrue(adapter.is_valid_file_type('test.json'))

        adapter = RepresentationServiceAdapterFactory.create_adapter_from_type(RepresentationType.Structure)
        self.assertTrue(adapter.is_valid_file_type('test.json'))

    def test_unknown_file_type(self):
        """
        Verify behavior when garbage file type passed
        """
        adapter = RepresentationServiceAdapterFactory.create_adapter_from_type(RepresentationType.RuleBased)
        self.assertFalse(adapter.is_valid_file_type('test.rules'))

        adapter = RepresentationServiceAdapterFactory.create_adapter_from_type(RepresentationType.KerasNN)
        self.assertFalse(adapter.is_valid_file_type('test.txt'))

        adapter = RepresentationServiceAdapterFactory.create_adapter_from_type(RepresentationType.Structure)
        self.assertFalse(adapter.is_valid_file_type('test.structure'))
