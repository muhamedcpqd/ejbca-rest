# alternatively to the REST API
# one can use Kafka messages to configure ejbca-rest
# this file is the EJBCA kafka entry point
# the purpose of functions here is to verify input and pass
# the requests to the controller class
import logging
import kafka
import json
from time import sleep
import requests
from threading import Thread

import conf
from controller.RequestError import RequestError
import controller.UserController as uc
from ejbcaUtils import initicalConf

LOGGER = logging.getLogger('ejbca.' + __name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)


class KafkaConsumer(Thread):
    def __init__(self):
        Thread.__init__(self)

    def get_topic(service, subject):
        if service in topic_map.keys():
            if subject in topic_map[service].keys():
                return topic_map[service][subject]

        target = "{}/topic/{}".format(CONFIG.data_broker, subject)
        userinfo = {
            "username": "device-manager",
            "service": service
        }

        jwt = "{}.{}.{}".format(base64.b64encode("model".encode()).decode(),
                                base64.b64encode(json.dumps(userinfo).encode()).decode(),
                                base64.b64encode("signature".encode()).decode())

        response = requests.get(target, headers={"authorization": jwt})
        if 200 <= response.status_code < 300:
            payload = response.json()
            if topic_map.get(service, None) is None:
                topic_map[service] = {}
            topic_map[service][subject] = payload['topic']
            return payload['topic']
        return None

    def run(self):
        while True:
            LOGGER.debug("waiting for new messages")

            # To consume latest messages and auto-commit offsets
            while True:
                try:
                    consumer = (kafka.
                                KafkaConsumer(
                                    get_topic('admin', 'dojot.device-manager.device'),
                                    group_id='ejbca',
                                    bootstrap_servers=[conf.kafkaHost]
                                           )
                                )
                    break
                except kafka.errors.NoBrokersAvailable:
                    LOGGER.error('Could not connect to Kafka at %s.'
                                 ' Chances are the server is not ready yet.'
                                 ' Will retry in 30sec' % conf.kafkaHost)
                    sleep(30)

            for message in consumer:
                try:
                    requestData = json.loads(message.value)
                except ValueError:
                    LOGGER.error('Could not decode message as JSON. '
                                 + dumpKafkaMessage(message))
                    continue

                if 'event' not in requestData.keys():
                    LOGGER.error('Event not specified. '
                                 + dumpKafkaMessage(message))
                    continue

                if requestData['event'] in ['create', 'update']:
                    try:
                        if 'data' not in requestData.keys():
                            LOGGER.error("data segment not found. "
                                         + dumpKafkaMessage(message))
                            continue
                        if 'id' not in requestData['data'].keys():
                            LOGGER.error("device id not specified. "
                                         + dumpKafkaMessage(message))
                            continue
                        requestData['username'] = requestData['data']['id']
                        uc.createOrEditUser(requestData)
                        LOGGER.info('user %s created'
                                    % requestData['username'])
                    except RequestError as err:
                        LOGGER.error(err.message + " "
                                     + dumpKafkaMessage(message))

                elif requestData['event'] == 'delete':
                    try:
                        if 'data' not in requestData.keys():
                            LOGGER.error("data segment not found. "
                                         + dumpKafkaMessage(message))
                            continue
                        if 'id' not in requestData['data'].keys():
                            LOGGER.error("device id not specified. "
                                         + dumpKafkaMessage(message))
                            continue
                        uc.deleteUser(requestData['data']['id'])
                        LOGGER.info("Device %s revocated"
                                    % requestData['data']['id'])
                    except RequestError as err:
                        LOGGER.error(err.message + " "
                                     + dumpKafkaMessage(message))

                else:
                    LOGGER.error("'event' " + requestData['event']
                                 + " not implemented"
                                 + dumpKafkaMessage(message))


# helper function to log messages (for debug purposes)
def dumpKafkaMessage(msg):
    return ('%s:%d:%d: key=%s value=%s'
            % (msg.topic, msg.partition,
               msg.offset, msg.key,
               msg.value)
            )
