import uvicorn
from openenv.core.env_server import create_fastapi_app
from my_env.models import Action, Observation
from my_env.env import CloudOptEnvironment
import my_env.tasks.easy as task_module

def env_factory():
    # The server will call this function to stamp out a fresh environment on every /reset
    return CloudOptEnvironment(task_module)

def main():
    # Pass the factory function (env_factory), NOT an instantiated object
    app = create_fastapi_app(env_factory, Action, Observation)
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()