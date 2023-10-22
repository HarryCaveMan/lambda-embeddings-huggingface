from boto3 import session
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(
        prog="CreateNewUsagePlanWithKey",
        description="Creates a new usage plan with key for an AWS API gateway api"
    )
    parser.add_argument(
        "-p","--aws-profile",
        type=str,
        help="The AWS profile to use for the client session"
    )
    parser.add_argument(
        "-r","--aws-region",
        type=str,
        default="us-east-1",
        help="The AWS profile to use for the client session"
    )
    parser.add_argument(
        "-g","--gateway-id",
        type=str,
        help="The api gateway id to create the key and usage plan for"
    )
    parser.add_argument(
        "-n","--usage-plan-name",
        type=str,
        help="The name to give the usage plan (will be propagated to the key with a \"_key\" suffix)"
    )
    return parser.parse_args().__dict__

def create_or_update_usage_plan(client,usage_plan_name,api_id) -> str:
    res = client.create_usage_plan(
        name=usage_plan_name,
        description=f"Usage plan {usage_plan_name} for API {api_id}",
        apiStages=[
            {
                "apiId": api_id,
                "stage": "api"
            }
        ]
    )
    return res["id"]

def create_api_key(client,usage_plan_id) -> (str,str):
    res = client.create_api_key(
        name=f"{usage_plan_id}_key",
        description=f"API key for usage plan {usage_plan_id}",
        enabled=True,
    )
    return res["id"],res["value"]

def create_usage_plan_key(client,usage_plan_id,key_id) -> None:
    client.create_usage_plan_key(
        usagePlanId=usage_plan_id,
        keyId=key_id,
        keyType="API_KEY"
    )

def main(aws_profile,aws_region,gateway_id,usage_plan_name) -> None:
    sess = session.Session(profile_name=aws_profile,region_name=aws_region)
    client = sess.client('apigateway')
    usage_plan_id = create_or_update_usage_plan(client,usage_plan_name,gateway_id)
    key_id,key_value = create_api_key(client,usage_plan_id)
    create_usage_plan_key(client,usage_plan_id,key_id)
    print(f"Successfully created usage plan, new key: {key_value}")

if __name__ == "__main__":
    args = parse_args()
    main(**args)