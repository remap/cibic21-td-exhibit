from datetime import datetime, timezone
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json


from boto3.dynamodb.types import TypeDeserializer
import decimal


from CibicObjects.secrets import AWS_Key, AWS_Secret


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def GetOneUser(user_id: str):
		_key = AWS_Key
		_secret = AWS_Secret

		_session = boto3.Session(aws_access_key_id=_key, aws_secret_access_key=_secret, region_name="us-west-1")
		_dynamodb = _session.resource('dynamodb')
		_table = _dynamodb.Table('cibic21-dynamodb-exhibit-filtered-journaling-data')
		response = _table.get_item( Key={
            'userId': user_id,
            'sortKey': 'profile'
            }
		)
		item = response['Item']

		return replace_decimals(item)

# print( GetOneUser('a744d900-2cbe-4bca-a364-397a415a7dac') )

def GetUserReflectionsWithDatetime(user_id: str, start: datetime, end: datetime):
		_key = AWS_Key
		_secret = AWS_Secret

		_session = boto3.Session(aws_access_key_id=_key, aws_secret_access_key=_secret, region_name="us-west-1")
		_dynamodb = _session.resource('dynamodb')
		_table = _dynamodb.Table('cibic21-dynamodb-exhibit-filtered-journaling-data')
		response = _table.query(
			KeyConditionExpression=Key('userId').eq(user_id) & Key("sortKey").between( f'reflection-{int(start.timestamp())}', f'reflection-{int(end.timestamp())}' )
		)
		items = response['Items']

		return replace_decimals(items)

# GetUserReflectionsWithDatetime('a744d900-2cbe-4bca-a364-397a415a7dac', datetime(2022, 6, 12), datetime(2022, 7, 5))

def GetReflectionsWithDatetime(start: datetime, end: datetime):
		_key = AWS_Key
		_secret = AWS_Secret

		_session = boto3.Session(aws_access_key_id=_key, aws_secret_access_key=_secret, region_name="us-west-1")
		_dynamodb = _session.resource('dynamodb')
		_table = _dynamodb.Table('cibic21-dynamodb-exhibit-filtered-journaling-data')
		response = _table.query(
			IndexName="type-created-index",
			KeyConditionExpression=Key('type').eq('reflection') & Key("created").between( start.astimezone(tz=timezone.utc).isoformat(), end.astimezone(tz=timezone.utc).isoformat() )
		)
		items = response['Items']
		

		return replace_decimals(items)
#GetReflectionsWithDatetime(datetime(2022, 6, 12), datetime(2022, 7, 5))
#print(GetReflectionsWithDatetime(datetime(2022, 6, 12), datetime(2022, 7, 5)))