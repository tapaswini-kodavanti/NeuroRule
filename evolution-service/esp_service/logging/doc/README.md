# Structured logging for ESP

Logs are written in JSON format to `stdout` by the ESP service. The AWS infrastructure (ECS/Fargate) siphons `stdout`
and copies the logs to CloudWatch. From there, a Lambda function ETLs the logs over to ElasticSearch, where they can
be queried directly or via the Kibana user interface.

Here's a sample log:

```json
{"timestamp": "2019-05-22T11:47:14.859893", "source": "esp", "message_type": "Other", "message": "AWS credentials found. Experiment results will be persisted to S3 bucket: esp-models"}
```

Sample query to ElasticSearch:

```bash
curl -i -X POST 'https://search-leaf-esp-3heu6ttabrkx5mjnjb7x5qci7m.us-west-2.es.amazonaws.com/cwl-2019.05.18/_search?pretty=true' \
-H "Content-Type: application/json" \
--data-binary @es_query.json
```

Note this uses the `es_query.json` file for the query parameters.

Sample response -- this is only the first item returned (for brevity):

```json
{
        "_index" : "cwl-2019.05.18",
        "_type" : "esp",
        "_id" : "34749354597451636417268949463123868948938028405529313353",
        "_score" : 1.9616585,
        "_source" : {
          "timestamp" : "2019-05-18T21:29:11.478337",
          "source" : "esp",
          "message_type" : "Metrics",
          "message" : "Evaluated population",
          "extra_properties" : {
            "experiment_id" : "FlappyBirdDarren2",
            "generation" : 8,
            "candidates" : {
              "1_8" : {
                "identity" : "(none)",
                "model_file" : "s3://esp-models/FlappyBirdDarren2/8/20190518-2129/1_8.json",
                "metrics" : {
                  "score" : 89
                }
              },
              "2_3" : {
                "identity" : "1_7~CUW~1_5#MGNP",
                "model_file" : "s3://esp-models/FlappyBirdDarren2/8/20190518-2129/2_3.json",
                "metrics" : {
                  "score" : 78
                }
              }
            }
          },
          "@id" : "34749354597451636417268949463123868948938028405529313353",
          "@timestamp" : "2019-05-18T21:29:11.478Z",
          "@message" : "{\"timestamp\": \"2019-05-18T21:29:11.478337\", \"source\": \"esp\", \"message_type\": \"Metrics\", \"message\": \"Evaluated population\", \"extra_properties\": {\"experiment_id\": \"FlappyBirdDarren2\", \"generation\": 8, \"candidates\": {\"1_8\": {\"identity\": \"(none)\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/1_8.json\", \"metrics\": {\"score\": 89.0}}, \"2_3\": {\"identity\": \"1_7~CUW~1_5#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/2_3.json\", \"metrics\": {\"score\": 78.0}}, \"8_3\": {\"identity\": \"7_4~CUW~1_8#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_3.json\", \"metrics\": {\"score\": 63.0}}, \"8_4\": {\"identity\": \"7_3~CUW~7_7#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_4.json\", \"metrics\": {\"score\": 34.0}}, \"8_5\": {\"identity\": \"1_8~CUW~7_3#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_5.json\", \"metrics\": {\"score\": 34.0}}, \"8_6\": {\"identity\": \"1_8~CUW~7_5#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_6.json\", \"metrics\": {\"score\": 63.0}}, \"8_7\": {\"identity\": \"7_9~CUW~7_6#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_7.json\", \"metrics\": {\"score\": 63.0}}, \"8_8\": {\"identity\": \"1_8~CUW~7_8#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_8.json\", \"metrics\": {\"score\": 63.0}}, \"8_9\": {\"identity\": \"7_7~CUW~7_3#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_9.json\", \"metrics\": {\"score\": 77.0}}, \"8_10\": {\"identity\": \"7_7~CUW~7_9#MGNP\", \"model_file\": \"s3://esp-models/FlappyBirdDarren2/8/20190518-2129/8_10.json\", \"metrics\": {\"score\": 63.0}}}}}",
          "@owner" : "634208487213",
          "@log_group" : "esp",
          "@log_stream" : "grpc/esp-service/ec13960a-d593-4766-81c6-1be23a8ea480"
        }
      }
```

From this returned JSON, you can extract metrics and other candidate info. The JSON parsing tool `jq` can be useful for
this kind of analysis.
