import settings, importlib


help_text = ""
for application in settings.APPLICATIONS:
    try:
        module = importlib.import_module(application) # Dinamic import
        help_text += module.help()
    except:
        pass