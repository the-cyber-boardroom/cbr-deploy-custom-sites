from typing                                                         import cast
from unittest                                                       import TestCase
from osbot_aws.AWS_Config                                           import aws_config
from osbot_utils.helpers.flows.Flow                                 import Flow
from cbr_deploy_custom_sites.flows.Flow__Update_CBR_Custom_Zip_File import Flow__Update_CBR_Custom_Zip_File


class test_Flow__Update_CBR_Custom_Zip_File(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.flow_update_zip = Flow__Update_CBR_Custom_Zip_File()

    def test_execute(self):
        aws_config.set_region('eu-west-1')

        with self.flow_update_zip as _:
            _.s3_key                   = 'cbr-custom-websites/cbr_website_beta/dev__cbr_custom_portuguese.zip'
            _.s3_bucket                = '654654216424--cbr-deploy--eu-west-1'
            _.lambda_name              = 'dev__cbr_custom_portuguese'
            _.zip_file__gh_source_code = 'https://github.com/the-cyber-boardroom/cbr-custom--portuguese/archive/refs/heads/dev.zip'

            flow = cast(Flow, _.create_flow())                  # BUG: todo: figure out why this cast is needed
            flow.execute()

            assert flow.flow_return_value == 'all done'
