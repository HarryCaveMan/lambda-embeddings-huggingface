# Sentence Embeddings Lambda
Generic implementation of HuggingFace BERT sentence embeddings for AWS lambda. Uses ECR Image runtime with model and torch/transformers installed int othe image.

## Features
- Currently API key authentication is always on. You will need to run the `create_usage_plan.py` script to create a usage plan for your API after it is deployed or you will only see 403 responses
- Future releases will include a toggle switch for API key auth

## API
The API only has a single path for encoding a list of sentences into embedding vectors.

### Authentication
You will need to run `create_usage_plan.py` or create your own api key for the api. Then you will need to include the key in the `x-api-key` header in every request.

### `POST /api/encode`
#### `Content-type: application/json`
#### Request Schema
```json
{
    "crid":int,
    "sentences":[str]
}
```
#### Response Schema
```json
{
    "crid":int,
    "embeddings":[float]
}
```