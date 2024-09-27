from unittest                                                import TestCase
from osbot_aws.deploy.Deploy_Lambda                          import Deploy_Lambda
from cbr_deploy_custom_sites.lambdas.dev.lambda__hello_world import run


class test_lambda__hello_world(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.handler = run
        cls.deploy_lambda = Deploy_Lambda(handler=cls.handler)


    def test_1__setUpClass(self):
        assert self.deploy_lambda.exists() is False

    def test_2__setup_bucket(self):
        osbot_setup = self.deploy_lambda.osbot_setup
        bucket_name = osbot_setup.s3_bucket_lambdas
        osbot_setup.set_up_buckets()
        assert osbot_setup.s3.bucket_exists(bucket_name) is True

    def test_3__create(self):
        self.deploy_lambda.deploy()
        assert self.deploy_lambda.exists() is True

    def test_4__invoke(self):
        payload = dict(name='world')
        assert self.deploy_lambda.invoke(payload) == '\nFrom lambda code, hello world\n'

    def test_5__delete(self):
        assert self.deploy_lambda.delete() is True

