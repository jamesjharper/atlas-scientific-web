# Atlas Scientific IOT Web Client 

# Building Static assets:
`npm install --no-optional`
`npm run build`

# Building Server Package:
`pipenv install -dev`
`pipenv run package`


# Run Server in Production 

`pip install waitress`
`pip install dist/atlas_scientific_web-0.1.0-py3-none-any.whl`
`waitress-serve --listen=localhost:8080 --call 'atlas_scientific_web:create_app'`