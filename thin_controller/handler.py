from mangum import Mangum

from thin_controller import app

handler = Mangum(app)
