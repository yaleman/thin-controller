"""AWS Lambda handler for the Thin Controller application using Mangum."""

from mangum import Mangum

from thin_controller import app

handler = Mangum(app, lifespan="off")
