# todoist-serverless-lambda

A Todoist-Webhook Integration to create tasks based on specific events

## Requirements

* This service requires Python 3.9+
* Deployment requires serverless-framework (serverless@1.75.1) with Node.js 12.x

## Installation

1. Install [Serverless framework](https://serverless.com/) using their [install instructions](https://serverless.com/learn/quick-start/#installing-serverless)

Add the serverless-python-requirements plugin
https://serverless.com/blog/serverless-python-packaging/

```bash
(venv) $ npm init
This utility will walk you through creating a package.json file.

...Truncated...

Is this ok? (yes) yes

(venv) $ npm install --save serverless-python-requirements
```

2. Save your Todoist API key and Clientsecret as an [SSM Parameter](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html)
    ```
    aws ssm put-parameter --name TodoistApiKey --type SecureString --value <your API key>
    aws ssm put-parameter --name TodoistClientsecret --type SecureString --value <your Clientsecret>
    ```

3. Deploy the function
    ```
    serverless deploy -s prod
    ```
## Usage
1. Register App Integration at [Todoist Developer Appconsole](https://developer.todoist.com/appconsole.html)

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Documentation
### Incoming Requests
Delivered via an [Example Event from an Application Load Balancer](https://docs.aws.amazon.com/lambda/latest/dg/lambda-services.html)
```json 
{
    "requestContext": {
        "elb": {
            "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-2:123456789012:targetgroup/lambda-279XGJDqGZ5rsrHC2Fjr/49e9d65c45c6791a"
        }
    },
    "httpMethod": "GET",
    "path": "/lambda",
    "queryStringParameters": {
        "query": "1234ABCD"
    },
    "headers": {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip",
        "accept-language": "en-US,en;q=0.9",
        "connection": "keep-alive",
        "host": "lambda-alb-123578498.us-east-2.elb.amazonaws.com",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "x-amzn-trace-id": "Root=1-5c536348-3d683b8b04734faae651f476",
        "x-forwarded-for": "72.12.164.125",
        "x-forwarded-port": "80",
        "x-forwarded-proto": "http",
        "x-imforwards": "20"
    },
    "body": "",
    "isBase64Encoded": false
}
```
### Contents of the Todoist Event
See more at https://developer.todoist.com/sync/v8/#webhooks
```json
POST /payload HTTP/1.1

Host: your_callback_url_host
Content-Type: application/json
X-Todoist-Hmac-SHA256: UEEq9si3Vf9yRSrLthbpazbb69kP9+CZQ7fXmVyjhPs=

{
    "event_name": "item:completed",
    "initiator": {
        "is_premium": true,
        "image_id": "abc",
        "id": 1,
        "full_name": "Ben Matheja",
        "email": "post@benmatheja.de"
    },
    "user_id": 1,
    "event_data": {
        "due_date": "Tue 23 May 2017 05:00:00 +0000",
        "assigned_by_uid": null,
        "is_recurring": 0,
        "is_archived": 0,
        "labels": [
            2
        ],
        "sync_id": null,
        "datetime": null,
        "content": "Kommen Zeit notieren",
        "in_history": 0,
        "timezone": null,
        "date": null,
        "checked": 0,
        "date_lang": "en",
        "id": 3,
        "priority": 3,
        "indent": 1,
        "date_added": "Tue 04 Apr 2017 17:52:20 +0000",
        "user_id": 4,
        "url": "https:\/\/todoist.com\/showTask?id=5",
        "is_deleted": 0,
        "item_order": 9,
        "datetime_utc": null,
        "parent_id": null,
        "due_date_utc": "Tue 23 May 2017 05:00:00 +0000",
        "responsible_uid": null,
        "project_id": 6,
        "collapsed": 0,
        "date_string": "every workday AT 7"
    }
}
```
## History

TODO: Write history

## Credits
TODO: Write credits

## License
TODO: Write license