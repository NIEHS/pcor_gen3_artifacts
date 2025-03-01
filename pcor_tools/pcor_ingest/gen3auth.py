"""
This package handles auth interactions with Gen3
"""
import json
import logging

import requests

from gen3.auth import Gen3Auth

logger = logging.getLogger(__name__)


class PcorGen3Auth:

    def __init__(self, pcor_ingest_configuration):
        self.pcor_ingest_configuration = pcor_ingest_configuration
        self.auth = None
        self.gen3_token = None

    def authenticate_to_gen3(self):
        """
        Obtain the Gen3Auth using information stored in the environment, obtains a refresh token
        :return: Gen3Auth object
        """
        logger.info("authenticate_to_gen3()")
        creds = self.obtain_creds_using_config()
        self.auth = Gen3Auth(endpoint=self.pcor_ingest_configuration.gen3_endpoint, refresh_token=creds)
        return self.auth

    def obtain_creds_using_config(self):
        """
        Get the creds json content using environment variables
         CREDENTIALS_FILE is the env variable that should hold the path to credentials.json
        GEN3_ENDPOINT is the env variable for the protocol/host for the Gen3 endpoint with no trailing slash
        :return: creds which is the json content of the creds file
        """
        logger.info("obtain_token_using_env()")
        with open(self.pcor_ingest_configuration.gen3_creds_location) as f:
            creds = json.load(f)
            return creds
            #api_key_id = creds["key_id"]
            #api_key = creds["api_key"]
            #self.gen3_token = self.obtain_token(api_key_id, api_key, self.pcor_ingest_configuration.gen3_endpoint)


    @staticmethod
    def obtain_token(api_key_id, api_key, endpoint):
        """
        Obtain the token for API requests by passing the API key information
        :param api_key_id: Gen3 API key identifier
        :param api_key: Gen3 API Key
        :param endpoint: URL for API
        :return: short-lived token for API requests
        """
        logger.info("obtain_token()")
        key = {
            "api_key": api_key,
            "key_id": api_key_id
        }

        token = requests.post(endpoint + '/user/credentials/cdis/access_token', json=key).json()
        logger.info("token:%s", token)
        return token

