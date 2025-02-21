import boto3
import os
import logging

# ロガーの設定
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

AGENT_ARN = os.environ['AGENT_ARN']

datasync = boto3.client('datasync')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    try:
        # DataSync Agentのステータス情報を取得
        response = datasync.describe_agent(AgentArn=AGENT_ARN)
        status = response['Status']

        # ステータスを数値に変換してCloudWatchのカスタムメトリクスに使用
        # ONLINEのステータスは1、OFFLINEは0
        status_value = 1 if status == 'ONLINE' else 0

        # CloudWatchカスタムメトリクスを送信
        cloudwatch.put_metric_data(
            Namespace='DataSync',
            MetricData=[
                {
                    'MetricName': 'DataSyncAgentStatus',
                    'Dimensions': [
                        {
                            'Name': 'AgentArn',
                            'Value': AGENT_ARN
                        },
                    ],
                    'Value': status_value,
                },
            ]
        )
        logger.info(f"DataSync Agent status: {status} ({status_value}) for Agent ARN: {AGENT_ARN}")

    except datasync.exceptions.InvalidRequestException as e:
        logger.error(f"InvalidRequestException: {e}")
        logger.error(f"Request ID: {e.response.get('ResponseMetadata', {}).get('RequestId')}")
        logger.error(f"Error Message: {e.response.get('Error', {}).get('Message')}")
        raise

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        raise

    return {
        'statusCode': 200,
        'body': f'DataSync Agent status check completed. Status: {status}'
    }