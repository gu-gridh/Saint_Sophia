from django.conf import settings

class DjangoRouter:
    """
    A router to control all database operations on built-in models
    """

    route_app_labels = {'admin', 'auth', 'contenttypes', 'sessions'}

    def db_for_read(self, model, **hints):        
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'default'
        return None

class AppRouter:
    """
    A router to control all database operations on projects.
    Routes to a database with same name as app_label
    """
    projects = settings.NON_MANAGED_APPS
    # projects.remove('default') # Ensure the default databases is treated differently

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.projects:
            return model._meta.app_label
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.projects:
            return model._meta.app_label
        return None

    """
    Only allow relations in the same app (Django can handle relationsships between databases anyway)
    """
    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == obj2._meta.app_label
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.projects:
            return app_label == db
        return None