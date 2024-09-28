from unittest                                                        import TestCase
from osbot_aws.AWS_Config                                            import aws_config
from osbot_aws.apis.Lambda                                           import Lambda
from osbot_utils.utils.Misc                                          import date_time_now
from cbr_deploy_custom_sites.deploy.CBR_Deploy__Custom_Sites__Lambda import CBR_Deploy__Custom_Sites__Lambda

class test_CBR_Deploy__Custom_Sites__Lambda(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cbr_deploy_lambda = CBR_Deploy__Custom_Sites__Lambda()

    def test_image_uri(self):
        with (self.cbr_deploy_lambda as _):
            assert _.image_uri('1.2.3') == '654654216424.dkr.ecr.eu-west-1.amazonaws.com/cbr-website-beta_lambda:1.2.3'

    def test_create_lambda_function(self):
        function_name = 'test_lambda__deploy__cbr_community'
        image_version = 'v0.192.0'
        with self.cbr_deploy_lambda as _:
            result = _.create_lambda_function(function_name=function_name, image_version=image_version)
            assert result is True

    # def test__change_deploy_zip_file(self):
    #     s3_key = 'cbr-custom-websites/cbr_website_beta/dev__cbr_custom_portuguese.zip'
    #     s3_bucket = '654654216424--cbr-deploy--eu-west-1'
    #     s3 = S3()
    #
    #     file_bytes = s3.file_bytes(s3_bucket, s3_key)
    #     pprint(len(file_bytes))
    #     file_to_change = "cbr_content/en/web-pages/demos/aaaaa.md"
    #     content        = b"# custom content"
    #     file_bytes = zip_bytes__replace_file(file_bytes, file_to_change, content)
        # files_to_remove = []
        # for file_path in zip_bytes__files(file_bytes):
        #     if (file_path.startswith('cbr_content/en/web-pages/demos'   ) or
        #         file_path.startswith('cbr_content/en/web-pages/dev'     ) or
        #         file_path.startswith('cbr_content/en/web-pages/support')):
        #         files_to_remove.append(file_path)
        # print(f"There are {len(files_to_remove)} files to remove")
        # file_bytes = zip_bytes__remove_files(file_bytes, files_to_remove)
        # pprint(list_set(zip_bytes__files(file_bytes)))
        #pprint(s3.file_upload_from_bytes(file_body=file_bytes, bucket=s3_bucket, key=s3_key))



    def test__nudge_lambda_function(self):
        aws_config.set_region('eu-west-1')
        lambda_name = 'dev__cbr_custom_portuguese'
        _lambda = Lambda(lambda_name)
        env_vars = _lambda.info().get('Configuration').get('Environment').get('Variables')
        env_vars['CBR_UPDATE_AT'] = date_time_now()
        _lambda.env_variables = env_vars
        assert _lambda.update_lambda_configuration         ().get('LastUpdateStatus') == 'InProgress'
        assert _lambda.wait_for_function_update_to_complete() == 'Successful'
