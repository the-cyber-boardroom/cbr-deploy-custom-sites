from osbot_aws.apis.Lambda                          import Lambda
from osbot_aws.aws.s3.S3                            import S3
from osbot_utils.helpers.flows.Flow import Flow

from osbot_utils.utils.Env import get_env

from osbot_utils.helpers.Zip_Bytes                  import Zip_Bytes
from osbot_utils.utils.Http                         import GET_bytes
from osbot_utils.utils.Misc                         import date_time_now
from osbot_utils.utils.Zip import zip_bytes__replace_file, zip_bytes__file_contents, zip_bytes__files, \
    zip_bytes__replace_files, zip_bytes__files_paths
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.helpers.flows.decorators.flow      import flow
from osbot_utils.helpers.flows.decorators.task      import task
from osbot_utils.base_classes.Type_Safe             import Type_Safe

ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_BUCKET      = 'FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_BUCKET'
ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__LAMBDA_NAME    = 'FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__LAMBDA_NAME'
ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_KEY         = 'FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_KEY'
ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__GH_SOURCE_CODE = 'FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__GH_SOURCE_CODE'


class Flow__Update_CBR_Custom_Zip_File(Type_Safe):
    s3_file_bytes           : bytes
    lambda_name             : str
    s3_key                  : str
    s3_bucket               : str
    zip_file__gh_source_code: str

    @cache_on_self
    def s3(self):
        return S3()

    @task()
    def load_vars_from_env(self):
        if not self.s3_key                  : self.s3_key                   = get_env(ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_KEY         , '')
        if not self.s3_bucket               : self.s3_bucket                = get_env(ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__S3_BUCKET      , '')
        if not self.lambda_name             : self.lambda_name              = get_env(ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__LAMBDA_NAME    , '')
        if not self.zip_file__gh_source_code: self.zip_file__gh_source_code = get_env(ENV_VAR__FLOW__UPDATE_CBR_CUSTOM_ZIP_FILE__GH_SOURCE_CODE , '')

        if not self.s3_key                  : raise ValueError("missing value for s3_key"                  )
        if not self.s3_bucket               : raise ValueError("missing value for s3_bucket"               )
        if not self.lambda_name             : raise ValueError("missing value for lambda_name"             )
        if not self.zip_file__gh_source_code: raise ValueError("missing value for zip_file__gh_source_code")

    @task()
    def check_s3_access(self):
        if self.s3().file_exists(self.s3_bucket, self.s3_key) is False:
            raise Exception("S3 error: file not found in S3: {self.s3_bucket}::{self.s3_key}")

    @task()
    def download__zip_file__cbr_custom__from_s3(self, flow_data: dict):
        self.s3_file_bytes = self.s3().file_bytes(self.s3_bucket, self.s3_key)
        flow_data['cbr_custom__s3__zip_bytes'] = self.s3_file_bytes

    @task()
    def download__zip_file__gh_source_code(self, flow_data: dict):
        zip_bytes = GET_bytes(self.zip_file__gh_source_code)
        flow_data['gh_source_code__zip_bytes'] = zip_bytes

    @task()
    def extract_custom_files_from_zip(self, flow_data: dict):
        base_path = 'cbr-custom--portuguese-dev/cbr_custom_portuguese/custom/'
        gh_zip_bytes = flow_data.get('gh_source_code__zip_bytes')
        with Zip_Bytes() as new_zip_file:
            for file_path, file_bytes in zip_bytes__files(gh_zip_bytes).items():
                if file_path.startswith(base_path) and file_path.endswith('/') is False:
                    new_file_path = file_path.replace(base_path, '')
                    new_zip_file.add_file(new_file_path, file_bytes)

        flow_data['cbr_custom__new__zip_bytes'] = new_zip_file.zip_bytes

    @task()
    def merge_gh_and_cbr_custom_zip_bytes(self, flow_data: dict):
        s3_zip_bytes  = flow_data['cbr_custom__s3__zip_bytes' ]
        new_zip_bytes = flow_data['cbr_custom__new__zip_bytes']
        new_zip_files = zip_bytes__files(new_zip_bytes)
        s3_updated_zip_bytes = zip_bytes__replace_files(s3_zip_bytes, new_zip_files)
        flow_data['cbr_custom__updated__zip_bytes'] = s3_updated_zip_bytes

    @task()
    def upload_changed_zip_file(self, flow_data: dict):
        s3_file_bytes = flow_data.get('cbr_custom__updated__zip_bytes')
        kwargs = {'file_body': s3_file_bytes,
                  'bucket'   : self.s3_bucket    ,
                  'key'      : self.s3_key       }
        if self.s3().file_upload_from_bytes(**kwargs) is False:
            raise Exception("Error uploading file to S3")
        print("zip with cbr_custom files uploaded to S3 ok")

    @task()
    def trigger_lambda_refresh(self):
        with Lambda(self.lambda_name) as _:
            env_vars = _.info().get('Configuration').get('Environment').get('Variables')
            env_vars['CBR_UPDATE_AT'] = date_time_now()
            _.env_variables = env_vars
            _.update_lambda_configuration()

    @task()
    def wait_for_lambda_update(self):
        with Lambda(self.lambda_name) as _:
            _.wait_for_function_update_to_complete()


    @flow()
    def create_flow(self) -> Flow:
        self.load_vars_from_env                     ()
        self.check_s3_access                        ()
        self.download__zip_file__cbr_custom__from_s3()
        self.download__zip_file__gh_source_code     ()
        self.extract_custom_files_from_zip          ()
        self.merge_gh_and_cbr_custom_zip_bytes      ()
        self.upload_changed_zip_file                ()
        self.trigger_lambda_refresh                 ()
        self.wait_for_lambda_update                 ()
        return 'all done'

if __name__ == '__main__':
    flow = Flow__Update_CBR_Custom_Zip_File().create_flow()
    flow.execute()
    flow.print_log_messages()