from diagrams import Cluster, Diagram
from diagrams.onprem.container import Docker
from diagrams.aws.storage import SimpleStorageServiceS3

graph_attr = {
    "layout": "dot",
    "rankdir": "TB",
    "nodesep": "1",
    "ranksep": "1",
    "splines": "true",
    "ratio": "auto",
}

node_attr = {
    "fontcolor": "black",
    "fontsize": "16",
    "shape": "ellipse",
    "style": "transparent",
    "color": "black"
}

edge_attr = {
    "color": "black",
    "arrowhead": "normal",
    "fontcolor": "black"
}

with (Diagram("sake.karned.bzh", show = False, graph_attr = graph_attr, node_attr = node_attr, edge_attr = edge_attr)) as diag:
    with Cluster("Public access", direction = "BT"):
        frontend = Docker("Frontend")
        admin = Docker("Admin")
        gateway = Docker("Gateway")
        keycloak = Docker("Keycloak")

    with Cluster("Private access", direction = "TB"):
        etl = Docker("ETL")
        ocr = Docker("OCR")
        clean = Docker("Clean")
        preprocessing = Docker("Preprocessing")
        train = Docker("Train")
        eval = Docker("Eval")
        predict = Docker("Predict")
        orchestrator = Docker("Orchestrator")
        dvc = Docker("DVC")

    with Cluster("Services", direction = "TB"):
        s3 = SimpleStorageServiceS3("S3")

    frontend >> gateway
    admin >> gateway

    frontend >> keycloak
    admin >> keycloak

    gateway >> orchestrator
    gateway >> dvc

    dvc >> preprocessing
    dvc >> train
    dvc >> eval
    dvc >> etl
    etl >> ocr
    etl >> clean



    orchestrator >> preprocessing
    orchestrator >> predict

    dvc >> s3
    orchestrator >> s3
    etl >> s3
    train >> s3
    eval >> s3