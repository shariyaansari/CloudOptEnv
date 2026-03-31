# server/app.py
import uvicorn
from openenv.core.env_server import create_fastapi_app
from my_env.models import Action, Observation
from my_env.env import CloudOptEnvironment
import my_env.tasks.easy as task_module

def main():
    # Instantiate our environment
    env = CloudOptEnvironment(task_module)
    
    # Wrap it in OpenEnv's standard FastAPI app
    app = create_fastapi_app(env, Action, Observation)
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()