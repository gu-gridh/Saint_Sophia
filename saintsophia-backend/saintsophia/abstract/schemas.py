from rest_framework.schemas.openapi import AutoSchema
from rest_framework import serializers
from rest_framework.fields import empty
import logging

logger = logging.getLogger(__name__)
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
    
    def get_filter_parameters(self, path, method):
        """
        Override to handle compatibility issues with django-filter.
        Safely gets filter parameters from filter backends.
        """
        if not self.allows_filters(path, method):
            return []
        
        parameters = []
        for filter_backend in self.view.filter_backends:
            try:
                # Try the new method first (django-filter >= 2.x with DRF schema support)
                if hasattr(filter_backend, 'get_schema_operation_parameters'):
                    parameters += filter_backend().get_schema_operation_parameters(self.view)
                # Fall back to getting filterset fields manually
                elif hasattr(filter_backend, 'get_filterset_class'):
                    filterset_class = filter_backend().get_filterset_class(self.view, self.view.get_queryset())
                    if filterset_class:
                        for field_name, filter_field in filterset_class.base_filters.items():
                            parameter = {
                                'name': field_name,
                                'required': filter_field.extra.get('required', False),
                                'in': 'query',
                                'description': filter_field.label or field_name,
                                'schema': {
                                    'type': 'string',
                                },
                            }
                            parameters.append(parameter)
            except Exception as e:
                # Log the error but don't break schema generation
                logger.warning(f"Could not get filter parameters from {filter_backend.__name__}: {e}")
                continue
        
        return parameters