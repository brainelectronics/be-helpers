# BE Helpers

[![Downloads](https://pepy.tech/badge/be-helpers)](https://pepy.tech/project/be-helpers)
![Release](https://img.shields.io/github/v/release/brainelectronics/be-helpers?include_prereleases&color=success)
![Python](https://img.shields.io/badge/python3-Ok-green.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/github/brainelectronics/be-helpers/branch/main/graph/badge.svg)](https://app.codecov.io/github/brainelectronics/be-helpers)

Custom brainelectronics python helper modules

---------------

## General

Collection of custom brainelectronics specific python helper modules.

<!-- MarkdownTOC -->

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
	- [Unittests](#unittests)
- [Credits](#credits)

<!-- /MarkdownTOC -->


## Installation

```bash
pip install be-helpers
```

## Usage

```python
from be_helpers import ModuleHelper
import time
from pathlib import Path

# default name is 'be_helpers.module_helper'
my_logger = ModuleHelper.create_logger()

# set logger level to INFO
ModuleHelper.set_logger_verbose_level(logger=my_logger, verbose_level=3)

# check 'a' to be an option of ['a', 'b', 'c'], result will be True
result = ModuleHelper.check_option_values(options=['a', 'b', 'c'], option='a')
print('"a" is an option of ["a", "b", "c"]: {}'.format(result))
# "a" is an option of ["a", "b", "c"]: True

# get current unix timestamp and format it
now = ModuleHelper.get_unix_timestamp()
time_format = "%H:%M:%S"
print('{}'.format(ModuleHelper.format_timestamp(timestamp=now, format=time_format)))
# 11:30:01

# create a random character number string of length 10
print('{}'.format(ModuleHelper.get_random_string(length=10)))
# 235LS5AY6BPC

# convert a string to a "uint16_t" list, useful for Modbus communications
result = ModuleHelper.convert_string_to_uint16t(content="test")
print('"test" as uint16_t: {}'.format(result))
# "test" as uint16_t: [29797, 29556]

# check for valid files or folders
here = ModuleHelper.get_full_path('.')
ModuleHelper.check_file(here / 'README.md', '.md')
# True

ModuleHelper.check_folder(here)
# True

# load YAML or JSON files as dictionaries
config = ModuleHelper.load_dict_from_file(here / 'tests/data/valid.json')
config = ModuleHelper.load_dict_from_file(here / 'tests/data/valid.yaml')
# {'key': 'val', 'key2': {'key_nested': 'val_nested'}, 'key3': ['asdf', 123, {'key4': 'val4'}]}

# save dictionaries as JSON or YAML files
ModuleHelper.save_dict_to_file(path=here / 'example/cfg.json', content=config)
ModuleHelper.save_dict_to_file(path=here / 'example/cfg.yaml', content=config)
# True
```

## Contributing

### Unittests

Run the unittests locally with the following command after installing this
package in a virtual environment

```bash
# run all tests
nose2 --config tests/unittest.cfg

# run only one specific tests
nose2 tests.test_module_helper.TestModuleHelper.test_set_logger_verbose_level
```

Generate the coverage files with

```bash
python create_report_dirs.py
coverage html
```

The coverage report is placed at `be-helpers/reports/coverage/html/index.html`

## Credits

Based on the [PyPa sample project][ref-pypa-sample].

<!-- Links -->
[ref-pypa-sample]: https://github.com/pypa/sampleproject
