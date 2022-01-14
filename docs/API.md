# Moving

* move to `backend/<route_name singular>`
    * router `router.py`
    * controller `controller.py`
    * model `model.py`
* Router
    * Change router prefix to singular
    * Change route tags to singular
    * Change all route types to `post`
    * Change all route paths to `create, delete, update, get, list, or other if specific buisness logic is needed`
    * Change route function names to `list_route, create_route, etc...`
    * Change status codes to use `fastapi.status`
    * Check all route input/output types
    * Change any `__dict__` to `.dict()`
    * Move any `.dict()` being passed to controllers into the controller and pass entire pydantic object
* app.py
    * Import new router
    * Change in app.include_router
* Controller
    * Change controller function names to `list_controller, delete_controller, etc...`
    * Add function param types
    * Add function return types
    * Change any status code returns to use `fastapi.status`
    * Change any pydantic `.dict()` to `dict(exclude_none=True)` if no `None`s are wanted in the DB
    * Return DB table object or list of where possible
* Model
    * Change model names to `CreateModel, DeleteModel, etc...`
    * Import model from `common.schemas` and rename to `GetModel` if using DB table Model for FastAPI docs
        * Add `assert GetModel`
* Tests
    * Change all requests to `.post(`
    * Change routes called
    * Change test function names

* Run `make test`
* Run `pytest` inside of `make interactive`
