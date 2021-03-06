# Copyright (c) 2015 Cisco Systems
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
from barbican.tests import utils
from functionaltests.api import base
from functionaltests.api.v1.behaviors import container_behaviors
from functionaltests.api.v1.behaviors import secret_behaviors
from functionaltests.api.v1.models import container_models
from functionaltests.api.v1.models import secret_models
from functionaltests.common import config


CONF = config.get_config()
admin_a = CONF.rbac_users.admin_a
creator_a = CONF.rbac_users.creator_a
observer_a = CONF.rbac_users.observer_a
auditor_a = CONF.rbac_users.auditor_a

admin_b = CONF.rbac_users.admin_b
creator_b = CONF.rbac_users.creator_b
observer_b = CONF.rbac_users.observer_b
auditor_b = CONF.rbac_users.auditor_b


test_data_rbac_read_secret = {
    'with_admin_a': {'user': admin_a, 'expected_return': 200},
    'with_creator_a': {'user': creator_a, 'expected_return': 200},
    'with_observer_a': {'user': observer_a, 'expected_return': 200},
    'with_auditor_a': {'user': auditor_a, 'expected_return': 403},
    'with_admin_b': {'user': admin_b, 'expected_return': 403},
    'with_creator_b': {'user': creator_b, 'expected_return': 403},
    'with_observer_b': {'user': observer_b, 'expected_return': 403},
    'with_auditor_b': {'user': auditor_b, 'expected_return': 403},
}


test_data_rbac_read_container = {
    'with_admin_a': {'user': admin_a, 'expected_return': 200},
    'with_creator_a': {'user': creator_a, 'expected_return': 200},
    'with_observer_a': {'user': observer_a, 'expected_return': 200},
    'with_auditor_a': {'user': auditor_a, 'expected_return': 200},
    'with_admin_b': {'user': admin_b, 'expected_return': 403},
    'with_creator_b': {'user': creator_b, 'expected_return': 403},
    'with_observer_b': {'user': observer_b, 'expected_return': 403},
    'with_auditor_b': {'user': auditor_b, 'expected_return': 403},
}


@utils.parameterized_test_case
class RbacTestCase(base.TestCase):
    """Functional tests exercising RBAC Policies"""
    def setUp(self):
        super(RbacTestCase, self).setUp()
        self.secret_behaviors = secret_behaviors.SecretBehaviors(self.client)
        self.container_behaviors = container_behaviors.ContainerBehaviors(
            self.client)

    def tearDown(self):
        self.secret_behaviors.delete_all_created_secrets()
        self.container_behaviors.delete_all_created_containers()
        super(RbacTestCase, self).tearDown()

    @utils.parameterized_dataset(test_data_rbac_read_secret)
    def test_rbac_read_secret(self, user, expected_return):
        secret_ref = self.store_secret()
        status = self.get_secret(secret_ref, user_name=user)
        self.assertEqual(expected_return, status)

    @utils.parameterized_dataset(test_data_rbac_read_container)
    def test_rbac_read_container(self, user, expected_return):
        container_ref = self.store_container()
        status = self.get_container(container_ref, user_name=user)
        self.assertEqual(expected_return, status)

# ----------------------- Helper Functions ---------------------------
    def store_secret(self, user_name=creator_a, admin=admin_a):
        test_model = secret_models.SecretModel(
            **get_default_secret_data())
        resp, secret_ref = self.secret_behaviors.create_secret(
            test_model, user_name=user_name, admin=admin)
        self.assertEqual(201, resp.status_code)
        return secret_ref

    def get_secret(self, secret_ref, user_name=creator_a):
        resp = self.secret_behaviors.get_secret(
            secret_ref, 'application/octet-stream',
            user_name=user_name)
        return resp.status_code

    def store_container(self, user_name=creator_a, admin=admin_a):
        secret_ref = self.store_secret(user_name=user_name, admin=admin)

        test_model = container_models.ContainerModel(
            **get_container_req(secret_ref))
        resp, container_ref = self.container_behaviors.create_container(
            test_model, user_name=user_name, admin=admin)
        self.assertEqual(201, resp.status_code)
        return container_ref

    def get_container(self, container_ref, user_name=creator_a):
        resp = self.container_behaviors.get_container(
            container_ref, user_name=user_name)
        return resp.status_code


# ----------------------- Support Functions ---------------------------
def get_default_secret_data():
    return {
        "name": "AES key",
        "expiration": "2018-02-28T19:14:44.180394",
        "algorithm": "aes",
        "bit_length": 256,
        "mode": "cbc",
        "payload": get_default_payload(),
        "payload_content_type": "application/octet-stream",
        "payload_content_encoding": "base64",
    }


def get_default_payload():
    return 'Z0Y2K2xMb0Yzb2hBOWFQUnB0KzZiUT09'


def get_container_req(secret_ref):
    return {"name": "testcontainer",
            "type": "generic",
            "secret_refs": [{'name': 'secret1', 'secret_ref': secret_ref}]}
