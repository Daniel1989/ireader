import json
import os
import uuid

import lancedb

uri = "./data"
db = lancedb.connect(uri)


# result = table.search([100, 100]).limit(2).to_pandas()

def check_table_exist(name):
    tables = db.table_names()
    return name in tables


def updateOrCreateTable(name, data):
    # [
    #     {"vector": [1.3, 1.4], "item": "fizz", "price": 100.0},
    #     {"vector": [9.5, 56.2], "item": "buzz", "price": 200.0},
    # ]
    if check_table_exist(name):
        tbl = db.open_table(name)
        data = data
        tbl.add(data)
    else:
        db.create_table(name, data=data)
        tbl = db.open_table(name)
        tbl.add(data)
        # tbl.create_index(num_sub_vectors=1)
    return True


def storeVectorResult(vectorData, url):
    path = 'vector_data'
    os.makedirs(path, exist_ok=True)
    digest = uuid.uuid5(uuid.NAMESPACE_DNS, url)
    path = os.path.join(path, digest.hex + '.json')
    with open(path, 'w') as f:
        f.write(json.dumps(vectorData))


def distanceToSimilarity(distance: None | float):
    if distance is None or not isinstance(distance, float):
        return 0.0
    elif distance >= 1.0:
        return 1.0
    elif distance <= 0.0:
        return 0.0
    else:
        return 1.0 - distance


def vectorSearch(name, query_vector):
    tbl = db.open_table(name)
    result = tbl.search(query_vector).metric("cosine").limit(4).to_pandas()
    context_texts = []
    source_documents = []
    score = []
    for index, row in result.iterrows():
        # 设定最小余弦距离阈值的主要原因是为了排除过于接近的匹配、增加结果的多样性、增强泛化性，从而满足特定的业务需求。
        MIN_DISTANCE = 0.25
        if row["_distance"] >= MIN_DISTANCE:
            score.append(distanceToSimilarity(row["_distance"]))
            context_texts.append(row["text"])
            source_documents.append(row.to_dict())

    return context_texts, score, source_documents
