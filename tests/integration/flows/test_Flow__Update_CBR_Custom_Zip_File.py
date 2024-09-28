from typing                                                         import cast
from unittest                                                       import TestCase
from osbot_aws.AWS_Config                                           import aws_config
from osbot_utils.utils.Env import set_env

from osbot_utils.utils.Dev import pprint

from osbot_utils.helpers.flows.Flow                                 import Flow
from cbr_deploy_custom_sites.flows.Flow__Update_CBR_Custom_Zip_File import Flow__Update_CBR_Custom_Zip_File


class test_Flow__Update_CBR_Custom_Zip_File(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.flow_update_zip = Flow__Update_CBR_Custom_Zip_File()

    def setUp(self):
        self.flow = cast(Flow, self.flow_update_zip.create_flow())       # BUG: todo: figure out why this cast is needed
        aws_config.set_region('eu-west-1')                              # todo: make this temporary so that it doesn't impact other tests

    def test_execute(self):

        with self.flow_update_zip as _:
            _.s3_key                   = 'cbr-custom-websites/cbr_website_beta/dev__cbr_custom_portuguese.zip'
            _.s3_bucket                = '654654216424--cbr-deploy--eu-west-1'
            _.lambda_name              = 'dev__cbr_custom_portuguese'
            _.zip_file__gh_source_code = 'https://github.com/the-cyber-boardroom/cbr-custom--portuguese/archive/refs/heads/dev.zip'


        self.flow.execute()

        assert self.flow.flow_return_value == 'all done'

    def test_execute_from_env_vars(self):

        # with self.flow as _:
        #     _.execute()
        #     assert _.flow_error.args[0] == "'load_vars_from_env' failed and task raise_on_error was set to True. Stopping flow execution"

        set_env('FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_BUCKET'      , '654654216424--cbr-deploy--eu-west-1'                                                      )
        set_env('FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__LAMBDA_NAME'    , 'dev__cbr_custom_portuguese'                                                               )
        set_env('FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_KEY'         , 'cbr-custom-websites/cbr_website_beta/dev__cbr_custom_portuguese.zip'                      )
        set_env('FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__GH_SOURCE_CODE' ,  'https://github.com/the-cyber-boardroom/cbr-custom--portuguese/archive/refs/heads/dev.zip')
        with self.flow as _:
            _.execute()
            assert _.flow_return_value == 'all done'
        #assert self.flow

        #assert self.flow.flow_return_value == 'all done'
