"""
Database router for wiki replica models.

This router directs queries for wiki_replica models to the 'wiki_replica'
database, while all other queries go to the default database.
"""


class WikiReplicaRouter:
    """
    A router to control database operations for wiki_replica models.
    """

    route_app_labels = {'wiki_replica'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read wiki_replica models go to wiki_replica database.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'wiki_replica'
        return None

    def db_for_write(self, model, **hints):
        """
        Wiki replica models are read-only - don't allow writes.
        """
        if model._meta.app_label in self.route_app_labels:
            # Return None to prevent writes - wiki replicas are read-only
            return None
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the wiki_replica app is involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Don't create wiki_replica tables in any database.
        These tables already exist in the wiki replica database.
        """
        if app_label in self.route_app_labels:
            return False  # Never migrate wiki_replica models
        return None
