#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Unittest for Module Helper package"""

import argparse
from datetime import datetime, timezone
from io import StringIO
from json import JSONDecodeError
import logging
from nose2.tools import params
import unittest
from pathlib import Path
import re
import random
import sys
import time
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any, List, Union
from unittest import mock
from unittest.mock import patch
from yaml import YAMLError

# custom imports
# from be_helpers.module_helper import ModuleHelper, ModuleHelperError
from be_helpers import ModuleHelper, ModuleHelperError

# MockFunction class specific imports
import inspect
from textwrap import dedent


class TestModuleHelper(unittest.TestCase):
    """This class describes a ModuleHelper unittest."""

    def setUp(self) -> None:
        """Run before every test method"""
        # define a format
        custom_format = "[%(asctime)s][%(levelname)-8s][%(filename)-20s @" \
                        " %(funcName)-15s:%(lineno)4s] %(message)s"

        # set basic config and level for all loggers
        logging.basicConfig(level=logging.INFO,
                            format=custom_format,
                            stream=sys.stdout)

        # create a logger for this TestSuite
        self.test_logger = logging.getLogger(__name__)

        # set the test logger level
        self.test_logger.setLevel(logging.DEBUG)

        # enable/disable the log output of the device logger for the tests
        # if enabled log data inside this test will be printed
        self.test_logger.disabled = False

    def test_init(self) -> None:
        """Test initalisation of ModuleHelper"""
        obj = ModuleHelper()
        self.assertIsInstance(obj, ModuleHelper)

    def test_create_logger(self) -> None:
        """Test logger creation"""
        logger_name = "Test Logger"
        logger_with_name = ModuleHelper.create_logger(logger_name=logger_name)

        self.assertIsInstance(logger_with_name, logging.Logger)
        self.assertEqual(logger_with_name.name, logger_name)
        self.assertEqual(logger_with_name.level, logging.DEBUG)
        self.assertEqual(logger_with_name.disabled, False)

        logger_without_name = ModuleHelper.create_logger()

        self.assertIsInstance(logger_without_name, logging.Logger)
        self.assertEqual(logger_without_name.name, "be_helpers.module_helper")
        self.assertEqual(logger_without_name.level, logging.DEBUG)

    def test_set_logger_verbose_level(self) -> None:
        """Test setting logger verbose level"""
        logger = ModuleHelper.create_logger()
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertFalse(logger.disabled)

        # set verbose level -vv == WARNING
        ModuleHelper.set_logger_verbose_level(logger=logger,
                                              verbose_level=2,
                                              debug_output=True)
        self.assertEqual(logger.level, logging.WARNING)

        # disable logger output
        logger = ModuleHelper.create_logger()
        ModuleHelper.set_logger_verbose_level(logger=logger,
                                              debug_output=False)
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertTrue(logger.disabled)

        logger = ModuleHelper.create_logger()
        ModuleHelper.set_logger_verbose_level(logger=logger,
                                              debug_output=True)
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertTrue(logger.disabled)

    '''
    @params(
        ({'a': 1, 'b': 2}, 'b', False, [2]),
        # (['a', 'b'], 'b', False, []),
        # ({'a': 1, 'b': 2}, 'c', True, ['c']),
    )
    def test_get_option_values(self,
                               options: List[dict],
                               option: str,
                               raise_error: bool,
                               expectation: list) -> None:
        """Test getting available option values"""
        logger_name = "Test Logger"
        logger_with_name = ModuleHelper.create_logger(logger_name=logger_name)
        with self.assertLogs(logger_name, level="INFO") as logger:
            result = ModuleHelper.get_option_values(options=options,
                                                    option=option,
                                                    raise_error=raise_error,
                                                    logger=logger_with_name)
            self.assertIsInstance(result, list)
            self.assertEqual(result, expectation)

        self.assertEqual(logger.output,
                         ["WARNING:Test Logger:{} is not a valid option".
                          format(option)])

        if raise_error:
            with self.assertRaises(ModuleHelperError) as context:
                error_message = '{} is no valid option'.format(option)
                result = ModuleHelper.get_option_values(options=options,
                                                        option=option,
                                                        raise_error=raise_error)
                self.assertIsInstance(result, list)
                # self.assertEqual(result, expectation)

            self.assertTrue(error_message in str(context.exception))
    '''

    def test_check_option_values(self) -> None:
        """Test selection is an available option"""
        available_options = ['a', 'b', 'c']
        valid_option = 'b'
        invalid_option = 'e'

        self.assertTrue(ModuleHelper.check_option_values(
            options=available_options,
            option=valid_option))

        self.assertFalse(ModuleHelper.check_option_values(
            options=available_options,
            option=invalid_option))

        with self.assertRaises(ModuleHelperError) as context:
            self.assertFalse(ModuleHelper.check_option_values(
                options=available_options,
                option=invalid_option,
                raise_error=True))

        error_message = '{} is no valid option of {}'.format(invalid_option,
                                                             available_options)
        self.assertTrue(error_message in str(context.exception))

        logger_name = "Test Logger"
        logger_with_name = ModuleHelper.create_logger(logger_name=logger_name)
        with self.assertLogs(logger_name, level="INFO") as logger:
            self.assertFalse(ModuleHelper.check_option_values(
                options=available_options,
                option=invalid_option,
                logger=logger_with_name))

        self.assertEqual(logger.output,
                         ["WARNING:Test Logger:{} is no valid option of {}".
                          format(invalid_option, available_options)])

    def test_format_timestamp(self) -> None:
        """Test formatting a timestamp"""
        now = int(time.time())
        known_time = 1662197400

        year_format = "%Y"
        time_format = "%H:%M:%S"
        date_time_format = "%m/%d/%Y, %H:%M:%S"
        known_time_format = "%a, %d %b %Y %H:%M:%S"

        year = datetime.fromtimestamp(now).strftime(year_format)
        full_time = datetime.fromtimestamp(now, tz=timezone.utc).strftime(
            time_format)
        date_time = datetime.fromtimestamp(now, tz=timezone.utc).strftime(
            date_time_format)
        known_time_expectation = "Sat, 03 Sep 2022 09:30:00"

        self.assertEqual(year, ModuleHelper.format_timestamp(
            timestamp=now,
            format=year_format))

        self.assertEqual(full_time, ModuleHelper.format_timestamp(
            timestamp=now,
            format=time_format))

        self.assertEqual(date_time, ModuleHelper.format_timestamp(
            timestamp=now,
            format=date_time_format))

        self.assertEqual(known_time_expectation, ModuleHelper.format_timestamp(
            timestamp=known_time,
            format=known_time_format))

    @patch('time.time', mock.MagicMock(return_value=12345))
    def test_get_unix_timestamp(self) -> None:
        self.assertIsInstance(ModuleHelper.get_unix_timestamp(), int)
        self.assertEqual(ModuleHelper.get_unix_timestamp(), 12345)

    def test_get_random_string(self) -> None:
        """Test getting random string with upper characters and numbers"""
        random_length = random.randint(0, 50)
        random_string = ModuleHelper.get_random_string(length=random_length)
        self.assertEqual(len(random_string), random_length)
        non_matching = re.findall(r'[^A-Z0-9]', random_string)
        self.assertEqual(len(non_matching), 0)

    @params(
        ("test", [29797, 29556]),
        (
            "e8c26e67a48d3f12af87054c412eb9eaa3c0993f",
            [25912, 25394, 13925, 13879, 24884, 14436, 13158, 12594, 24934,
             14391, 12341, 13411, 13361, 12901, 25145, 25953, 24883, 25392,
             14649, 13158]
        )
    )
    def test_convert_string_to_uint16t(self,
                                       input_data: str,
                                       expectation: List[int]) -> None:
        """
        Test conversion of string to list of uint16 values

        :param      input_data:   The input data
        :type       input_data:   str
        :param      expectation:  The expectation
        :type       expectation:  List[str]
        """
        # test without providing a logger
        result = ModuleHelper.convert_string_to_uint16t(content=input_data)
        self.assertIsInstance(result, list)
        self.assertTrue(all(x for x in result))
        self.assertEqual(result, expectation)

        # test with captured logger output
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)
        with self.assertLogs(logger_name, level="DEBUG") as log:
            result = ModuleHelper.convert_string_to_uint16t(content=input_data,
                                                            logger=logger)

            self.assertIsInstance(result, list)
            self.assertTrue(all(x for x in result))
            self.assertEqual(result, expectation)

            self.assertEqual(len(log.output), 2)
            self.assertEqual(len(log.records), 2)
            self.assertIn('DEBUG:Test Logger:Content as unicode: ',
                          log.output[0])
            self.assertIn('DEBUG:Test Logger:Content as numbers: ',
                          log.output[1])

    @params(
        (
            ["C", "B", "A"],
            False,  # descending
            True,   # return value
            ["A", "B", "C"]
        ),
        (
            "B",
            False,  # descending
            False,  # return value
            "B"
        ),
        (
            "ASDF",
            False,  # descending
            False,  # return value
            "ASDF"
        ),
        (
            [42, 84, 12],
            False,  # descending
            True,   # return value
            [12, 42, 84]
        ),
        (
            ["def", "abc", "ghi"],
            False,  # descending
            True,   # return value
            ["abc", "def", "ghi"],
        ),
        (
            ["def", "abc", "ghi"],
            True,  # descending
            True,   # return value
            ["ghi", "def", "abc"],
        )
    )
    def test_sort_by_name(self,
                          input_data: Union[Any, list],
                          descending: bool,
                          expectation_result: bool,
                          expectation: Union[Any, list]) -> None:
        """
        Test list sorting by name

        :param      input_data:         The input data
        :type       input_data:         Union[Any, list]
        :param      descending:         Flag to sort in descending order
        :type       descending:         bool
        :param      expectation_result: Expected return value of function
        :type       expectation_result: bool
        :param      expectation:        The expectation
        :type       expectation:        Union[Any, list]
        """
        result = ModuleHelper.sort_by_name(a_list=input_data,
                                           descending=descending)
        self.assertEqual(result, expectation_result)
        self.assertEqual(input_data, expectation)
        for ele in zip(input_data, expectation):
            self.assertIsInstance(ele, tuple)
            self.assertEqual(ele[0], ele[1])

    @params(
        ({'a': 1}, True),
        ([123], False),
        ("asdf", False),
        (123, False),
        ("{'a': 1}", False),
        ({'a'}, False)
    )
    def test_is_json(self,
                     input_data: Union[Any, dict],
                     expectation: bool) -> None:
        """
        Test input to be a valid JSON

        :param      input_data:   The input data
        :type       input_data:   Union[Any, dict]
        :param      expectation:  The expectation
        :type       expectation:  bool
        """
        result = ModuleHelper.is_json(content=input_data)
        self.assertEqual(result, expectation)

    @patch('sys.stderr', new_callable=StringIO)
    def test_parser_valid_file(self, mock_stderr: StringIO) -> None:
        """Test given argument is valid file for parser"""
        parser = argparse.ArgumentParser("Description")

        with NamedTemporaryFile() as fp:
            result = ModuleHelper.parser_valid_file(parser=parser, arg=fp.name)
            self.assertEqual(result, fp.name)

        with TemporaryDirectory() as dp:
            with self.assertRaises(SystemExit) as context:
                result = ModuleHelper.parser_valid_file(parser=parser, arg=dp)
                # error_message = 'File {} does not exist!'.format(dp.name)
                # self.assertTrue(error_message in str(context.exception))

            self.assertEqual(str(context.exception), '2')
            self.assertIn('The file {} does not exist!'.format(dp),
                          mock_stderr.getvalue())

    @patch('sys.stderr', new_callable=StringIO)
    def test_parser_valid_dir(self, mock_stderr: StringIO) -> None:
        """Test given argument is valid directory for parser"""
        parser = argparse.ArgumentParser("Description")

        with TemporaryDirectory() as dp:
            result = ModuleHelper.parser_valid_dir(parser=parser, arg=dp)
            self.assertEqual(result, dp)

        with NamedTemporaryFile() as fp:
            with self.assertRaises(SystemExit) as context:
                result = ModuleHelper.parser_valid_dir(parser=parser,
                                                       arg=fp.name)
                # error_message = 'Folder {} does not exist!'.format(fp.name)
                # self.assertTrue(error_message in str(context.exception))

            self.assertEqual(str(context.exception), '2')
            self.assertIn('The directory {} does not exist!'.format(fp.name),
                          mock_stderr.getvalue())

    def test_check_file(self) -> None:
        """Check given path is a file of specified type aka suffix"""
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.check_file(file_path=fp.name, suffix="")
            self.assertTrue(result)

        with NamedTemporaryFile() as fp:
            result = ModuleHelper.check_file(file_path=fp.name, suffix="asdf")
            self.assertFalse(result)

        with TemporaryDirectory() as dp:
            result = ModuleHelper.check_file(file_path=dp, suffix="")
            self.assertFalse(result)

    def test_check_folder(self) -> None:
        """Check given path is a folder"""
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.check_folder(folder_path=fp.name)
            self.assertFalse(result)

        with TemporaryDirectory() as dp:
            result = ModuleHelper.check_folder(folder_path=dp)
            self.assertTrue(result)

    def test_get_current_path(self) -> None:
        """Test get current path of ModuleHelper file"""
        result = ModuleHelper.get_current_path()
        # tests is child of repo, path of module_helper is child child of repo
        self.assertEqual(result.parent.parent, Path(__file__).parent.parent)

    def test_get_full_path(self) -> None:
        """Get full path to parent of provided path"""
        with TemporaryDirectory() as dp:
            result = ModuleHelper.get_full_path(base=dp)
            self.assertEqual(result, Path(dp).parent.resolve())

    def test_save_yaml_file(self) -> None:
        """Test saving content to a YAML file"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        content = {
            'key': 'val',
            'key2': {
                'key_nested': 'val_nested'
            },
            'key3': ['asdf', 123, {'key4': 'val4'}]
        }

        #
        # Test positive path
        #
        # positive path without logger or errors raising
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_yaml_file(path=fp.name, content=content)
            self.assertTrue(result)

            loaded_content = ModuleHelper.load_yaml_file(path=fp.name)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, content)

        # positive path with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_yaml_file(path=fp.name,
                                                     content=content,
                                                     logger=logger)
                self.assertTrue(result)

                loaded_content = ModuleHelper.load_yaml_file(path=fp.name)
                self.assertIsInstance(loaded_content, dict)
                self.assertEqual(loaded_content, content)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('DEBUG:Test Logger:File {} saved successfully'.
                      format(fp.name),
                      log.output[0])

        #
        # Test OSError
        #
        # test OSError
        with TemporaryDirectory() as dp:
            result = ModuleHelper.save_yaml_file(path=dp,
                                                 content=content)
            self.assertFalse(result)

        # test OSError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with TemporaryDirectory() as dp:
                result = ModuleHelper.save_yaml_file(path=dp,
                                                     content=content,
                                                     logger=logger)
                self.assertFalse(result)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        # test OSError raising
        with self.assertRaises(OSError) as context:
            with TemporaryDirectory() as dp:
                result = ModuleHelper.save_yaml_file(path=dp,
                                                     content=content,
                                                     raise_error=True)
                self.assertFalse(result)

        self.assertIn("Is a directory: '{}'".format(dp),
                      str(context.exception))

        # test OSError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(OSError) as context:
                with TemporaryDirectory() as dp:
                    result = ModuleHelper.save_yaml_file(path=dp,
                                                         content=content,
                                                         logger=logger,
                                                         raise_error=True)
                    self.assertFalse(result)

            self.assertIn("Is a directory: '{}'".format(dp),
                          str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

    def test_load_yaml_file(self) -> None:
        """Test loading a YAML file"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        content = {
            'key': 'val',
            'key2': {
                'key_nested': 'val_nested'
            },
            'key3': ['asdf', 123, {'key4': 'val4'}]
        }

        data_files_path = Path(__file__).parent / 'data'
        invalid_yaml_file_path = data_files_path / 'invalid.yaml'

        #
        # Test positive path
        #
        # positive path without logger or errors raising
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_yaml_file(path=fp.name, content=content)
            self.assertTrue(result)

            loaded_content = ModuleHelper.load_yaml_file(path=fp.name)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, content)

        # positive path with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_yaml_file(path=fp.name,
                                                     content=content)
                self.assertTrue(result)

                loaded_content = ModuleHelper.load_yaml_file(path=fp.name,
                                                             logger=logger)
                self.assertIsInstance(loaded_content, dict)
                self.assertEqual(loaded_content, content)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('DEBUG:Test Logger:Content of {} loaded successfully'.
                      format(fp.name),
                      log.output[0])

        #
        # Test OSError
        #
        # test OSError
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_yaml_file(path=fp.name,
                                                 content=content)
            self.assertTrue(result)

            # point to parent folder instead of file
            loaded_content = ModuleHelper.load_yaml_file(
                path=Path(fp.name).parent)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, {})

        # test OSError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_yaml_file(path=fp.name,
                                                     content=content)
                self.assertTrue(result)

                # point to parent folder instead of file
                loaded_content = ModuleHelper.load_yaml_file(
                    path=Path(fp.name).parent,
                    logger=logger)
                self.assertIsInstance(loaded_content, dict)
                self.assertEqual(loaded_content, {})

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        # test OSError raising
        with self.assertRaises(OSError) as context:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_yaml_file(path=fp.name,
                                                     content=content)
                self.assertTrue(result)

                # point to parent folder instead of file
                loaded_content = ModuleHelper.load_yaml_file(
                    path=Path(fp.name).parent,
                    raise_error=True)

        self.assertIn("Is a directory: '{}'".format(Path(fp.name).parent),
                      str(context.exception))

        # test OSError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(OSError) as context:
                with NamedTemporaryFile() as fp:
                    result = ModuleHelper.save_yaml_file(path=fp.name,
                                                         content=content)
                    self.assertTrue(result)

                    # point to parent folder instead of file
                    loaded_content = ModuleHelper.load_yaml_file(
                        path=Path(fp.name).parent,
                        raise_error=True,
                        logger=logger)

        self.assertIn("Is a directory: '{}'".format(Path(fp.name).parent),
                      str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        #
        # Test YAMLError
        #
        # test YAMLError
        loaded_content = ModuleHelper.load_yaml_file(
            path=invalid_yaml_file_path)
        self.assertIsInstance(loaded_content, dict)
        self.assertEqual(loaded_content, {})

        # test YAMLError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            loaded_content = ModuleHelper.load_yaml_file(
                path=invalid_yaml_file_path,
                logger=logger)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, {})

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to YAMLError:',
                      log.output[0])

        # test YAMLError raising
        with self.assertRaises(YAMLError) as context:
            loaded_content = ModuleHelper.load_yaml_file(
                path=invalid_yaml_file_path,
                raise_error=True)

        self.assertIn('mapping values are not allowed here',
                      str(context.exception))

        # test YAMLError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(YAMLError) as context:
                loaded_content = ModuleHelper.load_yaml_file(
                    path=invalid_yaml_file_path,
                    raise_error=True,
                    logger=logger)

        self.assertIn('mapping values are not allowed here',
                      str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to YAMLError:',
                      log.output[0])

    def test_save_json_file(self) -> None:
        """Test saving data as JSON file"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        content = {
            'key': 'val',
            'key2': {
                'key_nested': 'val_nested'
            },
            'key3': ['asdf', 123, {'key4': 'val4'}]
        }

        #
        # Test positive path
        #
        # positive path without logger or errors raising, with pretty format
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_json_file(path=fp.name, content=content)
            self.assertTrue(result)

            loaded_content = ModuleHelper.load_json_file(path=fp.name)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, content)

        # positive path without logger or errors raising, without pretty format
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_json_file(path=fp.name,
                                                 content=content,
                                                 pretty=False)
            self.assertTrue(result)

            loaded_content = ModuleHelper.load_json_file(path=fp.name)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, content)

        # positive path with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_json_file(path=fp.name,
                                                     content=content,
                                                     logger=logger)
                self.assertTrue(result)

                loaded_content = ModuleHelper.load_json_file(path=fp.name)
                self.assertIsInstance(loaded_content, dict)
                self.assertEqual(loaded_content, content)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('DEBUG:Test Logger:File {} saved successfully'.
                      format(fp.name),
                      log.output[0])

        #
        # Test OSError
        #
        # test OSError
        with TemporaryDirectory() as dp:
            result = ModuleHelper.save_json_file(path=dp,
                                                 content=content)
            self.assertFalse(result)

        # test OSError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with TemporaryDirectory() as dp:
                result = ModuleHelper.save_json_file(path=dp,
                                                     content=content,
                                                     logger=logger)
                self.assertFalse(result)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        # test OSError raising
        with self.assertRaises(OSError) as context:
            with TemporaryDirectory() as dp:
                result = ModuleHelper.save_json_file(path=dp,
                                                     content=content,
                                                     raise_error=True)
                self.assertFalse(result)

        self.assertIn("Is a directory: '{}'".format(dp),
                      str(context.exception))

        # test OSError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(OSError) as context:
                with TemporaryDirectory() as dp:
                    result = ModuleHelper.save_json_file(path=dp,
                                                         content=content,
                                                         logger=logger,
                                                         raise_error=True)
                    self.assertFalse(result)

            self.assertIn("Is a directory: '{}'".format(dp),
                          str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

    def test_load_json_file(self) -> None:
        """Test loading data from JSON file"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        content = {
            'key': 'val',
            'key2': {
                'key_nested': 'val_nested'
            },
            'key3': ['asdf', 123, {'key4': 'val4'}]
        }

        data_files_path = Path(__file__).parent / 'data'
        invalid_json_file_path = data_files_path / 'invalid.json'

        #
        # Test positive path
        #
        # positive path without logger or errors raising
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_json_file(path=fp.name, content=content)
            self.assertTrue(result)

            loaded_content = ModuleHelper.load_json_file(path=fp.name)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, content)

        # positive path with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_json_file(path=fp.name,
                                                     content=content)
                self.assertTrue(result)

                loaded_content = ModuleHelper.load_json_file(path=fp.name,
                                                             logger=logger)
                self.assertIsInstance(loaded_content, dict)
                self.assertEqual(loaded_content, content)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('DEBUG:Test Logger:Content of {} loaded successfully'.
                      format(fp.name),
                      log.output[0])

        #
        # Test OSError
        #
        # test OSError
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_json_file(path=fp.name,
                                                 content=content)
            self.assertTrue(result)

            # point to parent folder instead of file
            loaded_content = ModuleHelper.load_json_file(
                path=Path(fp.name).parent)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, {})

        # test OSError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_json_file(path=fp.name,
                                                     content=content)
                self.assertTrue(result)

                # point to parent folder instead of file
                loaded_content = ModuleHelper.load_json_file(
                    path=Path(fp.name).parent,
                    logger=logger)
                self.assertIsInstance(loaded_content, dict)
                self.assertEqual(loaded_content, {})

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        # test OSError raising
        with self.assertRaises(OSError) as context:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_json_file(path=fp.name,
                                                     content=content)
                self.assertTrue(result)

                # point to parent folder instead of file
                loaded_content = ModuleHelper.load_json_file(
                    path=Path(fp.name).parent,
                    raise_error=True)

        self.assertIn("Is a directory: '{}'".format(Path(fp.name).parent),
                      str(context.exception))

        # test OSError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(OSError) as context:
                with NamedTemporaryFile() as fp:
                    result = ModuleHelper.save_json_file(path=fp.name,
                                                         content=content)
                    self.assertTrue(result)

                    # point to parent folder instead of file
                    loaded_content = ModuleHelper.load_json_file(
                        path=Path(fp.name).parent,
                        raise_error=True,
                        logger=logger)

        self.assertIn("Is a directory: '{}'".format(Path(fp.name).parent),
                      str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        #
        # Test JSONDecodeError
        #
        # test JSONDecodeError
        loaded_content = ModuleHelper.load_json_file(
            path=invalid_json_file_path)
        self.assertIsInstance(loaded_content, dict)
        self.assertEqual(loaded_content, {})

        # test JSONDecodeError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            loaded_content = ModuleHelper.load_json_file(
                path=invalid_json_file_path,
                logger=logger)
            self.assertIsInstance(loaded_content, dict)
            self.assertEqual(loaded_content, {})

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn("WARNING:Test Logger:Failed due to ValueError: "
                      "Expecting ',' delimiter",
                      log.output[0])

        # test JSONDecodeError raising
        with self.assertRaises(JSONDecodeError) as context:
            loaded_content = ModuleHelper.load_json_file(
                path=invalid_json_file_path,
                raise_error=True)

        self.assertIn("Expecting ',' delimiter:", str(context.exception))

        # test JSONDecodeError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(JSONDecodeError) as context:
                loaded_content = ModuleHelper.load_json_file(
                    path=invalid_json_file_path,
                    raise_error=True,
                    logger=logger)

        self.assertIn("Expecting ',' delimiter:", str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn("WARNING:Test Logger:Failed due to ValueError: "
                      "Expecting ',' delimiter",
                      log.output[0])

    @params(
        'json',
        'yaml',
        'unsupported',
    )
    def test_save_dict_to_file(self, file_type: str) -> None:
        """Test saving dict to file"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        content = {
            'key': 'val',
            'key2': {
                'key_nested': 'val_nested'
            },
            'key3': ['asdf', 123, {'key4': 'val4'}]
        }

        if file_type in ['json', 'yaml']:
            #
            # Test positive path
            #
            # positive path without logger
            with NamedTemporaryFile() as fp:
                name_with_suffix = "{}.{}".format(fp.name, file_type)
                result = ModuleHelper.save_dict_to_file(path=name_with_suffix,
                                                        content=content)
                self.assertTrue(result)

                if file_type == 'json':
                    # point to parent folder instead of file
                    loaded_content = ModuleHelper.load_json_file(
                        path=Path(fp.name).parent)
                    self.assertIsInstance(loaded_content, dict)
                    self.assertEqual(loaded_content, {})
                elif file_type == 'yaml':
                    # point to parent folder instead of file
                    loaded_content = ModuleHelper.load_yaml_file(
                        path=Path(fp.name).parent)
                    self.assertIsInstance(loaded_content, dict)
                    self.assertEqual(loaded_content, {})

            # positive path with logger
            with self.assertLogs(logger_name, level="DEBUG") as log:
                with NamedTemporaryFile() as fp:
                    name_with_suffix = "{}.{}".format(fp.name, file_type)
                    result = ModuleHelper.save_dict_to_file(
                        path=name_with_suffix,
                        content=content,
                        logger=logger)
                    self.assertTrue(result)

                    # point to parent folder instead of file
                    loaded_content = ModuleHelper.load_json_file(
                        path=Path(fp.name).parent)
                    self.assertIsInstance(loaded_content, dict)
                    self.assertEqual(loaded_content, {})

            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn("DEBUG:Test Logger:Save file to: {}".
                          format(name_with_suffix),
                          log.output[-1])

            # negative path due to invalid path without logger
            invalid_path = "/random/path/asdf.{}".format(file_type)
            result = ModuleHelper.save_dict_to_file(path=invalid_path,
                                                    content=content)
            self.assertFalse(result)

            # negative path due to invalid path with logger
            with self.assertLogs(logger_name, level="WARNING") as log:
                invalid_path = "/random/path/asdf.{}".format(file_type)
                result = ModuleHelper.save_dict_to_file(path=invalid_path,
                                                        content=content,
                                                        logger=logger)
                self.assertFalse(result)

            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn("WARNING:Test Logger:Parent of given path is not a "
                          "directory",
                          log.output[-1])

            # negative path due to invalid content type without logger
            with NamedTemporaryFile() as fp:
                name_with_suffix = "{}.{}".format(fp.name, file_type)
                result = ModuleHelper.save_dict_to_file(path=name_with_suffix,
                                                        content=[content])
                self.assertFalse(result)

            # negative path due to invalid content type with logger
            with NamedTemporaryFile() as fp:
                name_with_suffix = "{}.{}".format(fp.name, file_type)
                with self.assertLogs(logger_name, level="WARNING") as log:
                    result = ModuleHelper.save_dict_to_file(
                        path=name_with_suffix,
                        content=[content],
                        logger=logger)
                    self.assertFalse(result)

            self.assertIn("WARNING:Test Logger:Given content is not a "
                          "dictionary",
                          log.output[-1])
        else:
            #
            # Test negative path
            #
            # negative path without logger
            with NamedTemporaryFile() as fp:
                name_with_suffix = "{}.{}".format(fp.name, file_type)
                result = ModuleHelper.save_dict_to_file(path=name_with_suffix,
                                                        content=content)
                self.assertFalse(result)

            # negative path with logger
            with self.assertLogs(logger_name, level="WARNING") as log:
                with NamedTemporaryFile() as fp:
                    name_with_suffix = "{}.{}".format(fp.name, file_type)
                    result = ModuleHelper.save_dict_to_file(
                        path=name_with_suffix,
                        content=content,
                        logger=logger)
                    self.assertFalse(result)

            # first logger output comes from "check_option_values" function,
            # second output comes from "save_dict_to_file"
            self.assertEqual(len(log.output), 2)
            self.assertEqual(len(log.records), 2)
            self.assertIn("WARNING:Test Logger:.{} is no valid option of {}".
                          format(file_type, ['.json', '.yaml']),
                          log.output[-1])

    @params(
        'valid.json',
        'valid.yaml',
        'unsupported.txt',
    )
    def test_load_dict_from_file(self, file_type: str) -> None:
        """Test loading dict from file"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        expected_content = {
            'key': 'val',
            'key2': {
                'key_nested': 'val_nested'
            },
            'key3': ['asdf', 123, {'key4': 'val4'}]
        }

        data_files_path = Path(__file__).parent / 'data'

        if Path(file_type).suffix.lower() in ['.json', '.yaml']:
            #
            # Test positive path
            #
            # positive path without logger
            file_path = data_files_path / file_type
            result = ModuleHelper.load_dict_from_file(path=file_path)
            self.assertIsInstance(result, dict)
            self.assertEqual(result, expected_content)

            # positive path with logger
            with self.assertLogs(logger_name, level="DEBUG") as log:
                result = ModuleHelper.load_dict_from_file(
                    path=file_path,
                    logger=logger)
                self.assertIsInstance(result, dict)
                self.assertEqual(result, expected_content)

            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn("DEBUG:Test Logger:Load file from: {}".
                          format(file_path),
                          log.output[-1])

            # negative path due to invalid path without logger
            file_path = data_files_path / '..' / file_type
            result = ModuleHelper.load_dict_from_file(path=file_path)
            self.assertIsInstance(result, dict)
            self.assertEqual(result, {})

            # negative path due to invalid path with logger
            with self.assertLogs(logger_name, level="WARNING") as log:
                result = ModuleHelper.load_dict_from_file(
                    path=file_path,
                    logger=logger)
                self.assertIsInstance(result, dict)
                self.assertEqual(result, {})

            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn("WARNING:Test Logger:Given path is not a valid file",
                          log.output[-1])
        else:
            #
            # Test negative path
            #
            # negative path without logger
            file_path = data_files_path / file_type
            result = ModuleHelper.load_dict_from_file(path=file_path)
            self.assertIsInstance(result, dict)
            self.assertEqual(result, {})

            # negative path with logger
            with self.assertLogs(logger_name, level="WARNING") as log:
                result = ModuleHelper.load_dict_from_file(
                    path=file_path,
                    logger=logger)
                self.assertIsInstance(result, dict)
                self.assertEqual(result, {})

            # first logger output comes from "check_option_values" function,
            # second output comes from "load_dict_from_file"
            self.assertEqual(len(log.output), 2)
            self.assertEqual(len(log.records), 2)
            self.assertIn("WARNING:Test Logger:{} is no valid option of {}".
                          format(Path(file_type).suffix.lower(),
                                 ['.json', '.yaml']),
                          log.output[-1])

    def test_get_raw_file_content(self) -> None:
        """Test getting raw file content"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        expected_content = \
            """Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
sed diam nonumy eirmod tempor invidunt ut labore et dolore
magna aliquyam erat, sed diam voluptua."""

        data_files_path = Path(__file__).parent / 'data'
        file_path = data_files_path / 'lorem.txt'

        #
        # Test positive path
        #
        # positive path without logger or errors raising
        result = ModuleHelper.get_raw_file_content(path=file_path)
        self.assertIsInstance(result, str)
        self.assertEqual(result, expected_content)

        # positive path with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            result = ModuleHelper.get_raw_file_content(path=file_path,
                                                       logger=logger)
            self.assertIsInstance(result, str)
            self.assertEqual(result, expected_content)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('DEBUG:Test Logger:Content of {} read successfully'.
                      format(file_path),
                      log.output[0])

        #
        # Test OSError
        #
        # test OSError
        result = ModuleHelper.get_raw_file_content(path=file_path.parent)
        self.assertIsInstance(result, str)
        self.assertEqual(result, '')

        # test OSError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            result = ModuleHelper.get_raw_file_content(path=file_path.parent,
                                                       logger=logger)
            self.assertIsInstance(result, str)
            self.assertEqual(result, '')

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        # test OSError raising
        with self.assertRaises(OSError) as context:
            result = ModuleHelper.get_raw_file_content(path=file_path.parent,
                                                       raise_error=True)
            self.assertIsInstance(result, str)
            self.assertEqual(result, '')

        self.assertIn("Is a directory: '{}'".format(file_path.parent),
                      str(context.exception))

        # test OSError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(OSError) as context:
                result = ModuleHelper.get_raw_file_content(
                    path=file_path.parent,
                    logger=logger,
                    raise_error=True)
                self.assertIsInstance(result, str)
                self.assertEqual(result, '')

        self.assertIn("Is a directory: '{}'".format(file_path.parent),
                      str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

    def test_save_list_to_file(self) -> None:
        """Test saving list to file"""
        logger_name = "Test Logger"
        logger = ModuleHelper.create_logger(logger_name=logger_name)

        content = ['asdf', 'qwertz', 1234]

        #
        # Test positive path
        #
        # positive path without logger or errors raising, without new line
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_list_to_file(path=fp.name,
                                                    content=content)
            self.assertTrue(result)

            loaded_content = ModuleHelper.get_raw_file_content(path=fp.name)
            self.assertIsInstance(loaded_content, str)
            self.assertEqual(loaded_content,
                             ''.join([str(ele) for ele in content]))

        # positive path without logger or errors raising, with new line
        with NamedTemporaryFile() as fp:
            result = ModuleHelper.save_list_to_file(path=fp.name,
                                                    with_new_line=True,
                                                    content=content)
            self.assertTrue(result)

            loaded_content = ModuleHelper.get_raw_file_content(path=fp.name)
            self.assertIsInstance(loaded_content, str)
            self.assertEqual(loaded_content,
                             '\n'.join([str(ele) for ele in content]))

        # positive path with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with NamedTemporaryFile() as fp:
                result = ModuleHelper.save_list_to_file(path=fp.name,
                                                        with_new_line=True,
                                                        content=content,
                                                        logger=logger)
                self.assertTrue(result)

                loaded_content = ModuleHelper.get_raw_file_content(
                    path=fp.name)
                self.assertIsInstance(loaded_content, str)
                self.assertEqual(loaded_content,
                                 '\n'.join([str(ele) for ele in content]))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('DEBUG:Test Logger:Content successfully saved to {}'.
                      format(fp.name),
                      log.output[0])

        # test negative path, content not a list, without logger
        result = ModuleHelper.save_list_to_file(path='file.txt',
                                                content='asdf')
        self.assertFalse(result)

        # test negative path, content not a list, with logger
        with self.assertLogs(logger_name, level="WARNING") as log:
            result = ModuleHelper.save_list_to_file(path='asdf.txt',
                                                    content=123,
                                                    logger=logger)
            self.assertFalse(result)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Content to save must be list, not '
                      '{}'.format(type(123)),
                      log.output[0])

        # test negative path, write_mode not available, without logger
        result = ModuleHelper.save_list_to_file(path='file.txt',
                                                content=content,
                                                mode='s')
        self.assertFalse(result)

        # test negative path, write_mode not available, without logger
        write_mode = 's'
        with self.assertLogs(logger_name, level="WARNING") as log:
            result = ModuleHelper.save_list_to_file(path='file.txt',
                                                    content=content,
                                                    mode=write_mode,
                                                    logger=logger)
            self.assertFalse(result)

        # first logger output comes from "check_option_values" function,
        # second output comes from "save_list_to_file"
        self.assertEqual(len(log.output), 2)
        self.assertEqual(len(log.records), 2)
        self.assertIn('WARNING:Test Logger:{} is no valid option of {}'.
                      format(write_mode, ['a', 'w']),
                      log.output[-1])

        #
        # Test OSError
        #
        # test OSError
        with TemporaryDirectory() as dp:
            result = ModuleHelper.save_list_to_file(path=dp,
                                                    content=content)
            self.assertFalse(result)

        # test OSError with logger
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with TemporaryDirectory() as dp:
                result = ModuleHelper.save_list_to_file(path=dp,
                                                        content=content,
                                                        logger=logger)
                self.assertFalse(result)

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

        # test OSError raising
        with self.assertRaises(OSError) as context:
            with TemporaryDirectory() as dp:
                result = ModuleHelper.save_list_to_file(path=dp,
                                                        content=content,
                                                        raise_error=True)
                self.assertFalse(result)

        self.assertIn("Is a directory: '{}'".format(dp),
                      str(context.exception))

        # test OSError with logger raising
        with self.assertLogs(logger_name, level="DEBUG") as log:
            with self.assertRaises(OSError) as context:
                with TemporaryDirectory() as dp:
                    result = ModuleHelper.save_list_to_file(path=dp,
                                                            content=content,
                                                            logger=logger,
                                                            raise_error=True)
                    self.assertFalse(result)

            self.assertIn("Is a directory: '{}'".format(dp),
                          str(context.exception))

        self.assertEqual(len(log.output), 1)
        self.assertEqual(len(log.records), 1)
        self.assertIn('WARNING:Test Logger:Failed due to OSError:',
                      log.output[0])

    def tearDown(self) -> None:
        """Run after every test method"""
        pass


class MockFunction:
    """Define Mock for functions to explore the details on their execution"""
    def __init__(self, func):
        self.func = func

    def __call__(mock_instance, *args, **kwargs):
        # Add locals() to function's return
        code = re.sub('[\\s]return\\b', ' return locals(), ',
                      dedent(inspect.getsource(mock_instance.func)))
        code = code + (f'\nloc, ret = {mock_instance.func.__name__}(*args, '
                       '**kwargs)')
        loc = {'args': args, 'kwargs': kwargs}
        exec(code, mock_instance.func.__globals__, loc)

        # Put execution locals into mock instance
        for location, value in loc['loc'].items():
            setattr(mock_instance, location, value)

        return loc['ret']


if __name__ == '__main__':
    unittest.main()
