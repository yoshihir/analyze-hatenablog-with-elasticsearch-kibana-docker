import re
from elasticsearch import Elasticsearch
import datetime
import argparse

columns = "AUTHOR|TITLE|BASENAME|STATUS|ALLOW COMMENTS|DATE"

blog_host = "https://yoshihir.hatenablog.com/entry/"
# template_pattern = re.compile("\<blockquote\>.+是非以下のページも御覧ください.+\<\/blockquote\>", flags=re.DOTALL)
template_pattern = ""

class MovableElasticsearchParser(object):

    def __init__(self, host, port):
        """
        Elasticsearchと接続する
        """
        # (1) Elasticsearchクライアントの初期化
        self.es = Elasticsearch(hosts=["{}:{}".format(host, port)])
        self.document = {}
        self.seq = ""

    def parse(self):
        """
        MovableTypeをパースする
        """
        # (3) メタ情報の解析
        elements = self.seq.split("-----\n")
        meta = elements[0]
        body = elements[1]

        meta_pattern = re.compile("({0}): (.*)".format(columns), flags=(re.MULTILINE | re.DOTALL))

        for metaline in meta.split("\n")[:-1]:
            matches = re.match(meta_pattern, metaline)
            if matches is not None:
                if matches.group(1).lower() in self.document:
                    self.document[matches.group(1).lower()]
                else:
                    self.document[matches.group(1).lower()] = matches.group(2)
        if "category" in self.document:
            self.document["category"] = self.document["category"].split(",")
            print(self.document["category"])

        body = re.sub("BODY:", "", body)
        body = re.sub(template_pattern, "", body)
        self.document["body"] = body

        # (4) 取得データの加工
        url = blog_host + self.document["basename"]
        self.document["source"] = url
        self.document["date"] = datetime.datetime.strptime(self.document["date"], "%m/%d/%Y %H:%M:%S")

        # (5) Elasticsearchへのデータ投入
        # print(self.document)
        self.es.index(index="blog", body=self.document)
        print(self.document)
        self.document={}


    def read_file(self, filename):
        """
        ファイルを読み込む。’--------’で区切ってparse()を呼び出す
        :param filename: データファイル名
        """
        # (2) ファイル解析
        with open(filename, encoding = "utf-8") as f:
            for line in f:
                if line == "--------\n":
                    self.parse()
                    self.seq=""
                else:
                    self.seq += line

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--host", type = str, default = "localhost")
    parser.add_argument("--port", type = int, default = 9201)
    parser.add_argument("--file", type = str, default = "yoshihir.hatenablog.com.export.txt")
    args=parser.parse_args()

    parser=MovableElasticsearchParser(host = args.host, port = args.port)
    parser.read_file(args.file)
