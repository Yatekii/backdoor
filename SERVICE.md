# Service File Structure

- service name
    - __init__.py -- contains all the major functions
    - more files included by __init__.py
    - blueprint -- blueprint for the service
        - __init__.py -- all the blueprint methods. MUST specify a variable __blueprint__ with the blueprint!
        - additional files concerning the blueprint
        - templates -- html files for the webui part