# Copyright (c) 2014 Huawei Inc.
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

import six

from vdiclient.api import base
# from vdiclient.nova import base


class Groups(base.Resource):
    resource_name = 'Groups'


class GroupManager(base.ResourceManager):
    resource_class = Groups

    def _assert_variables(self, **kwargs):
        for var_name, var_value in six.iteritems(kwargs):
            if var_value is None:
                raise base.APIException('Group is missing field "%s"' %
                                        var_name)

    def create(self, name, description):
        data = {
            'name': name,
            'description': description
        }
        return self._create('/groups', data, 'group')

    def list(self):
        return self._list('/groups', 'groups')

    def get(self, group_id):
        return self._get('/groups/%s' % group_id, 'group')

    # def delete(self, cluster_id):
    #     self._delete('/clusters/%s' % cluster_id)
