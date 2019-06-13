# CustomResourceCognito

This repository contains a [CloudFormation custom resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html) for provisioning Cognito Domain name, Identity providers and App client settings.

While you can provision an [Cognito via CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cognito-userpool.html), you are not able to create Domain name, Identity providers and App client settings with CloudFormation. This custom resource fills the gap.

# Usage

There are two steps to using this custom resource: deploying the custom resource Lambda and using the custom resource in a CloudFormation template.

## Deploying the custom resource Lambda

The custom resource uses the [custom-resource-helper library](https://github.com/aws-cloudformation/custom-resource-helper) and is deployed using AWS SAM. [See here for instructions on installing SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).

To deploy, run the following commands:

```bash
$ pip3 install crhelper -t ./cognito_domain/
$ aws s3 mb s3://${S3-BUCKET-NAME}/
$ sam package \
    --output-template-file domain-packaged.yaml \
    --s3-bucket ${S3-BUCKET-NAME} \
    --s3-prefix cognito_domain_fn \
    --template-file cognito-domain.yaml
$ aws cloudformation deploy \
    --template-file domain-packaged.yaml \
    --stack-name cognito-domain-name \
    --capabilities CAPABILITY_IAM
```

This will deploy the Cognito Domain custom resource function and register its ARN as the `CognitoDomainFunction` Export.

```bash
$ pip3 install crhelper -t ./cognito_idp/
$ sam package \
    --output-template-file idp-packaged.yaml \
    --s3-bucket ${S3-BUCKET-NAME} \
    --s3-prefix cognito_idp_fn \
    --template-file cognito-idp.yaml
$ aws cloudformation deploy \
    --template-file idp-packaged.yaml \
    --stack-name cognito-idp-cr \
    --capabilities CAPABILITY_IAM    
```

This will deploy the Cognito Identity provider custom resource function and register its ARN as the `CognitoIdpFunction` Export.

```bash
$ pip3 install crhelper -t ./cognito_app_client/
$ sam package \
    --output-template-file app-packaged.yaml \
    --s3-bucket ${S3-BUCKET-NAME} \
    --s3-prefix cognito_app_fn \
    --template-file cognito-app.yaml
$ aws cloudformation deploy \
    --template-file app-packaged.yaml \
    --stack-name cognito-app-cr \
    --capabilities CAPABILITY_IAM
```
This will deploy the Cognito App client custom resource function and register its ARN as the `CognitoAppFunction` Export.

## Using the custom resource Lambda

The next step is to use the custom resource in a CloudFormation stack. There is an example in `template.yaml` in this directory.

To use it, run:

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name cognito-user-pool \
  --parameter-overrides Domain=${DOMAIN} ${CallbackURLs} ${SignOutURLSs}
```

For example:

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name cognito-user-pool \
  --parameter-overrides \
    Domain=uksb-test-01 \
    CallbackURLs=https://primary.app.url/login,https://secondary.app.url/login \
    SignOutURLSs=https://primary.app.url/logout,https://secondary.app.url/logout
```