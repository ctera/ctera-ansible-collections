# pylint: disable=protected-access

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is licensed under the Apache License 2.0.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright 2020, CTERA Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import unittest.mock as mock
import munch

try:
    from cterasdk import CTERAException, portal_types
except ImportError:  # pragma: no cover
    pass  # caught by ctera_common

from ansible_collections.ctera.ctera.plugins.modules.ctera_portal_folder_group import CteraPortalFolderGroup
import tests.ut.mocks.ctera_portal_base_mock as ctera_portal_base_mock
from tests.ut.base import BaseTest


class TestCteraPortalFolderGroup(BaseTest):

    def setUp(self):
        super().setUp()
        ctera_portal_base_mock.mock_bases(self, CteraPortalFolderGroup)

    def test__execute(self):
        for is_present in [True, False]:
            self._test__execute(is_present)

    @staticmethod
    def _test__execute(is_present):
        folder_group = CteraPortalFolderGroup()
        folder_group.parameters = dict(state='present' if is_present else 'absent')
        folder_group._get_folder_group = mock.MagicMock(return_value=dict())
        folder_group._ensure_present = mock.MagicMock()
        folder_group._ensure_absent = mock.MagicMock()
        folder_group._execute()
        if is_present:
            folder_group._ensure_present.assert_called_once_with(mock.ANY)
            folder_group._ensure_absent.assert_not_called()
        else:
            folder_group._ensure_absent.assert_called_once_with(mock.ANY)
            folder_group._ensure_present.assert_not_called()

    def test_get_folder_group_exists(self):
        expected_fg_dict = dict(
            name='fg_name',
            owner=dict(name='admin')
        )
        returned_object = munch.Munch(
            dict(
                name=expected_fg_dict['name'],
                owner='objs/12/portal/PortalUser/%s' % expected_fg_dict['owner']['name']
            )
        )
        folder_group = CteraPortalFolderGroup()
        folder_group.parameters = dict(name=expected_fg_dict['name'])
        folder_group._ctera_portal.cloudfs.get = mock.MagicMock(return_value=returned_object)
        self.assertDictEqual(expected_fg_dict, folder_group._get_folder_group())

    def test__get_folder_group_doesnt_exist(self):
        folder_group = CteraPortalFolderGroup()
        folder_group.parameters = dict(name='admin')
        folder_group._ctera_portal.cloudfs.get = mock.MagicMock(side_effect=CTERAException(response=munch.Munch(code=404)))
        self.assertIsNone(folder_group._get_folder_group())

    def test_ensure_present(self):
        for is_present in [True, False]:
            for change_attributes in [True, False]:
                self._test_ensure_present(is_present, change_attributes)

    @staticmethod
    def _test_ensure_present(is_present, change_attributes):
        current_attributes = dict(
            name='fg_name',
            owner=dict(name='admin')
        )
        desired_attributes = copy.deepcopy(current_attributes)
        if change_attributes:
            desired_attributes['owner']['name'] = 'Tester'
        folder_group = CteraPortalFolderGroup()
        folder_group.parameters = desired_attributes
        folder_group._ensure_present(current_attributes if is_present else None)
        if is_present:
            folder_group._ctera_portal.cloudfs.mkfg.assert_not_called()
        else:
            folder_group._ctera_portal.cloudfs.mkfg.assert_called_with(
                desired_attributes['name'],
                user=portal_types.UserAccount(desired_attributes['owner']['name'])
            )

    def test_ensure_absent(self):
        for is_present in [True, False]:
            self._test_ensure_absent(is_present)

    @staticmethod
    def _test_ensure_absent(is_present):
        name = 'main'
        folder_group = CteraPortalFolderGroup()
        folder_group.parameters = dict(name=name)
        folder_group._ensure_absent(folder_group.parameters if is_present else None)
        if is_present:
            folder_group._ctera_portal.cloudfs.rmfg.assert_called_once_with(name)
        else:
            folder_group._ctera_portal.cloudfs.rmfg.assert_not_called()
