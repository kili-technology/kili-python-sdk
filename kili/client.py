#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from kili import mutations, queries, subscriptions
from kili.authentication import KiliAuth


class Kili(
        mutations.asset.MutationsAsset,
        mutations.label.MutationsLabel,
        mutations.notification.MutationsNotification,
        mutations.organization.MutationsOrganization,
        mutations.project.MutationsProject,
        mutations.user.MutationsUser,
        queries.asset.QueriesAsset,
        queries.label.QueriesLabel,
        queries.lock.QueriesLock,
        queries.organization.QueriesOrganization,
        queries.notification.QueriesNotification,
        queries.project.QueriesProject,
        queries.project_user.QueriesProjectUser,
        queries.user.QueriesUser,
        subscriptions.label.SubscriptionsLabel):

    def __init__(self, api_key=os.getenv('KILI_API_KEY'),
                 api_endpoint='https://cloud.kili-technology.com/api/label/v2/graphql',
                 verify=True):
        """Kili Client
        
        Parameters
        ----------
        api_key: 
            User API key generated from https://cloud.kili-technology.com/label/my-account/api-key

        api_endpoint : str
            Recipient of the HTTP operation
        
        verify : bool
            Verify certificate. Set to False on local deployment without SSL.
        
        Returns
        -------
        Kili object
        Object container your API session.
        Then, list:
        - your assets with: kili.assets()
        - your labels with: kili.labels()
        - your projects with: kili.projects()
        """
        self.auth = KiliAuth(api_key=api_key, api_endpoint=api_endpoint, verify=verify)
        super().__init__(self.auth)
