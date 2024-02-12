from rest_framework.schemas.openapi import AutoSchema
from rest_framework import serializers
from rest_framework.fields import empty

class SaintSophiaSchema(AutoSchema):

    def get_tags(self, path, method):
        # If user have specified tags, use them.
        if self._tags:
            return self._tags

        # First element of a specific path could be valid tag. This is a fallback solution.
        # PUT, PATCH, GET(Retrieve), DELETE:        /user_profile/{id}/       tags = [user-profile]
        # POST, GET(List):                          /user_profile/            tags = [user-profile]
        if path.startswith('/'):
            path = path[1:]

        tags = [path.split('/')[2].replace('_', '-')]

        return tags