# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import testtools

from vdiclient.api import base


class ResourceTest(testtools.TestCase):
    def test_create_resource(self):
        dict = {"name": "test"}
        resource = TestResource(None, dict)
        self.assertEqual("test", resource.name)
        self.assertEqual("Test Description", resource.description)

    def test_overwrite_default(self):
        dict = {"name": "test",
                "description": "Changed Description"}
        resource = TestResource(None, dict)
        self.assertEqual("test", resource.name)
        self.assertEqual("Changed Description", resource.description)
        self.assertEqual("extra", resource.extra)

    def test_create_dont_modify_info_dict(self):
        dict = {"name": "test",
                "description": "Changed Description"}
        dict_copy = dict.copy()
        resource = TestResource(None, dict)
        self.assertIsNotNone(resource)
        self.assertEqual(dict_copy, dict)

    def test_resource_str(self):
        dict = {"name": "test",
                "description": "Changed Description"}
        resource = TestResource(None, dict)
        rstr = str(resource)
        self.assertIn(resource.resource_name, rstr)
        self.assertIn("name", rstr)
        self.assertIn("description", rstr)
        self.assertIn("Changed Description", rstr)
        self.assertNotIn("Test Description", rstr)
        self.assertIn("extra", rstr)
        self.assertNotIn("manager", rstr)


class TestResource(base.Resource):
    resource_name = 'Test Resource'
    defaults = {'description': 'Test Description',
                'extra': "extra"}
