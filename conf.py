import os

kafkaHost = os.environ.get("EJBCA_KAFKA_HOST", "kafka:9092")
service = "admin"
data_broker = "http://data-broker"
subject = "dojot.device-manager.device"
