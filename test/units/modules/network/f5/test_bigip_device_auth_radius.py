# -*- coding: utf-8 -*-
#
# Copyright: (c) 2019, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
import sys

if sys.version_info < (2, 7):
    pytestmark = pytest.mark.skip("F5 Ansible modules require Python >= 2.7")

from ansible.module_utils.basic import AnsibleModule

try:
    from library.modules.bigip_device_auth_radius import ApiParameters
    from library.modules.bigip_device_auth_radius import ModuleParameters
    from library.modules.bigip_device_auth_radius import ModuleManager
    from library.modules.bigip_device_auth_radius import ArgumentSpec
    from test.units.compat import unittest
    from test.units.compat.mock import Mock
    from test.units.compat.mock import patch
    from test.units.compat.utils import set_module_args
except ImportError:
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_device_auth_radius import ApiParameters
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_device_auth_radius import ModuleParameters
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_device_auth_radius import ModuleManager
    from ansible_collections.f5networks.f5_modules.plugins.modules.bigip_device_auth_radius import ArgumentSpec
    from ansible_collections.f5networks.f5_modules.tests.units.compat import unittest
    from ansible_collections.f5networks.f5_modules.tests.units.compat import Mock
    from ansible_collections.f5networks.f5_modules.tests.units.compat import patch
    from ansible_collections.f5networks.f5_modules.tests.units.utils import set_module_args


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            servers=['foo1', 'foo2'],
            retries=5,
            service_type='login',
            accounting_bug=False,
            fallback_to_local=True,
            use_for_auth=True,
        )
        p = ModuleParameters(params=args)

        assert '/Common/foo1' and '/Common/foo2' in p.servers
        assert p.retries == 5
        assert p.use_for_auth == 'yes'
        assert p.accounting_bug == 'disabled'
        assert p.service_type == "login"
        assert p.fallback_to_local == 'yes'

    def test_api_parameters(self):
        args = load_fixture('load_radius_config.json')

        p = ApiParameters(params=args)
        assert p.retries == 3
        assert p.service_type == 'authenticate-only'
        assert p.accounting_bug == 'disabled'
        assert p.servers == ['/Common/system_auth_name1']


class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()

    def test_create(self, *args):
        set_module_args(dict(
            servers=['foo1', 'foo2'],
            retries=5,
            service_type='login',
            accounting_bug=False,
            fallback_to_local=True,
            use_for_auth=True,
            state='present',
            provider=dict(
                password='admin',
                server='localhost',
                user='admin'
            )
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )

        # Override methods to force specific logic in the module to happen
        mm = ModuleManager(module=module)
        mm.exists = Mock(return_value=False)
        mm.create_on_device = Mock(return_value=True)
        mm.update_auth_source_on_device = Mock(return_value=True)
        mm.update_fallback_on_device = Mock(return_value=True)

        results = mm.exec_module()
        assert results['changed'] is True
        assert '/Common/foo1' and '/Common/foo2' in results['servers']
        assert results['retries'] == 5
        assert results['accounting_bug'] == 'disabled'
        assert results['service_type'] == 'login'
        assert results['fallback_to_local'] == 'yes'
