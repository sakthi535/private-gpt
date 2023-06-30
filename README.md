
# Private-gpt : Flask Server


The flask server handles api endpoint for frontend application and connects to OpenAI Models for chat completion with the help of langchain framework.
## Deployment

Before deployment ensure to create a config file with required connection details for both elasticsearch database and OpenAI key.


Install requirements with,

```bash
  pip install requirements.txt  
```

Then start the server with 

```bash
  python server.py
```


## API Reference

#### Get all items

```http
  POST /addFiles
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `data` | `FileList` | Files to upload in bytes |

#### Get item

```http
  POST /eraseIndex
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `name`      | `string` | Name of index to be removed from alias |

```http
  GET /get_indices
```

| Response | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
|       | `List` | List of indices with alias |

```http
  GET /createResponse
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `question`      | `string` | User generated query |
| `index`      | `string` | Index associated with the query |


```http
  GET /add_index
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `name`      | `string` | Name of index to be added |




## Environment Variables

To run this project, you will need to add the following environment variables to your config.py file

```bash

config = {
    "cloud_id" : <Usage of cloud id is not supported currently by codebase>,
    "host" : <elastic-search address>,
    "auth" : [
        {
            "username" : <elasticsearch username>,
            "password" : <elasticsearch password>
        }   
    ],
    "application_name" : "romTalk",
    "Open-AI Key": <OpenAI Key>,
    "mapping" : {
    "properties": {
      "metadata": {
        "properties": {
          "name": {
            "type": "text",
            "fields": {
              "keyword": {
                "type": "keyword",
                "ignore_above": 256
              }
            }
          },
          "type": {
            "type": "text",
            "fields": {
              "keyword": {
                "type": "keyword",
                "ignore_above": 256
              }
            }
          }
        }
      },
      "text": {
        "type": "text"
      },
      "vector": {
        "type": "dense_vector",
        "dims": 1536
      }
    }
  }
}
```

The above mapping is necessery to store dense vectors generated from OpenAI embedding model in es database.
## Todo Next

* Add a relational sql database to track changes and monitor token usage. 
* Integrate IAM and security policies
## Authors

- [@sakthi535](https://www.github.com/sakthi535)
