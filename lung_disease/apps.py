from django.apps import AppConfig


class LungDiseaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lung_disease'

    def ready(self):
        import lung_disease.signals
