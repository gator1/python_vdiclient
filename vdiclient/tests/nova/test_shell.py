#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

#import prettytable
import re
import six
import sys

#from distutils.version import StrictVersion

import fixtures
import mock
from testtools import matchers

import vdiclient.api.client
from vdiclient.openstack.common.apiclient import exceptions
import vdiclient.shell
from vdiclient.tests.nova import utils

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where'}

FAKE_ENV2 = {'OS_USERNAME': 'username',
             'OS_PASSWORD': 'password',
             'OS_TENANT_ID': 'tenant_id',
             'OS_AUTH_URL': 'http://no.where'}


class FakePlugin:
    name = 'fake'
    versions = ['1.0', ]
    title = 'a fake plugin'


class FakePluginManager:
    def list(self):
        return (FakePlugin(),)


class FakeImage:
    name = 'fake'
    id = 'aaa-bb-ccc'
    username = 'you'
    description = None
    tags = []


class FakeImageManager:
    def list(self):
        return (FakeImage(),)


class FakePluginClient:
    def __init__(self, *args, **kwargs):
        self.plugins = FakePluginManager()
        self.images = FakeImageManager()


class ShellTest(utils.TestCase):

    def make_env(self, exclude=None, fake_env=FAKE_ENV):
        env = dict((k, v) for k, v in fake_env.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def setUp(self):
        super(ShellTest, self).setUp()
# NA atm
#       self.useFixture(fixtures.MonkeyPatch(
#                       'novaclient.client.get_client_class',
#                       mock.MagicMock))
#       self.nc_util = mock.patch('novaclient.utils.isunauthenticated').start()
#       self.nc_util.return_value = False

    def shell(self, argstr, exitcodes=(0,)):
        orig = sys.stdout
        orig_stderr = sys.stderr
        try:
            sys.stdout = six.StringIO()
            sys.stderr = six.StringIO()
            _shell = vdiclient.shell.OpenStackSaharaShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertIn(exc_value.code, exitcodes)
        finally:
            stdout = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig
            stderr = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = orig_stderr
        return (stdout, stderr)

    def test_help_unknown_command(self):
        self.assertRaises(exceptions.CommandError, self.shell, 'help foofoo')

# NA
#    def test_invalid_timeout(self):
#        for f in [0, -1, -10]:
#            cmd_text = '--timeout %s' % (f)
#            stdout, stderr = self.shell(cmd_text, exitcodes=[0, 2])
#            required = [
#                'argument --timeout: %s must be greater than 0' % (f),
#            ]
#            for r in required:
#                self.assertIn(r, stderr)

    def test_help(self):
        required = [
            '.*?^usage: sahara',
            '.*?^\s+plugin-list\s+Print a list of available plugins.',
            '.*?^See "sahara help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('help')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: sahara plugin-list',
            '.*?^Print a list of available plugins.',
        ]
        stdout, stderr = self.shell('help plugin-list')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_no_options(self):
        required = [
            '.*?^usage: sahara',
            '.*?^\s+plugin-list\s+Print a list of available plugins.',
            '.*?^See "sahara help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_bash_completion(self):
        stdout, stderr = self.shell('bash-completion')
        # just check we have some output
        required = [
            '.*help',
            '.*plugin-list',
            '.*plugin-show',
            '.*--name']
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_no_username(self):
        required = ('You must provide a username'
                    ' via either --os-username or env[OS_USERNAME]',)
        self.make_env(exclude='OS_USERNAME')
        try:
            self.shell('plugin-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_no_tenant_name(self):
        required = ('You must provide a tenant name or tenant id'
                    ' via --os-tenant-name, --os-tenant-id,'
                    ' env[OS_TENANT_NAME] or env[OS_TENANT_ID]',)
        self.make_env(exclude='OS_TENANT_NAME')
        try:
            self.shell('plugin-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_no_tenant_id(self):
        required = ('You must provide a tenant name or tenant id'
                    ' via --os-tenant-name, --os-tenant-id,'
                    ' env[OS_TENANT_NAME] or env[OS_TENANT_ID]',)
        self.make_env(exclude='OS_TENANT_ID', fake_env=FAKE_ENV2)
        try:
            self.shell('plugin-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_no_auth_url(self):
        required = ('You must provide an auth url'
                    ' via either --os-auth-url or env[OS_AUTH_URL] or'
                    ' specify an auth_system which defines a default url'
                    ' with --os-auth-system or env[OS_AUTH_SYSTEM]',)
        self.make_env(exclude='OS_AUTH_URL')
        try:
            self.shell('plugin-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

#    @mock.patch('sys.stdin', side_effect=mock.MagicMock)
#    @mock.patch('getpass.getpass', return_value='password')
#    def test_password(self, mock_getpass, mock_stdin):
    @mock.patch('vdiclient.api.client.Client', FakePluginClient)
    def test_password(self):
        ex = (
            '+------+----------+---------------+\n'
            '| name | versions | title         |\n'
            '+------+----------+---------------+\n'
            '| fake | 1.0      | a fake plugin |\n'
            '+------+----------+---------------+\n'
        )
#        self.make_env(exclude='OS_PASSWORD')
        self.make_env()
        stdout, stderr = self.shell('plugin-list')
        self.assertEqual((stdout + stderr), ex)

#    @mock.patch('sys.stdin', side_effect=mock.MagicMock)
#    @mock.patch('getpass.getpass', side_effect=EOFError)
#    def test_no_password(self, mock_getpass, mock_stdin):
    def test_no_password(self):
        required = ('Expecting a password provided'
                    ' via either --os-password, env[OS_PASSWORD],'
                    ' or prompted response',)
        self.make_env(exclude='OS_PASSWORD')
        try:
            self.shell('plugin-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

# TODO(mattf) Only one version of API right now
#    def _test_service_type(self, version, service_type, mock_client):
#        if version is None:
#            cmd = 'list'
#        else:
#            cmd = '--os-compute-api-version %s list' % version
#        self.make_env()
#        self.shell(cmd)
#        _, client_kwargs = mock_client.call_args
#        self.assertEqual(service_type, client_kwargs['service_type'])
#
#    @mock.patch('novaclient.client.Client')
#    def test_default_service_type(self, mock_client):
#        self._test_service_type(None, 'compute', mock_client)
#
#    @mock.patch('novaclient.client.Client')
#    def test_v1_1_service_type(self, mock_client):
#        self._test_service_type('1.1', 'compute', mock_client)
#
#    @mock.patch('novaclient.client.Client')
#    def test_v2_service_type(self, mock_client):
#        self._test_service_type('2', 'compute', mock_client)
#
#    @mock.patch('novaclient.client.Client')
#    def test_v3_service_type(self, mock_client):
#        self._test_service_type('3', 'computev3', mock_client)
#
#    @mock.patch('novaclient.client.Client')
#    def test_v_unknown_service_type(self, mock_client):
#        self._test_service_type('unknown', 'compute', mock_client)

    @mock.patch('vdiclient.api.client.Client', FakePluginClient)
    def test_image_list(self):
        ex = (
            '+------+------------+----------+------+-------------+\n'
            '| name | id         | username | tags | description |\n'
            '+------+------------+----------+------+-------------+\n'
            '| fake | aaa-bb-ccc | you      |      | None        |\n'
            '+------+------------+----------+------+-------------+\n'
        )
        self.make_env()
        stdout, stderr = self.shell('image-list')
        self.assertEqual((stdout + stderr), ex)
