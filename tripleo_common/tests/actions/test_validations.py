# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import collections
from unittest import mock

from tripleo_common.actions import validations
from tripleo_common.tests import base


class GetPubkeyActionTest(base.TestCase):

    @mock.patch(
        'tripleo_common.actions.base.TripleOAction.get_workflow_client')
    def test_run_existing_pubkey(self, get_workflow_client_mock):
        mock_ctx = mock.MagicMock()
        mistral = mock.MagicMock()
        get_workflow_client_mock.return_value = mistral
        environment = collections.namedtuple('environment', ['variables'])
        mistral.environments.get.return_value = environment(variables={
            'public_key': 'existing_pubkey'
        })
        action = validations.GetPubkeyAction()
        self.assertEqual('existing_pubkey', action.run(mock_ctx))

    @mock.patch(
        'tripleo_common.actions.base.TripleOAction.get_workflow_client')
    @mock.patch('tripleo_common.utils.passwords.create_ssh_keypair')
    def test_run_no_pubkey(self, mock_create_keypair,
                           get_workflow_client_mock):
        mock_ctx = mock.MagicMock()
        mistral = mock.MagicMock()
        get_workflow_client_mock.return_value = mistral
        mistral.environments.get.side_effect = 'nope, sorry'
        mock_create_keypair.return_value = {
            'public_key': 'public_key',
            'private_key': 'private_key',
        }

        action = validations.GetPubkeyAction()
        self.assertEqual('public_key', action.run(mock_ctx))


class Enabled(base.TestCase):

    @mock.patch(
        'tripleo_common.actions.base.TripleOAction.get_workflow_client')
    def test_validations_enabled(self, get_workflow_client_mock):
        mock_ctx = mock.MagicMock()
        mistral = mock.MagicMock()
        get_workflow_client_mock.return_value = mistral
        mistral.environments.get.return_value = {}
        action = validations.Enabled()
        result = action._validations_enabled(mock_ctx)
        self.assertEqual(result, True)

    @mock.patch(
        'tripleo_common.actions.base.TripleOAction.get_workflow_client')
    def test_validations_disabled(self, get_workflow_client_mock):
        mock_ctx = mock.MagicMock()
        mistral = mock.MagicMock()
        get_workflow_client_mock.return_value = mistral
        mistral.environments.get.side_effect = Exception()
        action = validations.Enabled()
        result = action._validations_enabled(mock_ctx)
        self.assertEqual(result, False)

    @mock.patch(
        'tripleo_common.actions.validations.Enabled._validations_enabled')
    @mock.patch(
        'tripleo_common.actions.base.TripleOAction.get_workflow_client')
    def test_success_with_validations_enabled(self, get_workflow_client_mock,
                                              validations_enabled_mock):
        mock_ctx = mock.MagicMock()
        validations_enabled_mock.return_value = True
        action = validations.Enabled()
        action_result = action.run(mock_ctx)
        self.assertIsNone(action_result.error)
        self.assertEqual('Validations are enabled',
                         action_result.data['stdout'])

    @mock.patch(
        'tripleo_common.actions.validations.Enabled._validations_enabled')
    @mock.patch(
        'tripleo_common.actions.base.TripleOAction.get_workflow_client')
    def test_success_with_validations_disabled(self, get_workflow_client_mock,
                                               validations_enabled_mock):
        mock_ctx = mock.MagicMock()
        validations_enabled_mock.return_value = False
        action = validations.Enabled()
        action_result = action.run(mock_ctx)
        self.assertIsNone(action_result.data)
        self.assertEqual('Validations are disabled',
                         action_result.error['stdout'])
