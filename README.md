# elasticsearch-kibana-docker-sample

## install & start
```shell
$ git clone git@github.com:yoshihir/elasticsearch-kibana-docker-sample.git
$ cd elasticsearch-kibana-docker-sample
$ docker-compose up
```
## health check
```shell
## health check
$ curl http://localhost:9201/_cluster/health?pretty
## cluster topology
$ curl http://localhost:9201/_cat/nodes?v
## master node
curl http://localhost:9201/_cat/master?v
```

## Kibana's DevTools
```shell
PUT _template/blog
{
  "index_patterns": "blog",
  "settings": {
    "analysis": {
      "tokenizer": {
        "kuromoji": {
          "type": "kuromoji_tokenizer",
          "mode": "search"
        }
      },
      "analyzer": {
        "kuromoji-analyzer": {
          "type": "custom",
          "tokenizer": "kuromoji",
          "filter": [
            "ja_stop",
            "kuromoji_part_of_speech",
            "lowercase"
          ],
          "char_filter": [
            "html_strip"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "body": {
        "type": "text",
        "fielddata": true,
        "analyzer": "kuromoji-analyzer"
      },
      "title": {
        "type": "text",
        "analyzer": "kuromoji-analyzer",
        "fielddata": true,
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      }
    }
  }
}
```
## Submit data to ElasticSearch
```shell
python indexing.py --host localhost --port 9201 --file yoshihir.hatenablog.com.export.txt
```
