from osbot_aws.deploy.Deploy_Lambda import Deploy_Lambda
from osbot_utils.base_classes.Type_Safe import Type_Safe

IMAGE_URI__FORMAT = '654654216424.dkr.ecr.eu-west-1.amazonaws.com/cbr-website-beta_lambda:{version}'

class CBR_Deploy__Custom_Sites__Lambda(Type_Safe):

    def image_uri(self, version):
        return IMAGE_URI__FORMAT.format(version=version)

    def create_lambda_function(self, function_name, image_version):
        lambda_deploy = Deploy_Lambda(handler=function_name)
        lambda_deploy.set_container_image(self.image_uri(image_version))
        #lambda_deploy.function_url()
        return lambda_deploy.deploy()

