#!flask/bin/python
import api
api.create_app().run(host="0.0.0.0", debug=True)
