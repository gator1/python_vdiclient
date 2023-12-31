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

from vdiclient.api import base


class NodeGroupTemplate(base.Resource):
    resource_name = 'Node Group Template'


class NodeGroupTemplateManager(base.ResourceManager):
    resource_class = NodeGroupTemplate

    def _assign_field(self, name, plugin_name, hadoop_version, flavor_id,
                      description=None,
                      volumes_per_node=None, volumes_size=None,
                      node_processes=None, node_configs=None,
                      floating_ip_pool=None):

        data = {
            'name': name,
            'plugin_name': plugin_name,
            'hadoop_version': hadoop_version,
            'flavor_id': flavor_id,
            'node_processes': node_processes
        }

        self._copy_if_defined(data,
                              description=description,
                              node_configs=node_configs,
                              floating_ip_pool=floating_ip_pool)

        if volumes_per_node:
            data.update({"volumes_per_node": volumes_per_node,
                         "volumes_size": volumes_size})

        return data

    def create(self, name, plugin_name, hadoop_version, flavor_id,
               description=None, volumes_per_node=None, volumes_size=None,
               node_processes=None, node_configs=None, floating_ip_pool=None):

        data = self._assign_field(name, plugin_name, hadoop_version, flavor_id,
                                  description, volumes_per_node, volumes_size,
                                  node_processes, node_configs,
                                  floating_ip_pool)

        return self._create('/node-group-templates', data,
                            'node_group_template')

    def update(self, ng_template_id, name, plugin_name, hadoop_version,
               flavor_id, description=None, volumes_per_node=None,
               volumes_size=None, node_processes=None,
               node_configs=None, floating_ip_pool=None):

        data = self._assign_field(name, plugin_name, hadoop_version, flavor_id,
                                  description, volumes_per_node,
                                  volumes_size, node_processes,
                                  node_configs, floating_ip_pool)

        return self._update('/node-group-templates/%s' % ng_template_id, data,
                            'node_group_template')

    def list(self):
        return self._list('/node-group-templates', 'node_group_templates')

    def get(self, ng_template_id):
        return self._get('/node-group-templates/%s' % ng_template_id,
                         'node_group_template')

    def delete(self, ng_template_id):
        self._delete('/node-group-templates/%s' % ng_template_id)
