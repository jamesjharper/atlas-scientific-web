from .api import create_app

def serve_dev(as_module=False):
    create_app().run(host="0.0.0.0", debug = True)

if __name__ == '__main__':
    serve_dev()
