# -*- coding: utf-8 -*-
import pandas
import numpy
import io
import sys
import unittest
import unittest.mock
import tempfile
from pandas.util.testing import assert_frame_equal
import os
import copy
import json
from datetime import datetime

sys.path.append("..")
import nPYc
import warnings
from nPYc.enumerations import VariableType, AssayRole, SampleType, QuantificationType, CalibrationMethod


class test_nmrtargeteddataset_full_brukerxml_load(unittest.TestCase):
    """
	Test all steps of loadBrukerXMLDataset and parameters input: find and read Bruker XML files, filter features by units, format sample and feature metadata, initialise expectedConcentration and calibration, apply limits of quantification.
	Underlying functions tested independently
	Test BrukerQuant-UR until BrukerBI-LISA is definitive
	"""

    def setUp(self):
        # 49 features, 9 samples, BrukerQuant-UR
        self.datapathQuantUR = os.path.join('..', '..', 'npc-standard-project', 'Raw_Data', 'nmr', 'UnitTest1')
        # Expected TargetedDataset
        # Do not check sampleMetadata['Path']
        self.expectedQuantUR = dict()
        self.expectedQuantUR['sampleMetadata'] = pandas.DataFrame(
            {'Sample File Name': ['UnitTest1_Urine_Rack1_SLL_270814/10',
                                  'UnitTest1_Urine_Rack1_SLL_270814/20',
                                  'UnitTest1_Urine_Rack1_SLL_270814/30',
                                  'UnitTest1_Urine_Rack1_SLL_270814/40',
                                  'UnitTest1_Urine_Rack1_SLL_270814/50',
                                  'UnitTest1_Urine_Rack1_SLL_270814/60',
                                  'UnitTest1_Urine_Rack1_SLL_270814/70',
                                  'UnitTest1_Urine_Rack1_SLL_270814/80',
                                  'UnitTest1_Urine_Rack1_SLL_270814/90'],
             'Sample Base Name': ['UnitTest1_Urine_Rack1_SLL_270814/10',
                                  'UnitTest1_Urine_Rack1_SLL_270814/20',
                                  'UnitTest1_Urine_Rack1_SLL_270814/30',
                                  'UnitTest1_Urine_Rack1_SLL_270814/40',
                                  'UnitTest1_Urine_Rack1_SLL_270814/50',
                                  'UnitTest1_Urine_Rack1_SLL_270814/60',
                                  'UnitTest1_Urine_Rack1_SLL_270814/70',
                                  'UnitTest1_Urine_Rack1_SLL_270814/80',
                                  'UnitTest1_Urine_Rack1_SLL_270814/90'],
             'expno': [10, 20, 30, 40, 50, 60, 70, 80, 90],
             'Acquired Time': [datetime(2017, 8, 23, 19, 39, 1),
                               datetime(2017, 8, 23, 19, 56, 55),
                               datetime(2017, 8, 23, 20, 14, 50),
                               datetime(2017, 8, 23, 20, 32, 35),
                               datetime(2017, 8, 23, 20, 50, 9),
                               datetime(2017, 8, 23, 21, 7, 48),
                               datetime(2017, 8, 23, 21, 25, 38),
                               datetime(2017, 8, 23, 21, 42, 57),
                               datetime(2017, 8, 23, 22, 00, 53)],
             'Run Order': [0, 1, 2, 3, 4, 5, 6, 7, 8],
             'AssayRole': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                           numpy.nan],
             'SampleType': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                            numpy.nan],
             'Dilution': [100, 100, 100, 100, 100, 100, 100, 100, 100],
             'Correction Batch': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                  numpy.nan, numpy.nan],
             'Sample ID': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                           numpy.nan],
             'Exclusion Details': [None, None, None, None, None, None, None, None, None],
             'Batch': [1, 1, 1, 1, 1, 1, 1, 1, 1]})
        self.expectedQuantUR['sampleMetadata']['Metadata Available'] = False

        self.expectedQuantUR['featureMetadata'] = pandas.DataFrame({'Feature Name': ['Dimethylamine',
                                                                                     'Trimethylamine',
                                                                                     '1-Methylhistidine',
                                                                                     '2-Furoylglycine',
                                                                                     '4-Aminobutyric acid',
                                                                                     'Alanine',
                                                                                     'Arginine',
                                                                                     'Betaine',
                                                                                     'Creatine',
                                                                                     'Glycine',
                                                                                     'Guanidinoacetic acid',
                                                                                     'Methionine',
                                                                                     'N,N-Dimethylglycine',
                                                                                     'Sarcosine',
                                                                                     'Taurine',
                                                                                     'Valine',
                                                                                     'Benzoic acid',
                                                                                     'D-Mandelic acid',
                                                                                     'Hippuric acid',
                                                                                     'Acetic acid',
                                                                                     'Citric acid',
                                                                                     'Formic acid',
                                                                                     'Fumaric acid',
                                                                                     'Imidazole',
                                                                                     'Lactic acid',
                                                                                     'Proline betaine',
                                                                                     'Succinic acid',
                                                                                     'Tartaric acid',
                                                                                     'Trigonelline',
                                                                                     '2-Methylsuccinic acid',
                                                                                     '2-Oxoglutaric acid',
                                                                                     '3-Hydroxybutyric acid',
                                                                                     'Acetoacetic acid',
                                                                                     'Acetone',
                                                                                     'Oxaloacetic acid',
                                                                                     'Pyruvic acid',
                                                                                     '1-Methyladenosine',
                                                                                     '1-Methylnicotinamide',
                                                                                     'Adenosine',
                                                                                     'Allantoin',
                                                                                     'Allopurinol',
                                                                                     'Caffeine',
                                                                                     'Inosine',
                                                                                     'D-Galactose',
                                                                                     'D-Glucose',
                                                                                     'D-Lactose',
                                                                                     'D-Mannitol',
                                                                                     'D-Mannose',
                                                                                     'Myo-Inositol'],
                                                                    'Lower Reference Percentile': [2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5,
                                                                                                   2.5, 2.5, 2.5, 2.5,
                                                                                                   2.5],
                                                                    'Lower Reference Value': ['-', '-', '-', '-', '-',
                                                                                              11, '-', 9, '-', 38, '-',
                                                                                              '-', '-', '-',
                                                                                              '-', '-', '-', 2, '-',
                                                                                              '-', '-', '-', '-', '-',
                                                                                              '-', '-', '-', '-',
                                                                                              '-', '-', '-', '-', '-',
                                                                                              '-', '-', '-', '-', '-',
                                                                                              '-', '-', '-',
                                                                                              '-', '-', '-', '-', '-',
                                                                                              '-', '-', '-'],
                                                                    'Unit': ['mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea', 'mmol/mol Crea',
                                                                             'mmol/mol Crea'],
                                                                    'Upper Reference Percentile': [97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5, 97.5, 97.5,
                                                                                                   97.5],
                                                                    'Upper Reference Value': [5.40000000e+01,
                                                                                              3.00000000e+00,
                                                                                              1.50000000e+01,
                                                                                              4.00000000e+01,
                                                                                              2.00000000e+01,
                                                                                              7.20000000e+01,
                                                                                              7.50000000e+02,
                                                                                              7.80000000e+01,
                                                                                              2.80000000e+02,
                                                                                              4.40000000e+02,
                                                                                              1.40000000e+02,
                                                                                              1.80000000e+01,
                                                                                              1.50000000e+01,
                                                                                              7.00000000e+00,
                                                                                              1.70000000e+02,
                                                                                              7.00000000e+00,
                                                                                              1.00000000e+01,
                                                                                              1.70000000e+01,
                                                                                              6.60000000e+02,
                                                                                              5.10000000e+01,
                                                                                              7.00000000e+02,
                                                                                              4.30000000e+01,
                                                                                              3.00000000e+00,
                                                                                              4.80000000e+01,
                                                                                              1.10000000e+02,
                                                                                              2.80000000e+02,
                                                                                              3.90000000e+01,
                                                                                              1.10000000e+02,
                                                                                              6.70000000e+01,
                                                                                              4.80000000e+01,
                                                                                              9.20000000e+01,
                                                                                              1.00000000e+02,
                                                                                              3.00000000e+01,
                                                                                              7.00000000e+00,
                                                                                              6.60000000e+01,
                                                                                              1.30000000e+01,
                                                                                              5.00000000e+00,
                                                                                              3.20000000e+01,
                                                                                              3.90000000e+02,
                                                                                              4.70000000e+01,
                                                                                              1.10000000e+01,
                                                                                              6.10000000e+01,
                                                                                              1.90000000e+01,
                                                                                              4.40000000e+01,
                                                                                              1.40000000e+02,
                                                                                              9.60000000e+01,
                                                                                              1.80000000e+02,
                                                                                              8.00000000e+00,
                                                                                              4.40000000e+03],
                                                                    'comment': ['', '', '', '', '', '', '', '', '', '',
                                                                                '', '', '', '', '', '', '',
                                                                                '', '', '', '', '', '', '', '', '', '',
                                                                                '', '', '', '', '', '', '',
                                                                                '', '', '', '', '', '', '', '', '', '',
                                                                                '', '', '', '', ''],
                                                                    'LOD': [3.10000000e+01, 2.00000000e+00,
                                                                            1.50000000e+01,
                                                                            3.90000000e+01, 2.00000000e+01,
                                                                            1.00000000e+01,
                                                                            7.50000000e+02, 7.00000000e+00,
                                                                            5.00000000e+01,
                                                                            3.40000000e+01, 1.00000000e+02,
                                                                            1.80000000e+01,
                                                                            5.00000000e+00, 2.00000000e+00,
                                                                            1.40000000e+02,
                                                                            2.00000000e+00, 1.00000000e+01,
                                                                            2.00000000e+00,
                                                                            1.70000000e+02, 5.00000000e+00,
                                                                            4.00000000e+01,
                                                                            1.00000000e+01, 2.00000000e+00,
                                                                            4.80000000e+01,
                                                                            4.90000000e+01, 2.50000000e+01,
                                                                            5.00000000e+00,
                                                                            5.00000000e+00, 3.50000000e+01,
                                                                            4.80000000e+01,
                                                                            9.20000000e+01, 1.00000000e+02,
                                                                            1.40000000e+01,
                                                                            2.00000000e+00, 1.70000000e+01,
                                                                            9.00000000e+00,
                                                                            5.00000000e+00, 3.20000000e+01,
                                                                            3.90000000e+02,
                                                                            1.70000000e+01, 1.00000000e+01,
                                                                            4.50000000e+01,
                                                                            1.90000000e+01, 4.30000000e+01,
                                                                            3.40000000e+01,
                                                                            9.60000000e+01, 1.80000000e+02,
                                                                            6.00000000e+00,
                                                                            4.40000000e+03],
                                                                    'LLOQ': [numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan],
                                                                    'quantificationType': [
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther,
                                                                        QuantificationType.QuantOther],
                                                                    'calibrationMethod': [
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration,
                                                                        CalibrationMethod.otherCalibration],
                                                                    'ULOQ': [numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                                                             numpy.nan]})
        self.expectedQuantUR['intensityData'] = numpy.array([[53.00, 0.00, 0.00, 47.00, 0.00, 61.00, 0.00, 24.00,
                                                              2100.00, 250.00, 140.00, 0.00, 46.00, 5.00, 660.00, 12.00,
                                                              0.00, 0.00, 250.00, 25.00,
                                                              480.00, 49.00, 0.00, 0.00, 0.00, 39.00, 47.00, 16.00,
                                                              0.00, 0.00, 0.00, 0.00, 38.00, 7.00, 63.00, 14.00, 0.00,
                                                              0.00, 0.00, 0.00, 22.00,
                                                              0.00, 0.00, 0.00, 110.00, 0.00, 0.00, 0.00, 0.00],
                                                             [62.00, 0.00, 0.00, 0.00, 0.00, 69.00, 0.00, 41.00, 800.00,
                                                              210.00, 160.00, 0.00, 34.00, 2.00, 150.00, 8.00, 0.00,
                                                              0.00, 220.00, 11.00, 650.00,
                                                              36.00, 2.00, 0.00, 0.00, 100.00, 23.00, 710.00, 0.00,
                                                              0.00, 0.00, 0.00, 37.00, 7.00, 48.00, 15.00, 0.00, 0.00,
                                                              0.00, 25.00, 0.00, 66.00, 0.00,
                                                              0.00, 110.00, 0.00, 0.00, 0.00, 0.00],
                                                             [57.00, 0.00, 0.00, 0.00, 0.00, 65.00, 0.00, 54.00,
                                                              1700.00, 190.00, 210.00, 0.00, 37.00, 5.00, 180.00, 10.00,
                                                              0.00, 0.00, 330.00, 10.00,
                                                              350.00, 78.00, 0.00, 0.00, 0.00, 0.00, 6.00, 120.00, 0.00,
                                                              0.00, 0.00, 0.00, 15.00, 5.00, 0.00, 15.00, 0.00, 0.00,
                                                              0.00, 0.00, 0.00, 45.00,
                                                              0.00, 0.00, 110.00, 0.00, 0.00, 0.00, 0.00],
                                                             [61.00, 0.00, 0.00, 0.00, 0.00, 56.00, 0.00, 23.00,
                                                              1500.00, 150.00, 160.00, 0.00, 24.00, 3.00, 370.00, 7.00,
                                                              0.00, 0.00, 180.00, 18.00, 380.00,
                                                              65.00, 0.00, 0.00, 0.00, 0.00, 16.00, 0.00, 0.00, 0.00,
                                                              0.00, 0.00, 14.00, 4.00, 26.00, 14.00, 0.00, 0.00, 0.00,
                                                              0.00, 17.00, 56.00, 0.00, 0.00,
                                                              98.00, 0.00, 0.00, 0.00, 0.00],
                                                             [37.00, 0.00, 0.00, 0.00, 0.00, 52.00, 0.00, 0.00, 99.00,
                                                              160.00, 0.00, 0.00, 6.00, 0.00, 0.00, 3.00, 0.00, 0.00,
                                                              210.00, 9.00, 620.00, 14.00,
                                                              0.00, 0.00, 0.00, 0.00, 14.00, 5.00, 0.00, 0.00, 0.00,
                                                              0.00, 18.00, 2.00, 24.00, 0.00, 0.00, 0.00, 0.00, 27.00,
                                                              0.00, 0.00, 0.00, 0.00, 84.00,
                                                              0.00, 0.00, 0.00, 0.00],
                                                             [32.00, 0.00, 0.00, 0.00, 0.00, 43.00, 0.00, 11.00, 460.00,
                                                              260.00, 120.00, 0.00, 0.00, 0.00, 190.00, 4.00, 0.00,
                                                              0.00, 0.00, 0.00, 790.00, 18.00,
                                                              0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
                                                              0.00, 0.00, 2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 29.00,
                                                              0.00, 0.00, 0.00, 0.00, 100.00, 0.00,
                                                              0.00, 11.00, 0.00],
                                                             [36.00, 0.00, 0.00, 0.00, 0.00, 40.00, 0.00, 10.00, 270.00,
                                                              200.00, 130.00, 0.00, 0.00, 0.00, 210.00, 5.00, 0.00,
                                                              0.00, 0.00, 0.00, 730.00, 14.00,
                                                              0.00, 0.00, 0.00, 0.00, 6.00, 0.00, 0.00, 0.00, 0.00,
                                                              0.00, 25.00, 4.00, 38.00, 0.00, 0.00, 0.00, 0.00, 22.00,
                                                              10.00, 0.00, 0.00, 0.00, 85.00, 0.00,
                                                              190.00, 11.00, 0.00],
                                                             [33.00, 0.00, 0.00, 0.00, 0.00, 85.00, 0.00, 13.00,
                                                              1100.00, 350.00, 240.00, 0.00, 15.00, 0.00, 240.00, 4.00,
                                                              0.00, 0.00, 0.00, 20.00, 670.00, 47.00,
                                                              0.00, 0.00, 0.00, 0.00, 30.00, 250.00, 0.00, 0.00, 0.00,
                                                              0.00, 17.00, 3.00, 22.00, 0.00, 0.00, 0.00, 0.00, 0.00,
                                                              0.00, 0.00, 0.00, 0.00, 90.00, 0.00,
                                                              0.00, 0.00, 0.00],
                                                             [47.00, 4.00, 0.00, 0.00, 0.00, 79.00, 0.00, 21.00, 100.00,
                                                              470.00, 170.00, 0.00, 20.00, 3.00, 0.00, 3.00, 0.00, 0.00,
                                                              350.00, 15.00, 51.00, 52.00,
                                                              0.00, 0.00, 0.00, 0.00, 34.00, 17.00, 140.00, 0.00, 0.00,
                                                              0.00, 18.00, 3.00, 38.00, 0.00, 0.00, 0.00, 0.00, 24.00,
                                                              0.00, 54.00, 0.00, 0.00, 110.00,
                                                              0.00, 0.00, 0.00, 0.00]])

        self.expectedQuantUR['expectedConcentration'] = pandas.DataFrame(None, index=list(
            self.expectedQuantUR['sampleMetadata'].index), columns=self.expectedQuantUR['featureMetadata'][
            'Feature Name'].tolist())

        # Calibration
        self.expectedQuantUR['calibIntensityData'] = numpy.ndarray(
            (0, self.expectedQuantUR['featureMetadata'].shape[0]))
        self.expectedQuantUR['calibSampleMetadata'] = pandas.DataFrame(None, columns=self.expectedQuantUR[
            'sampleMetadata'].columns)
        self.expectedQuantUR['calibSampleMetadata']['Metadata Available'] = False
        self.expectedQuantUR['calibFeatureMetadata'] = pandas.DataFrame(
            {'Feature Name': self.expectedQuantUR['featureMetadata']['Feature Name'].tolist()})
        self.expectedQuantUR['calibExpectedConcentration'] = pandas.DataFrame(None, columns=
        self.expectedQuantUR['featureMetadata']['Feature Name'].tolist())
        # Excluded
        self.expectedQuantUR['sampleMetadataExcluded'] = []
        self.expectedQuantUR['featureMetadataExcluded'] = []
        self.expectedQuantUR['intensityDataExcluded'] = []
        self.expectedQuantUR['expectedConcentrationExcluded'] = []
        self.expectedQuantUR['excludedFlag'] = []
        # Attributes
        tmpDataset = nPYc.NMRTargetedDataset('', fileType='empty')
        self.expectedQuantUR['Attributes'] = {'methodName': "Bruker Quant-UR Data",
                                              'dpi': tmpDataset.Attributes['dpi'],
                                              'rsdThreshold': 30,
                                              'figureFormat': tmpDataset.Attributes['figureFormat'],
                                              'figureSize': tmpDataset.Attributes['figureSize'],
                                              'histBins': tmpDataset.Attributes['histBins'],
                                              'noFiles': tmpDataset.Attributes['noFiles'],
                                              'quantiles': tmpDataset.Attributes['quantiles'],
                                              'methodName': 'Bruker Quant-UR Data',
                                              'externalID': [],
                                              'sampleMetadataNotExported': ['Acqu Date', 'Acqu Time', 'Sample Type'],
                                              'featureMetadataNotExported': ['comment'],
                                              'analyticalMeasurements': {'Acquired Time': 'date',
                                                                         'Acquisition batch': 'categorical',
                                                                         'Assay data location': 'categorical',
                                                                         'Assay data name': 'categorical',
                                                                         'Assay protocol': 'categorical',
                                                                         'AssayRole': 'categorical',
                                                                         'Batch': 'categorical',
                                                                         'Correction Batch': 'categorical',
                                                                         'Dilution': 'continuous',
                                                                         'Exclusion Details': 'categorical',
                                                                         'Instrument': 'categorical',
                                                                         'Matrix': 'categorical',
                                                                         'Measurement Date': 'date',
                                                                         'Measurement Time': 'date',
                                                                         'Plate': 'categorical',
                                                                         'Plot Sample Type': 'categorical',
                                                                         'Re-Run': 'categorical',
                                                                         'Run Order': 'continuous',
                                                                         'Sample batch': 'categorical',
                                                                         'Sample position': 'categorical',
                                                                         'SampleType': 'categorical',
                                                                         'Skipped': 'categorical',
                                                                         'Study': 'categorical',
                                                                         'Suplemental Injections': 'categorical',
                                                                         'Well': 'categorical'},
                                              'excludeFromPlotting': ['Sample File Name', 'Sample Base Name',
                                                                      'Batch Termini',
                                                                      'Study Reference', 'Long-Term Reference',
                                                                      'Method Reference',
                                                                      'Dilution Series', 'Skipped', 'Study Sample',
                                                                      'File Path',
                                                                      'Exclusion Details', 'Assay protocol', 'Status',
                                                                      'Measurement Date',
                                                                      'Measurement Time', 'Data Present',
                                                                      'LIMS Present', 'LIMS Marked Missing',
                                                                      'Assay data name', 'Assay data location',
                                                                      'AssayRole',
                                                                      'SampleType', 'Sample ID', 'Plot Sample Type',
                                                                      'SubjectInfoData',
                                                                      'Detector Unit', 'TargetLynx Sample ID',
                                                                      'MassLynx Row ID'],
                                              'additionalQuantParamColumns': ['LOD',
                                                                              'Lower Reference Percentile',
                                                                              'Lower Reference Value',
                                                                              'Upper Reference Percentile',
                                                                              'Upper Reference Value'],
                                              "sampleTypeColours": {"StudySample": "b", "StudyPool": "g",
                                                                    "ExternalReference": "r", "MethodReference": "m",
                                                                    "ProceduralBlank": "c", "Other": "grey",
                                                                    "Study Sample": "b", "Study Reference": "g",
                                                                    "Long-Term Reference": "r",
                                                                    "Method Reference": "m", "Blank": "c",
                                                                    "Unspecified SampleType or AssayRole": "grey"}}

        # 112 features, 10 samples, BrukerBI-LISA
        self.datapathBILISA = os.path.join('..', '..', 'npc-standard-project', 'Raw_Data', 'nmr', 'UnitTest3')
        # Expected TargetedDataset
        # Do not check sampleMetadata['Path']
        self.expectedBILISA = dict()
        self.expectedBILISA['sampleMetadata'] = pandas.DataFrame(
            {'Sample File Name': ['UnitTest3_Serum_Rack01_RCM_190116/10',
                                  'UnitTest3_Serum_Rack01_RCM_190116/100',
                                  'UnitTest3_Serum_Rack01_RCM_190116/110',
                                  'UnitTest3_Serum_Rack01_RCM_190116/120',
                                  'UnitTest3_Serum_Rack01_RCM_190116/130',
                                  'UnitTest3_Serum_Rack01_RCM_190116/140',
                                  'UnitTest3_Serum_Rack01_RCM_190116/150',
                                  'UnitTest3_Serum_Rack01_RCM_190116/160',
                                  'UnitTest3_Serum_Rack01_RCM_190116/170',
                                  'UnitTest3_Serum_Rack01_RCM_190116/180'],
             'Sample Base Name': ['UnitTest3_Serum_Rack01_RCM_190116/10',
                                  'UnitTest3_Serum_Rack01_RCM_190116/100',
                                  'UnitTest3_Serum_Rack01_RCM_190116/110',
                                  'UnitTest3_Serum_Rack01_RCM_190116/120',
                                  'UnitTest3_Serum_Rack01_RCM_190116/130',
                                  'UnitTest3_Serum_Rack01_RCM_190116/140',
                                  'UnitTest3_Serum_Rack01_RCM_190116/150',
                                  'UnitTest3_Serum_Rack01_RCM_190116/160',
                                  'UnitTest3_Serum_Rack01_RCM_190116/170',
                                  'UnitTest3_Serum_Rack01_RCM_190116/180'],
             'expno': [10, 100, 110, 120, 130, 140, 150, 160, 170, 180],
             'Acquired Time': [datetime(2017, 5, 2, 12, 39, 12),
                               datetime(2017, 5, 5, 21, 32, 37),
                               datetime(2017, 5, 2, 16, 3, 59),
                               datetime(2017, 5, 2, 16, 49, 39),
                               datetime(2017, 5, 2, 17, 12, 42),
                               datetime(2017, 5, 5, 21, 56, 7),
                               datetime(2017, 5, 5, 22, 19, 12),
                               datetime(2017, 5, 5, 22, 42, 32),
                               datetime(2017, 5, 2, 18, 45, 32),
                               datetime(2017, 5, 2, 19, 8, 37)],
             'Run Order': [0, 6, 1, 2, 3, 7, 8, 9, 4, 5],
             'AssayRole': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                           numpy.nan, numpy.nan],
             'SampleType': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                            numpy.nan, numpy.nan],
             'Dilution': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
             'Correction Batch': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                                  numpy.nan, numpy.nan, numpy.nan],
             'Sample ID': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                           numpy.nan, numpy.nan],
             'Exclusion Details': [None, None, None, None, None, None, None, None, None, None],
             'Batch': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]})
        self.expectedBILISA['sampleMetadata']['Metadata Available'] = False

        self.expectedBILISA['featureMetadata'] = pandas.DataFrame(
            {'Feature Name': ['TPTG', 'TPCH', 'LDCH', 'HDCH', 'TPA1', 'TPA2', 'TPAB', 'LDHD',
                              'ABA1', 'TBPN', 'VLPN', 'IDPN', 'LDPN', 'L1PN', 'L2PN', 'L3PN',
                              'L4PN', 'L5PN', 'L6PN', 'VLTG', 'IDTG', 'LDTG', 'HDTG', 'VLCH',
                              'IDCH', 'VLFC', 'IDFC', 'LDFC', 'HDFC', 'VLPL', 'IDPL', 'LDPL',
                              'HDPL', 'HDA1', 'HDA2', 'VLAB', 'IDAB', 'LDAB', 'V1TG', 'V2TG',
                              'V3TG', 'V4TG', 'V5TG', 'V1CH', 'V2CH', 'V3CH', 'V4CH', 'V5CH',
                              'V1FC', 'V2FC', 'V3FC', 'V4FC', 'V5FC', 'V1PL', 'V2PL', 'V3PL',
                              'V4PL', 'V5PL', 'L1TG', 'L2TG', 'L3TG', 'L4TG', 'L5TG', 'L6TG',
                              'L1CH', 'L2CH', 'L3CH', 'L4CH', 'L5CH', 'L6CH', 'L1FC', 'L2FC',
                              'L3FC', 'L4FC', 'L5FC', 'L6FC', 'L1PL', 'L2PL', 'L3PL', 'L4PL',
                              'L5PL', 'L6PL', 'L1AB', 'L2AB', 'L3AB', 'L4AB', 'L5AB', 'L6AB',
                              'H1TG', 'H2TG', 'H3TG', 'H4TG', 'H1CH', 'H2CH', 'H3CH', 'H4CH',
                              'H1FC', 'H2FC', 'H3FC', 'H4FC', 'H1PL', 'H2PL', 'H3PL', 'H4PL',
                              'H1A1', 'H2A1', 'H3A1', 'H4A1', 'H1A2', 'H2A2', 'H3A2', 'H4A2'],
             'Lower Reference Percentile': [2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                                            2.5, 2.5],
             'Lower Reference Value': [5.34500000e+01, 1.40310000e+02, 5.45200000e+01,
                                       3.46000000e+01, 1.12000000e+02, 2.40700000e+01,
                                       4.81800000e+01, 9.80000000e-01, 3.00000000e-01,
                                       8.76010000e+02, 5.01100000e+01, 3.59500000e+01,
                                       7.60420000e+02, 9.81000000e+01, 4.66500000e+01,
                                       5.12400000e+01, 7.70700000e+01, 8.56000000e+01,
                                       9.06400000e+01, 2.13800000e+01, 4.62000000e+00,
                                       1.17700000e+01, 7.29000000e+00, 4.88000000e+00,
                                       3.91000000e+00, 2.66000000e+00, 9.40000000e-01,
                                       1.71900000e+01, 6.98000000e+00, 6.44000000e+00,
                                       2.97000000e+00, 3.66900000e+01, 5.65000000e+01,
                                       1.10040000e+02, 2.48600000e+01, 2.76000000e+00,
                                       1.98000000e+00, 4.18200000e+01, 6.23000000e+00,
                                       2.75000000e+00, 2.16000000e+00, 2.93000000e+00,
                                       1.08000000e+00, 8.00000000e-01, 3.90000000e-01,
                                       4.80000000e-01, 1.41000000e+00, 1.00000000e-01,
                                       1.10000000e-01, 4.00000000e-02, 5.00000000e-02,
                                       1.50000000e-01, 2.00000000e-02, 1.31000000e+00,
                                       8.10000000e-01, 8.20000000e-01, 1.62000000e+00,
                                       4.00000000e-01, 2.51000000e+00, 1.19000000e+00,
                                       1.15000000e+00, 1.21000000e+00, 1.12000000e+00,
                                       1.35000000e+00, 8.07000000e+00, 2.48000000e+00,
                                       3.19000000e+00, 4.32000000e+00, 5.41000000e+00,
                                       6.26000000e+00, 2.49000000e+00, 9.90000000e-01,
                                       1.27000000e+00, 1.07000000e+00, 1.56000000e+00,
                                       1.78000000e+00, 5.87000000e+00, 2.20000000e+00,
                                       2.39000000e+00, 3.05000000e+00, 3.72000000e+00,
                                       4.44000000e+00, 5.40000000e+00, 2.57000000e+00,
                                       2.82000000e+00, 4.24000000e+00, 4.71000000e+00,
                                       4.98000000e+00, 1.40000000e+00, 9.80000000e-01,
                                       1.30000000e+00, 1.94000000e+00, 6.10000000e+00,
                                       3.98000000e+00, 6.82000000e+00, 1.06400000e+01,
                                       1.45000000e+00, 7.40000000e-01, 1.25000000e+00,
                                       2.13000000e+00, 7.67000000e+00, 7.40000000e+00,
                                       1.20300000e+01, 1.97500000e+01, 5.95000000e+00,
                                       9.94000000e+00, 1.82600000e+01, 5.60300000e+01,
                                       7.70000000e-01, 1.88000000e+00, 4.85000000e+00,
                                       1.20200000e+01],
             'Unit': ['mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      '-/-', '-/-', 'nmol/L', 'nmol/L', 'nmol/L', 'nmol/L', 'nmol/L',
                      'nmol/L', 'nmol/L', 'nmol/L', 'nmol/L', 'nmol/L', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL',
                      'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL'],
             'Upper Reference Percentile': [97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5, 97.5,
                                            97.5, 97.5, 97.5, 97.5],
             'Upper Reference Value': [4.89810000e+02, 3.41430000e+02, 2.26600000e+02,
                                       9.62500000e+01, 2.16850000e+02, 4.77000000e+01,
                                       1.59940000e+02, 4.08000000e+00, 1.07000000e+00,
                                       2.90820000e+03, 4.73040000e+02, 3.16390000e+02,
                                       2.55951000e+03, 5.67230000e+02, 4.26740000e+02,
                                       4.99000000e+02, 5.77040000e+02, 6.14860000e+02,
                                       8.15440000e+02, 3.35600000e+02, 1.00010000e+02,
                                       4.52200000e+01, 2.85800000e+01, 7.69900000e+01,
                                       4.99600000e+01, 3.30900000e+01, 1.38900000e+01,
                                       6.33500000e+01, 2.70500000e+01, 6.75800000e+01,
                                       3.25300000e+01, 1.20760000e+02, 1.35930000e+02,
                                       2.22020000e+02, 4.79900000e+01, 2.60200000e+01,
                                       1.74000000e+01, 1.40770000e+02, 2.12190000e+02,
                                       6.69200000e+01, 4.88800000e+01, 2.84300000e+01,
                                       7.26000000e+00, 3.51300000e+01, 1.53600000e+01,
                                       1.62300000e+01, 1.51100000e+01, 3.93000000e+00,
                                       1.28900000e+01, 6.60000000e+00, 8.09000000e+00,
                                       7.21000000e+00, 2.20000000e+00, 3.24100000e+01,
                                       1.54300000e+01, 1.35300000e+01, 1.28700000e+01,
                                       5.06000000e+00, 1.40300000e+01, 6.40000000e+00,
                                       5.72000000e+00, 8.43000000e+00, 8.98000000e+00,
                                       1.31600000e+01, 5.87200000e+01, 4.80900000e+01,
                                       4.56400000e+01, 4.88600000e+01, 4.86900000e+01,
                                       5.41900000e+01, 1.69400000e+01, 1.43500000e+01,
                                       1.32900000e+01, 1.24900000e+01, 1.27100000e+01,
                                       1.21800000e+01, 2.98000000e+01, 2.48200000e+01,
                                       2.42100000e+01, 2.50600000e+01, 2.52900000e+01,
                                       2.79100000e+01, 3.12000000e+01, 2.34700000e+01,
                                       2.74400000e+01, 3.17400000e+01, 3.38200000e+01,
                                       4.48500000e+01, 1.19600000e+01, 5.47000000e+00,
                                       5.49000000e+00, 8.49000000e+00, 4.60700000e+01,
                                       1.55800000e+01, 1.87900000e+01, 3.02600000e+01,
                                       1.19600000e+01, 4.59000000e+00, 5.27000000e+00,
                                       8.54000000e+00, 5.71700000e+01, 2.68200000e+01,
                                       3.15300000e+01, 4.35300000e+01, 7.54000000e+01,
                                       3.62200000e+01, 4.70900000e+01, 1.10490000e+02,
                                       8.31000000e+00, 7.78000000e+00, 1.18400000e+01,
                                       2.95800000e+01],
             'comment': ['Main Parameters, Triglycerides, TG',
                         'Main Parameters, Cholesterol, Chol',
                         'Main Parameters, LDL Cholesterol, LDL-Chol',
                         'Main Parameters, HDL Cholesterol, HDL-Chol',
                         'Main Parameters, Apo-A1, Apo-A1',
                         'Main Parameters, Apo-A2, Apo-A2',
                         'Main Parameters, Apo-B100, Apo-B100',
                         'Calculated Figures, LDL Cholesterol / HDL Cholesterol, LDL-Chol/HDL-Chol',
                         'Calculated Figures, Apo-A1 / Apo-B100, Apo-B100/Apo-A1',
                         'Calculated Figures, Total ApoB Particle Number, Total Particle Number',
                         'Calculated Figures, VLDL Particle Number, VLDL Particle Number',
                         'Calculated Figures, IDL Particle Number, IDL Particle Number',
                         'Calculated Figures, LDL Particle Number, LDL Particle Number',
                         'Calculated Figures, LDL-1 Particle Number, LDL-1 Particle Number',
                         'Calculated Figures, LDL-2 Particle Number, LDL-2 Particle Number',
                         'Calculated Figures, LDL-3 Particle Number, LDL-3 Particle Number',
                         'Calculated Figures, LDL-4 Particle Number, LDL-4 Particle Number',
                         'Calculated Figures, LDL-5 Particle Number, LDL-5 Particle Number',
                         'Calculated Figures, LDL-6 Particle Number, LDL-6 Particle Number',
                         'Lipoprotein Main Fractions, Triglycerides, VLDL',
                         'Lipoprotein Main Fractions, Triglycerides, IDL',
                         'Lipoprotein Main Fractions, Triglycerides, LDL',
                         'Lipoprotein Main Fractions, Triglycerides, HDL',
                         'Lipoprotein Main Fractions, Cholesterol, VLDL',
                         'Lipoprotein Main Fractions, Cholesterol, IDL',
                         'Lipoprotein Main Fractions, Free Cholesterol, VLDL',
                         'Lipoprotein Main Fractions, Free Cholesterol, IDL',
                         'Lipoprotein Main Fractions, Free Cholesterol, LDL',
                         'Lipoprotein Main Fractions, Free Cholesterol, HDL',
                         'Lipoprotein Main Fractions, Phospholipids, VLDL',
                         'Lipoprotein Main Fractions, Phospholipids, IDL',
                         'Lipoprotein Main Fractions, Phospholipids, LDL',
                         'Lipoprotein Main Fractions, Phospholipids, HDL',
                         'Lipoprotein Main Fractions, Apo-A1, HDL',
                         'Lipoprotein Main Fractions, Apo-A2, HDL',
                         'Lipoprotein Main Fractions, Apo-B, VLDL',
                         'Lipoprotein Main Fractions, Apo-B, IDL',
                         'Lipoprotein Main Fractions, Apo-B, LDL',
                         'VLDL Subfractions, Triglycerides, VLDL-1',
                         'VLDL Subfractions, Triglycerides, VLDL-2',
                         'VLDL Subfractions, Triglycerides, VLDL-3',
                         'VLDL Subfractions, Triglycerides, VLDL-4',
                         'VLDL Subfractions, Triglycerides, VLDL-5',
                         'VLDL Subfractions, Cholesterol, VLDL-1',
                         'VLDL Subfractions, Cholesterol, VLDL-2',
                         'VLDL Subfractions, Cholesterol, VLDL-3',
                         'VLDL Subfractions, Cholesterol, VLDL-4',
                         'VLDL Subfractions, Cholesterol, VLDL-5',
                         'VLDL Subfractions, Free Cholesterol, VLDL-1',
                         'VLDL Subfractions, Free Cholesterol, VLDL-2',
                         'VLDL Subfractions, Free Cholesterol, VLDL-3',
                         'VLDL Subfractions, Free Cholesterol, VLDL-4',
                         'VLDL Subfractions, Free Cholesterol, VLDL-5',
                         'VLDL Subfractions, Phospholipids, VLDL-1',
                         'VLDL Subfractions, Phospholipids, VLDL-2',
                         'VLDL Subfractions, Phospholipids, VLDL-3',
                         'VLDL Subfractions, Phospholipids, VLDL-4',
                         'VLDL Subfractions, Phospholipids, VLDL-5',
                         'LDL Subfractions, Triglycerides, LDL-1',
                         'LDL Subfractions, Triglycerides, LDL-2',
                         'LDL Subfractions, Triglycerides, LDL-3',
                         'LDL Subfractions, Triglycerides, LDL-4',
                         'LDL Subfractions, Triglycerides, LDL-5',
                         'LDL Subfractions, Triglycerides, LDL-6',
                         'LDL Subfractions, Cholesterol, LDL-1',
                         'LDL Subfractions, Cholesterol, LDL-2',
                         'LDL Subfractions, Cholesterol, LDL-3',
                         'LDL Subfractions, Cholesterol, LDL-4',
                         'LDL Subfractions, Cholesterol, LDL-5',
                         'LDL Subfractions, Cholesterol, LDL-6',
                         'LDL Subfractions, Free Cholesterol, LDL-1',
                         'LDL Subfractions, Free Cholesterol, LDL-2',
                         'LDL Subfractions, Free Cholesterol, LDL-3',
                         'LDL Subfractions, Free Cholesterol, LDL-4',
                         'LDL Subfractions, Free Cholesterol, LDL-5',
                         'LDL Subfractions, Free Cholesterol, LDL-6',
                         'LDL Subfractions, Phospholipids, LDL-1',
                         'LDL Subfractions, Phospholipids, LDL-2',
                         'LDL Subfractions, Phospholipids, LDL-3',
                         'LDL Subfractions, Phospholipids, LDL-4',
                         'LDL Subfractions, Phospholipids, LDL-5',
                         'LDL Subfractions, Phospholipids, LDL-6',
                         'LDL Subfractions, Apo-B, LDL-1', 'LDL Subfractions, Apo-B, LDL-2',
                         'LDL Subfractions, Apo-B, LDL-3', 'LDL Subfractions, Apo-B, LDL-4',
                         'LDL Subfractions, Apo-B, LDL-5', 'LDL Subfractions, Apo-B, LDL-6',
                         'HDL Subfractions, Triglycerides, HDL-1',
                         'HDL Subfractions, Triglycerides, HDL-2',
                         'HDL Subfractions, Triglycerides, HDL-3',
                         'HDL Subfractions, Triglycerides, HDL-4',
                         'HDL Subfractions, Cholesterol, HDL-1',
                         'HDL Subfractions, Cholesterol, HDL-2',
                         'HDL Subfractions, Cholesterol, HDL-3',
                         'HDL Subfractions, Cholesterol, HDL-4',
                         'HDL Subfractions, Free Cholesterol, HDL-1',
                         'HDL Subfractions, Free Cholesterol, HDL-2',
                         'HDL Subfractions, Free Cholesterol, HDL-3',
                         'HDL Subfractions, Free Cholesterol, HDL-4',
                         'HDL Subfractions, Phospholipids, HDL-1',
                         'HDL Subfractions, Phospholipids, HDL-2',
                         'HDL Subfractions, Phospholipids, HDL-3',
                         'HDL Subfractions, Phospholipids, HDL-4',
                         'HDL Subfractions, Apo-A1, HDL-1',
                         'HDL Subfractions, Apo-A1, HDL-2',
                         'HDL Subfractions, Apo-A1, HDL-3',
                         'HDL Subfractions, Apo-A1, HDL-4',
                         'HDL Subfractions, Apo-A2, HDL-1',
                         'HDL Subfractions, Apo-A2, HDL-2',
                         'HDL Subfractions, Apo-A2, HDL-3', 'HDL Subfractions, Apo-A2, HDL-4'],
             'LOD': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan,
                     numpy.nan, numpy.nan],
             'LLOQ': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan],
             'quantificationType': [QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored,
                                    QuantificationType.Monitored,
                                    QuantificationType.Monitored, QuantificationType.Monitored],
             'calibrationMethod': [CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration,
                                   CalibrationMethod.noCalibration, CalibrationMethod.noCalibration],
             'ULOQ': [numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan,
                      numpy.nan, numpy.nan]})
        self.expectedBILISA['intensityData'] = numpy.array([[303.99, 278.77, 134.23, 51.30, 130.78, 28.58, 168.37, 2.62,
                                                             1.29, 3061.47, 600.04, 385.28, 2198.55, 541.55, 219.90,
                                                             160.24, 219.88, 421.21, 527.26,
                                                             188.71, 31.67, 70.47, 29.35, 69.77, 48.03, 28.61, 13.80,
                                                             37.52, 5.17, 58.43, 19.18, 86.89, 79.48, 134.42, 31.89,
                                                             33.00, 21.19, 120.91, 53.10, 36.78,
                                                             43.43, 42.21, 8.07, 10.19, 9.73, 15.17, 26.37, 5.00, 3.31,
                                                             4.81, 6.42, 11.15, 2.14, 8.83, 9.29, 14.47, 21.27, 4.98,
                                                             26.39, 8.74, 7.90, 10.56, 9.31,
                                                             10.95, 43.23, 13.58, 6.15, 10.22, 24.65, 32.38, 13.28,
                                                             4.93, 2.19, 2.93, 6.57, 5.57, 28.40, 9.52, 5.87, 8.10,
                                                             14.38, 18.09, 29.78, 12.09, 8.81, 12.09,
                                                             23.17, 29.00, 12.02, 5.00, 4.94, 7.62, 21.93, 7.90, 6.02,
                                                             12.53, 1.63, 1.07, 0.99, 2.51, 30.42, 15.35, 14.25, 20.86,
                                                             36.70, 22.30, 20.29, 56.70, 5.57,
                                                             5.21, 7.05, 13.36],
                                                            [239.60, 269.23, 122.38, 105.63, 259.63, 36.61, 115.48,
                                                             1.16, 0.44, 2099.65, 313.87, 161.60, 1625.62, 403.79,
                                                             270.04, 223.23, 95.91, 178.89, 447.90,
                                                             155.48, 29.61, 40.00, 37.33, 33.08, 16.40, 17.22, 4.84,
                                                             36.79, 25.04, 39.47, 14.82, 75.92, 156.96, 268.55, 37.16,
                                                             17.26, 8.89, 89.40, 77.93, 28.63,
                                                             24.82, 18.14, 3.50, 9.10, 5.27, 7.51, 9.42, 2.12, 5.31,
                                                             2.52, 3.36, 3.69, 0.58, 12.31, 7.41, 8.44, 8.62, 2.23,
                                                             14.41, 5.78, 5.12, 3.80, 3.66, 8.98,
                                                             34.59, 24.20, 17.40, 5.48, 10.86, 29.79, 10.64, 7.39, 4.63,
                                                             2.70, 2.40, 6.56, 21.69, 14.12, 10.44, 4.62, 6.86, 17.80,
                                                             22.21, 14.85, 12.28, 5.27,
                                                             9.84, 24.63, 19.74, 6.48, 4.90, 5.76, 66.38, 15.38, 9.84,
                                                             13.85, 13.54, 2.76, 2.28, 1.89, 86.48, 27.48, 19.99, 23.69,
                                                             118.96, 44.48, 34.61, 75.47,
                                                             12.47, 7.49, 5.95, 10.85],
                                                            [187.80, 255.49, 127.88, 87.24, 209.02, 34.79, 115.53, 1.47,
                                                             0.55, 2100.58, 292.37, 187.87, 1641.50, 374.48, 265.93,
                                                             208.41, 157.33, 244.85, 353.33,
                                                             108.04, 20.60, 39.78, 27.61, 31.11, 21.79, 14.55, 6.34,
                                                             35.79, 17.81, 31.84, 11.99, 77.41, 124.57, 215.80, 35.71,
                                                             16.08, 10.33, 90.28, 40.30, 18.27,
                                                             20.79, 21.25, 4.98, 4.77, 3.70, 6.28, 11.69, 3.19, 2.49,
                                                             1.78, 2.73, 4.65, 1.07, 6.21, 4.62, 7.02, 10.36, 3.24,
                                                             14.25, 5.69, 5.13, 4.95, 4.33, 6.56,
                                                             33.96, 24.26, 16.70, 11.64, 16.48, 23.20, 10.39, 7.47,
                                                             5.13, 3.90, 4.32, 5.19, 21.13, 14.06, 10.27, 7.61, 9.77,
                                                             14.18, 20.60, 14.63, 11.46, 8.65,
                                                             13.47, 19.43, 13.18, 5.01, 4.22, 5.34, 43.88, 14.40, 10.94,
                                                             15.83, 8.30, 2.34, 2.17, 2.36, 56.27, 23.89, 20.06, 24.51,
                                                             76.66, 34.29, 32.73, 71.17,
                                                             8.06, 6.14, 7.05, 13.24],
                                                            [514.82, 166.43, 52.04, 47.19, 149.56, 40.44, 113.07, 1.10,
                                                             0.76, 2055.83, 794.53, 330.35, 1088.28, 145.20, 97.18,
                                                             0.00, 40.23, 424.38, 508.46, 396.61,
                                                             75.99, 45.70, 36.00, 85.59, 40.87, 42.57, 11.95, 5.25,
                                                             0.00, 102.07, 26.31, 37.72, 81.19, 162.85, 43.90, 43.70,
                                                             18.17, 59.85, 205.21, 66.13, 59.66,
                                                             56.03, 11.33, 23.74, 9.96, 15.55, 25.32, 6.38, 12.59, 5.49,
                                                             8.23, 11.16, 3.25, 30.90, 15.63, 19.77, 24.58, 7.05, 17.58,
                                                             3.61, 5.51, 5.04, 5.48, 9.57,
                                                             1.47, 1.78, 0.00, 0.00, 27.70, 30.82, 0.52, 0.00, 0.00,
                                                             0.00, 5.94, 5.75, 7.22, 1.29, 0.00, 0.49, 15.55, 17.43,
                                                             7.99, 5.34, 0.00, 2.21, 23.34, 27.96,
                                                             12.40, 6.12, 7.03, 11.29, 12.06, 7.94, 7.11, 17.50, 0.00,
                                                             0.10, 1.24, 3.14, 22.66, 18.04, 19.24, 29.38, 30.71, 27.67,
                                                             27.61, 74.92, 6.10, 7.30, 10.44,
                                                             20.76],
                                                            [166.91, 199.47, 83.08, 90.03, 211.32, 32.01, 75.96, 0.92,
                                                             0.36, 1381.23, 216.69, 86.13, 993.41, 253.03, 176.79,
                                                             122.76, 58.32, 110.32, 259.39, 103.44,
                                                             20.53, 23.65, 28.13, 22.04, 8.67, 12.31, 2.60, 21.08,
                                                             18.48, 26.89, 8.63, 51.76, 124.88, 217.79, 33.11, 11.92,
                                                             4.74, 54.64, 55.80, 13.89, 13.13, 14.86,
                                                             4.79, 6.72, 1.58, 2.96, 6.38, 2.94, 3.35, 1.06, 1.66, 2.41,
                                                             0.76, 8.26, 3.44, 4.36, 6.56, 3.03, 8.63, 3.28, 3.34, 2.20,
                                                             1.74, 4.10, 23.59, 16.78, 10.28,
                                                             5.85, 7.94, 17.42, 6.49, 4.94, 3.86, 2.88, 2.18, 4.06,
                                                             15.05, 9.82, 6.56, 4.57, 4.94, 10.80, 13.92, 9.72, 6.75,
                                                             3.21, 6.07, 14.27, 13.51, 5.36, 4.30,
                                                             4.62, 45.29, 16.74, 12.14, 13.66, 7.83, 2.13, 1.80, 1.69,
                                                             57.46, 26.51, 20.05, 19.86, 78.34, 34.05, 35.28, 65.63,
                                                             7.30, 5.55, 6.61, 10.53],
                                                            [204.69, 239.17, 130.86, 64.56, 167.89, 36.08, 125.49, 2.03,
                                                             0.75, 2281.80, 342.89, 174.71, 1757.31, 272.82, 218.27,
                                                             148.27, 173.50, 386.36, 529.62,
                                                             139.69, 22.96, 35.91, 22.03, 38.79, 20.55, 17.49, 6.31,
                                                             32.31, 9.92, 40.11, 12.37, 76.70, 92.02, 172.05, 37.72,
                                                             18.86, 9.61, 96.65, 56.77, 24.52, 26.77,
                                                             23.35, 4.81, 7.97, 5.51, 8.63, 12.70, 3.53, 3.69, 2.71,
                                                             3.72, 4.97, 1.20, 9.57, 6.55, 9.15, 11.13, 3.76, 11.17,
                                                             4.31, 4.10, 4.60, 5.13, 7.00, 23.72,
                                                             18.63, 10.87, 12.83, 28.48, 34.47, 7.15, 5.72, 3.32, 3.79,
                                                             6.68, 7.44, 15.16, 10.79, 7.23, 8.07, 15.70, 19.11, 15.00,
                                                             12.00, 8.15, 9.54, 21.25, 29.13,
                                                             8.30, 3.91, 4.13, 6.26, 21.90, 10.30, 9.98, 19.84, 3.20,
                                                             1.25, 1.79, 3.21, 28.01, 17.53, 18.52, 28.79, 35.95, 25.15,
                                                             29.62, 79.86, 4.43, 4.86, 7.49, 19.30],
                                                            [251.29, 270.78, 132.76, 85.46, 238.14, 48.81, 118.49, 1.55,
                                                             0.50, 2154.51, 360.65, 220.68, 1552.59, 308.27, 238.96,
                                                             189.59, 262.05, 342.26, 274.46,
                                                             162.77, 33.72, 34.75, 33.10, 44.87, 27.25, 20.40, 7.89,
                                                             32.02, 16.56, 47.76, 15.16, 79.41, 138.49, 248.82, 49.04,
                                                             19.83, 12.14, 85.39, 72.38, 26.27,
                                                             27.50, 27.34, 6.96, 9.94, 4.90, 8.39, 14.57, 4.28, 4.83,
                                                             2.31, 3.45, 6.07, 1.99, 11.53, 6.60, 9.47, 13.42, 5.09,
                                                             11.78, 4.68, 5.03, 4.78, 4.02, 4.65,
                                                             28.70, 20.90, 15.38, 21.47, 25.66, 17.66, 8.56, 6.29, 3.62,
                                                             5.34, 5.80, 3.91, 18.60, 12.00, 9.81, 12.87, 14.66, 11.49,
                                                             16.95, 13.14, 10.43, 14.41,
                                                             18.82, 15.09, 12.65, 6.21, 6.34, 8.18, 30.84, 15.65, 15.68,
                                                             21.02, 5.59, 2.80, 3.70, 4.30, 45.40, 28.79, 30.18, 36.02,
                                                             61.25, 41.18, 49.26, 95.45,
                                                             7.92, 8.60, 11.86, 20.59],
                                                            [91.57, 256.88, 147.04, 100.98, 222.79, 30.04, 108.71, 1.46,
                                                             0.49, 1976.65, 121.70, 112.51, 1729.08, 342.32, 294.64,
                                                             251.22, 176.77, 242.00, 369.01,
                                                             30.24, 6.39, 35.85, 25.78, 7.69, 10.73, 4.79, 2.96, 40.84,
                                                             24.12, 10.09, 6.56, 85.46, 130.87, 229.15, 30.97, 6.69,
                                                             6.19, 95.09, 7.14, 3.50, 6.05,
                                                             9.23, 3.24, 0.00, 0.27, 0.93, 4.80, 1.96, 0.00, 0.02, 0.29,
                                                             1.25, 0.06, 0.87, 0.93, 1.91, 4.68, 1.76, 11.06, 5.35,
                                                             4.93, 4.81, 4.03, 6.10, 33.38,
                                                             29.24, 22.75, 16.19, 18.35, 25.51, 9.90, 9.13, 7.73, 5.90,
                                                             5.23, 6.25, 20.04, 16.59, 13.25, 9.77, 10.60, 15.37, 18.83,
                                                             16.20, 13.82, 9.72, 13.31,
                                                             20.29, 13.82, 4.73, 3.45, 3.70, 55.30, 17.06, 11.57, 14.01,
                                                             11.73, 2.58, 2.04, 1.60, 67.00, 25.40, 17.66, 18.77, 94.23,
                                                             36.41, 31.75, 65.78, 8.51,
                                                             5.21, 5.51, 8.69],
                                                            [108.74, 228.04, 105.26, 105.40, 216.12, 36.37, 85.19, 1.00,
                                                             0.39, 1548.99, 159.10, 110.49, 1276.59, 259.42, 236.69,
                                                             120.20, 22.71, 168.51, 430.07,
                                                             49.30, 9.98, 26.15, 22.15, 14.90, 10.59, 7.71, 3.22, 25.35,
                                                             20.77, 14.68, 7.44, 62.20, 138.39, 226.96, 37.08, 8.75,
                                                             6.08, 70.21, 14.11, 4.67, 8.49,
                                                             14.38, 4.73, 0.73, 0.52, 2.01, 7.11, 2.84, 0.71, 0.33,
                                                             0.99, 2.63, 0.65, 1.27, 1.31, 3.18, 6.74, 2.72, 8.42, 3.71,
                                                             3.88, 2.39, 2.50, 6.35, 24.33, 23.79,
                                                             10.81, 3.11, 12.16, 28.46, 7.11, 7.46, 4.29, 2.66, 3.44,
                                                             6.66, 15.16, 13.48, 6.86, 2.86, 6.98, 16.93, 14.27, 13.02,
                                                             6.61, 1.25, 9.27, 23.65, 11.80,
                                                             4.63, 3.38, 2.50, 51.33, 20.46, 14.84, 14.66, 10.00, 3.27,
                                                             2.35, 1.56, 63.58, 30.66, 23.48, 20.49, 87.62, 37.13,
                                                             37.54, 58.50, 8.56, 6.86, 7.99, 10.39],
                                                            [162.57, 233.86, 132.04, 82.05, 197.44, 38.08, 104.29, 1.61,
                                                             0.53, 1896.32, 256.88, 126.96, 1501.86, 203.83, 237.30,
                                                             195.00, 219.55, 320.63, 350.75,
                                                             112.22, 18.11, 25.72, 22.26, 25.99, 13.68, 14.02, 4.07,
                                                             33.08, 15.57, 32.75, 10.04, 73.98, 110.39, 207.92, 38.79,
                                                             14.13, 6.98, 82.60, 48.53, 17.41,
                                                             19.12, 19.68, 4.84, 4.56, 2.59, 5.15, 8.73, 2.87, 2.80,
                                                             1.56, 2.26, 3.58, 0.98, 6.95, 4.46, 6.61, 8.92, 3.28, 6.75,
                                                             3.38, 3.68, 3.55, 3.18, 5.16, 18.81,
                                                             22.81, 17.84, 20.18, 25.38, 24.90, 5.29, 6.70, 5.03, 5.71,
                                                             6.13, 5.27, 12.04, 12.49, 10.17, 11.32, 13.76, 14.35,
                                                             11.21, 13.05, 10.72, 12.07, 17.63,
                                                             19.29, 9.48, 4.25, 3.74, 4.82, 31.83, 14.53, 11.85, 19.77,
                                                             6.16, 2.13, 2.37, 3.15, 41.12, 22.89, 19.96, 27.05, 58.15,
                                                             30.28, 34.20, 81.22, 6.13, 5.84,
                                                             7.66, 17.18]])
        self.expectedBILISA['expectedConcentration'] = pandas.DataFrame(None, index=list(
            self.expectedBILISA['sampleMetadata'].index), columns=self.expectedBILISA['featureMetadata'][
            'Feature Name'].tolist())

        # Calibration
        self.expectedBILISA['calibIntensityData'] = numpy.ndarray((0, self.expectedBILISA['featureMetadata'].shape[0]))
        self.expectedBILISA['calibSampleMetadata'] = pandas.DataFrame(None, columns=self.expectedBILISA[
            'sampleMetadata'].columns)
        self.expectedBILISA['calibSampleMetadata']['Metadata Available'] = False
        self.expectedBILISA['calibFeatureMetadata'] = pandas.DataFrame(
            {'Feature Name': self.expectedBILISA['featureMetadata']['Feature Name'].tolist()})
        self.expectedBILISA['calibExpectedConcentration'] = pandas.DataFrame(None, columns=
        self.expectedBILISA['featureMetadata']['Feature Name'].tolist())
        # Excluded
        self.expectedBILISA['sampleMetadataExcluded'] = []
        self.expectedBILISA['featureMetadataExcluded'] = []
        self.expectedBILISA['intensityDataExcluded'] = []
        self.expectedBILISA['expectedConcentrationExcluded'] = []
        self.expectedBILISA['excludedFlag'] = []
        # Attributes
        tmpDataset = nPYc.NMRTargetedDataset('', fileType='empty')
        self.expectedBILISA['Attributes'] = copy.deepcopy(self.expectedQuantUR['Attributes'])
        self.expectedBILISA['Attributes']['methodName'] = 'NMR Bruker - BI-LISA'

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_loadBrukerXMLDataset(self, mock_stdout):

        with self.subTest(msg='Basic import BrukerQuant-UR with matching fileNamePattern'):
            expected = copy.deepcopy(self.expectedQuantUR)
            # Generate
            result = nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification', sop='BrukerQuant-UR',
                                          fileNamePattern='.*?urine_quant_report_b\.xml$', unit='mmol/mol Crea')
            # Remove path from sampleMetadata
            result.sampleMetadata.drop(['Path'], axis=1, inplace=True)
            result.calibration['calibSampleMetadata'].drop(['Path'], axis=1, inplace=True)

            # Need to sort samples as different OS have different path order
            result.sampleMetadata.sort_values('Sample Base Name', inplace=True)
            sortIndex = result.sampleMetadata.index.values
            result.intensityData = result.intensityData[sortIndex, :]
            result.expectedConcentration = result.expectedConcentration.loc[sortIndex, :]
            result.sampleMetadata = result.sampleMetadata.reset_index(drop=True)
            result.expectedConcentration = result.expectedConcentration.reset_index(drop=True)

            # Test
            pandas.util.testing.assert_frame_equal(
                expected['sampleMetadata'].reindex(sorted(expected['sampleMetadata']), axis=1),
                result.sampleMetadata.reindex(sorted(result.sampleMetadata), axis=1))
            pandas.util.testing.assert_frame_equal(
                expected['featureMetadata'].reindex(sorted(expected['featureMetadata']), axis=1),
                result.featureMetadata.reindex(sorted(result.featureMetadata), axis=1))
            numpy.testing.assert_array_almost_equal(expected['intensityData'], result._intensityData)
            pandas.util.testing.assert_frame_equal(
                expected['expectedConcentration'].reindex(sorted(expected['expectedConcentration']), axis=1),
                result.expectedConcentration.reindex(sorted(result.expectedConcentration), axis=1))
            # Calibration
            pandas.util.testing.assert_frame_equal(
                expected['calibSampleMetadata'].reindex(sorted(expected['calibSampleMetadata']), axis=1),
                result.calibration['calibSampleMetadata'].reindex(sorted(result.calibration['calibSampleMetadata']),
                                                                  axis=1))
            pandas.util.testing.assert_frame_equal(
                expected['calibFeatureMetadata'].reindex(sorted(expected['calibFeatureMetadata']), axis=1),
                result.calibration['calibFeatureMetadata'].reindex(sorted(result.calibration['calibFeatureMetadata']),
                                                                   axis=1))
            numpy.testing.assert_array_almost_equal(expected['calibIntensityData'],
                                                    result.calibration['calibIntensityData'])
            pandas.util.testing.assert_frame_equal(
                expected['calibExpectedConcentration'].reindex(sorted(expected['calibExpectedConcentration']), axis=1),
                result.calibration['calibExpectedConcentration'].reindex(
                    sorted(result.calibration['calibExpectedConcentration']), axis=1), check_index_type=False)
            # Attributes, no check of 'Log'
            self.assertEqual(len(expected['Attributes'].keys()), len(result.Attributes.keys()) - 1)
            for i in expected['Attributes']:
                self.assertEqual(expected['Attributes'][i], result.Attributes[i])

        with self.subTest(msg='Basic import BrukerQuant-UR with implicit fileNamePattern from SOP'):
            expected = copy.deepcopy(self.expectedQuantUR)
            # Generate
            result = nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification', sop='BrukerQuant-UR',
                                          unit='mmol/mol Crea')
            # Remove path from sampleMetadata
            result.sampleMetadata.drop(['Path'], axis=1, inplace=True)
            result.calibration['calibSampleMetadata'].drop(['Path'], axis=1, inplace=True)

            # Need to sort samples as different OS have different path order
            result.sampleMetadata.sort_values('Sample Base Name', inplace=True)
            sortIndex = result.sampleMetadata.index.values
            result.intensityData = result.intensityData[sortIndex, :]
            result.expectedConcentration = result.expectedConcentration.loc[sortIndex, :]
            result.sampleMetadata = result.sampleMetadata.reset_index(drop=True)
            result.expectedConcentration = result.expectedConcentration.reset_index(drop=True)

            # Test
            pandas.util.testing.assert_frame_equal(
                expected['sampleMetadata'].reindex(sorted(expected['sampleMetadata']), axis=1),
                result.sampleMetadata.reindex(sorted(result.sampleMetadata), axis=1))
            pandas.util.testing.assert_frame_equal(
                expected['featureMetadata'].reindex(sorted(expected['featureMetadata']), axis=1),
                result.featureMetadata.reindex(sorted(result.featureMetadata), axis=1))
            numpy.testing.assert_array_almost_equal(expected['intensityData'], result._intensityData)
            pandas.util.testing.assert_frame_equal(
                expected['expectedConcentration'].reindex(sorted(expected['expectedConcentration']), axis=1),
                result.expectedConcentration.reindex(sorted(result.expectedConcentration), axis=1))
            # Calibration
            pandas.util.testing.assert_frame_equal(
                expected['calibSampleMetadata'].reindex(sorted(expected['calibSampleMetadata']), axis=1),
                result.calibration['calibSampleMetadata'].reindex(sorted(result.calibration['calibSampleMetadata']),
                                                                  axis=1))
            pandas.util.testing.assert_frame_equal(
                expected['calibFeatureMetadata'].reindex(sorted(expected['calibFeatureMetadata']), axis=1),
                result.calibration['calibFeatureMetadata'].reindex(sorted(result.calibration['calibFeatureMetadata']),
                                                                   axis=1))
            numpy.testing.assert_array_almost_equal(expected['calibIntensityData'],
                                                    result.calibration['calibIntensityData'])
            pandas.util.testing.assert_frame_equal(
                expected['calibExpectedConcentration'].reindex(sorted(expected['calibExpectedConcentration']), axis=1),
                result.calibration['calibExpectedConcentration'].reindex(
                    sorted(result.calibration['calibExpectedConcentration']), axis=1), check_index_type=False)
            # Attributes, no check of 'Log'
            self.assertEqual(len(expected['Attributes'].keys()), len(result.Attributes.keys()) - 1)
            for i in expected['Attributes']:
                self.assertEqual(expected['Attributes'][i], result.Attributes[i])

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_loadBrukerXMLDataset_warnDuplicates(self, mock_stdout):

        with self.subTest(msg='Import duplicated features (BI-LISA), Raises warning if features are duplicated'):
            expected = copy.deepcopy(self.expectedBILISA)

            # Raise and check warning
            with warnings.catch_warnings(record=True) as w:
                # Cause all warnings to always be triggered.

                warnings.simplefilter("always")
                result = nPYc.NMRTargetedDataset(self.datapathBILISA, fileType='Bruker Quantification',
                                              sop='BrukerBI-LISA', fileNamePattern='.*?results\.xml$')
                # check each warning
                self.assertEqual(len(w), 1)
                assert issubclass(w[0].category, UserWarning)
                assert "The following features are present more than once, only the first occurence will be kept:" in str(
                    w[0].message)

                # Check fuplicated features were filtered
                result.sampleMetadata.drop(['Path'], axis=1, inplace=True)
                result.calibration['calibSampleMetadata'].drop(['Path'], axis=1, inplace=True)

                # Need to sort samples as different OS have different path order
                result.sampleMetadata.sort_values('Sample Base Name', inplace=True)
                sortIndex = result.sampleMetadata.index.values
                result.intensityData = result.intensityData[sortIndex, :]
                result.expectedConcentration = result.expectedConcentration.loc[sortIndex, :]
                result.sampleMetadata = result.sampleMetadata.reset_index(drop=True)
                result.expectedConcentration = result.expectedConcentration.reset_index(drop=True)

                # Test
                pandas.util.testing.assert_frame_equal(
                    expected['sampleMetadata'].reindex(sorted(expected['sampleMetadata']), axis=1),
                    result.sampleMetadata.reindex(sorted(result.sampleMetadata), axis=1))
                pandas.util.testing.assert_frame_equal(
                    expected['featureMetadata'].reindex(sorted(expected['featureMetadata']), axis=1),
                    result.featureMetadata.reindex(sorted(result.featureMetadata), axis=1))
                numpy.testing.assert_array_almost_equal(expected['intensityData'], result._intensityData)
                pandas.util.testing.assert_frame_equal(
                    expected['expectedConcentration'].reindex(sorted(expected['expectedConcentration']), axis=1),
                    result.expectedConcentration.reindex(sorted(result.expectedConcentration), axis=1))
                # Calibration
                pandas.util.testing.assert_frame_equal(
                    expected['calibSampleMetadata'].reindex(sorted(expected['calibSampleMetadata']), axis=1),
                    result.calibration['calibSampleMetadata'].reindex(sorted(result.calibration['calibSampleMetadata']),
                                                                      axis=1))
                pandas.util.testing.assert_frame_equal(
                    expected['calibFeatureMetadata'].reindex(sorted(expected['calibFeatureMetadata']), axis=1),
                    result.calibration['calibFeatureMetadata'].reindex(
                        sorted(result.calibration['calibFeatureMetadata']), axis=1))
                numpy.testing.assert_array_almost_equal(expected['calibIntensityData'],
                                                        result.calibration['calibIntensityData'])
                pandas.util.testing.assert_frame_equal(
                    expected['calibExpectedConcentration'].reindex(sorted(expected['calibExpectedConcentration']),
                                                                   axis=1),
                    result.calibration['calibExpectedConcentration'].reindex(
                        sorted(result.calibration['calibExpectedConcentration']), axis=1), check_index_type=False)
                # Attributes, no check of 'Log'
                self.assertEqual(len(expected['Attributes'].keys()), len(result.Attributes.keys()) - 1)
                for i in expected['Attributes']:
                    self.assertEqual(expected['Attributes'][i], result.Attributes[i])

    def test_brukerXML_raises(self):

        with self.subTest(msg='Raises TypeError if `fileNamePattern` is not a str'):
            self.assertRaises(TypeError,
                              lambda: nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification',
                                                           sop='BrukerQuant-UR', fileNamePattern=5,
                                                           unit='mmol/mol Crea'))

        with self.subTest(msg='Raises TypeError if `pdata` is not am int'):
            self.assertRaises(TypeError,
                              lambda: nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification',
                                                           sop='BrukerQuant-UR', pdata='notAnInt',
                                                           fileNamePattern='.*?urine_quant_report_b\.xml$',
                                                           unit='mmol/mol Crea'))
            self.assertRaises(TypeError,
                              lambda: nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification',
                                                           sop='BrukerQuant-UR', pdata=1.0,
                                                           fileNamePattern='.*?urine_quant_report_b\.xml$',
                                                           unit='mmol/mol Crea'))

        with self.subTest(msg='Raises TypeError if `unit` is not None or a str'):
            self.assertRaises(TypeError,
                              lambda: nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification',
                                                           sop='BrukerQuant-UR', unit=5,
                                                           fileNamePattern='.*?urine_quant_report_b\.xml$'))

        with self.subTest(msg='Raises ValueError if `unit` is not one of the unit in the input data'):
            self.assertRaises(ValueError,
                              lambda: nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification',
                                                           sop='BrukerQuant-UR', unit='notAnExistingUnit',
                                                           fileNamePattern='.*?urine_quant_report_b\.xml$'))

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_loadlims(self, mock_stdout):

        with self.subTest(msg='UnitTest1'):
            dataset = nPYc.NMRTargetedDataset(self.datapathQuantUR, fileType='Bruker Quantification', sop='BrukerQuant-UR',
                                           fileNamePattern='.*?urine_quant_report_b\.xml$', unit='mmol/mol Crea')

            limspath = os.path.join('..', '..', 'npc-standard-project', 'Derived_Worklists',
                                    'UnitTest1_NMR_urine_PCSOP.011.csv')
            dataset.addSampleInfo(filePath=limspath, descriptionFormat='NPC LIMS')

            dataset.sampleMetadata.sort_values('Sample Base Name', inplace=True)
            sortIndex = dataset.sampleMetadata.index.values
            dataset.intensityData = dataset.intensityData[sortIndex, :]
            dataset.sampleMetadata = dataset.sampleMetadata.reset_index(drop=True)

            expected = pandas.Series(
                ['UT1_S1_u1', 'UT1_S2_u1', 'UT1_S3_u1', 'UT1_S4_u1', 'UT1_S4_u2', 'UT1_S4_u3', 'UT1_S4_u4',
                 'External Reference Sample', 'Study Pool Sample'],
                name='Sample ID',
                dtype='str')

            pandas.util.testing.assert_series_equal(dataset.sampleMetadata['Sample ID'], expected)

            expected = pandas.Series(['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9'],
                                     name='Sample position',
                                     dtype='str')

            pandas.util.testing.assert_series_equal(dataset.sampleMetadata['Sample position'], expected)

        with self.subTest(msg='UnitTest3'):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                dataset = nPYc.NMRTargetedDataset(self.datapathBILISA, fileType='Bruker Quantification',
                                               sop='BrukerBI-LISA', fileNamePattern='.*?results\.xml$')

            limspath = os.path.join('..', '..', 'npc-standard-project', 'Derived_Worklists',
                                    'UnitTest3_NMR_serum_PCSOP.012.csv')
            dataset.addSampleInfo(filePath=limspath, descriptionFormat='NPC LIMS')

            dataset.sampleMetadata.sort_values('Sample Base Name', inplace=True)
            sortIndex = dataset.sampleMetadata.index.values
            dataset.intensityData = dataset.intensityData[sortIndex, :]
            dataset.sampleMetadata = dataset.sampleMetadata.reset_index(drop=True)

            expected = pandas.Series(['UT3_S8', 'UT3_S7', 'UT3_S6', 'UT3_S5', 'UT3_S4',
                                      'UT3_S3', 'UT3_S2', 'External Reference Sample',
                                      'Study Pool Sample', 'UT3_S1'],
                                     name='Sample ID',
                                     dtype='str')

            pandas.util.testing.assert_series_equal(dataset.sampleMetadata['Sample ID'], expected)

            expected = pandas.Series(['A1', 'A2', 'A3', 'A4', 'A5',
                                      'A6', 'A7', 'A8', 'A9', 'A10'],
                                     name='Sample position',
                                     dtype='str')

            pandas.util.testing.assert_series_equal(dataset.sampleMetadata['Sample position'], expected)


class test_nmrtargeteddataset_import_undefined(unittest.TestCase):
    """
	Test an error is raised when passing an unknown fileType
	"""

    def setUp(self):
        self.targetedData = nPYc.NMRTargetedDataset('', fileType='empty')

    def test_nmrtargeteddataset_import_raise_notimplemented(self):
        self.assertRaises(NotImplementedError, nPYc.NMRTargetedDataset, os.path.join('nopath'), fileType=None)

if __name__ == '__main__':
    unittest.main()