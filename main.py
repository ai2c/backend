import json
import os
import random

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.config import readConfig, writeConfig
from src.credentials import refreshCredentials
from src.metadata import readMetadata, writeMetadata, jsonExtract

if os.path.exists("config.env"):
    account_list, client_id, client_secret, category_list, refresh_token, secret_key, tmdb_api_key, environment = readConfig()
else:
    writeConfig()
    account_list, client_id, client_secret, category_list, refresh_token, secret_key, tmdb_api_key, environment = readConfig()

drive, access_token = refreshCredentials(
    "", client_id, client_secret, refresh_token, True)

configuration_url = "http://api.themoviedb.org/3/configuration?api_key=" + tmdb_api_key
configuration_content = json.loads(
    (requests.get(configuration_url)).content)
backdrop_base_url = configuration_content["images"]["base_url"] + \
    configuration_content["images"]["backdrop_sizes"][3]
poster_base_url = configuration_content["images"]["base_url"] + \
    configuration_content["images"]["poster_sizes"][3]

metadata = readMetadata(category_list)
metadata = writeMetadata(category_list, drive, tmdb_api_key,
                         backdrop_base_url, poster_base_url)

app = Flask(__name__)
CORS(app)
app.secret_key = secret_key


@app.route("/api/v1/metadata")
def metadataAPI():
    tmp_metadata = readMetadata(category_list)
    a = request.args.get("a")  # AUTH
    c = request.args.get("c")  # CATEGORY
    q = request.args.get("q")  # SEARCH-QUERY
    s = request.args.get("s")  # SORT-ORDER
    r = request.args.get("r")  # RANGE
    id = request.args.get("id")  # ID
    if any(a == account["auth"] for account in account_list):
        if c:
            tmp_metadata = [
                next((i for i in tmp_metadata if i["name"] == c), None)]
            if tmp_metadata:
                pass
            else:
                return None
        if q:
            index = 0
            for category in tmp_metadata:
                tmp_metadata[index]["files"] = [
                    item for item in category["files"] if q.lower() in item["title"].lower()]
                index = index + 1
        if s:
            index = 0
            for category in tmp_metadata:
                if s == "alphabet-asc":
                    tmp_metadata[index]["files"] = sorted(
                        category["files"], key=lambda k: k["title"])
                elif s == "alphabet-des":
                    tmp_metadata[index]["files"] = sorted(
                        category["files"], key=lambda k: k["title"], reverse=True)
                elif s == "date-asc":
                    tmp_metadata[index]["files"] = sorted(
                        category["files"], key=lambda k: tuple(map(int, k["releaseDate"].split('-'))))
                elif s == "date-des":
                    tmp_metadata[index]["files"] = sorted(category["files"], key=lambda k: tuple(
                        map(int, k["releaseDate"].split('-'))), reverse=True)
                elif s == "popularity-asc":
                    tmp_metadata[index]["files"] = sorted(
                        category["files"], key=lambda k: float(k["popularity"]))
                elif s == "popularity-des":
                    tmp_metadata[index]["files"] = sorted(
                        category["files"], key=lambda k: float(k["popularity"]), reverse=True)
                elif s == "random":
                    random.shuffle(tmp_metadata[index]["files"])
                else:
                    return None
                index = index + 1
        if r:
            index = 0
            for category in tmp_metadata:
                tmp_metadata[index]["files"] = eval(
                    "category['files']" + "[" + r + "]")
                index = index + 1
        if id:
            ids = jsonExtract(obj=tmp_metadata, key="id", getObj=True)
            for item in ids:
                if item["id"] == id:
                    tmp_metadata = item
        return jsonify(tmp_metadata)
    else:
        return None


if __name__ == "__main__":
    app.run(port=31145)
