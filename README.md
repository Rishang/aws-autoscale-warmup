# autoscaling warmup for ec2/fargate

---

# Problem statement

---

There are 2 parts in order to perform this process

1. `rulegen` serverless code to shedule cloudwatch events for autoscaling.

2. `rulegen-scale` serverless code which gets invoked by `rulegen` cloudwatch rules to perform autoscaling on defined autoscaling groups.

## logical flow

- sheduled events for multiple resource and time, autoscaling will be defined by use in for of json as the syntax defined in [rulegen](https://github.com/Rishang/onetime-aws-autoscale/tree/main/event_rule_gen)

- This json will be uploaded to s3 bucket, before uploading bucket-arn and file name has to be defined in `serverless.yml` file as defined in [rulegen](https://github.com/Rishang/onetime-aws-autoscale/tree/main/event_rule_gen)

- On s3 bucket put event for that file `rulegen` lambda will generate cloudwatch event rules based on shedules and minimum count defined in json file by the user.

- This rules will trigger next lambda [rulegen-scale](https://github.com/Rishang/onetime-aws-autoscale/tree/main/scale) which will perform task of modifing autoscaling minimum count of ec2/fargate and after updating autoscaling count, event rule will be removed as it was been made to run once only.


## Flow Diagram

![Diagram flow](https://raw.githubusercontent.com/Rishang/onetime-aws-autoscale/4c189bf643089604007a774c68184718603e1416/.github/images/customAutoScaling.svg)

## prerequisite
1. [Nodejs](https://nodejs.org/en/)
2. [npm](http://npmjs.org/install.sh)

To install nodejs [click here](https://github.com/nodesource/distributions)

---

## Steps for implementation

1. Install serverless on your local device.
        
    - `sudo npm install -G serverless`

    - Now inside git repo directory run: `npm i -D serverless-dotenv-plugin`

2. Create a s3 bucket on your aws account where you will upload your sheduled scaling json file.

3. provide required example variables values at `.env.dev` file as follows

        ENV_AWS_REGION="<YOUR-REGION>"
        ENV_AWS_PROFILE="<YOUR-PROFILE>"

        BUCKET_NAME="shedule-event-ec2"
        BUCKET_FILE="test.json"

4. run `serverless deploy`

This now in you aws account in s3 bucket `shedule-event-ec2` you can put scaling time shedules in file [example/shedule.json](https://github.com/Rishang/onetime-aws-autoscale/blob/main/example/shedule.json) 

same can be written in yaml as well like: [example/shedule.yml](https://github.com/Rishang/onetime-aws-autoscale/blob/main/example/shedule.yml)

like follows:

```yaml
---
- service_type: fargate
  scaling_group_name: service/cluster-wp/fastapi
  shedule_table:
    date: 30/11/2021
    shedule:
    - start: '16:40:00'
      end: '16:57:00'
      count: 4
    - start: '16:55:00'
      end: '17:57:00'
      count: 6
- service_type: ec2
  scaling_group_name: scl
  shedule_table:
    date: 30/11/2021
    shedule:
    - start: '16:10:00'
      end: '17:37:00'
      count: 4
    - start: '17:35:00'
      end: '18:57:00'
      count: 6

```
