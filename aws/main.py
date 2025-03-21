import os
from dotenv import load_dotenv
import typer

from services.ec2 import ec2_router


app = typer.Typer(no_args_is_help=True)
app.add_typer(ec2_router, name="ec2")


@app.callback()
def callback(ctx: typer.Context):
    load_dotenv(".env")

    REGION = os.getenv('AWS_REGION')
    ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

    ctx.obj = {
        "credentials": {
            "region": REGION,
            "access_key": ACCESS_KEY,
            "secret_key": SECRET_KEY,
            "session_token": SESSION_TOKEN,
        }
    }


if __name__ == "__main__":
    app()
