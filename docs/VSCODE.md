# VSCode Debugger Setup
When developing locally, always run code within Docker. 

To use the VS Code debugger while running the docker environments locally perform the following steps for your respective project

### Backend
* from amirainvest_com run make vs_code_debug
This will build backend according to the [Environment](DEVELOPMENT.md) specified. The debugger will also install and begin broadcasting on port `5678`. 

NOTE: The app within the container will not actually launch until your debugger client in VS Code has attached itself to the container. 

Proceed to the next step once the terminal window shows that debugpy has finished pip installing.
* navigate to `src/backend_amirainvest_com/lib/backend_amirainvest_com/main.py`within your VSCode workspace (you may be able to perform this from any file within the project)
* From within VSCode, begin the debugger (from the `Run` tab, the debug icon on the sidebar, or pressing `F5`). Select the option to `Remote Attach`. Set `Host` to `localhost` and `port` to `5678`
The debugger will now attach. In your original terminal window, the backend app will now proceed and launch backend, broadcasting the app on port `5000`.


# _Debugging_
You can now debug your VS Code debugger to debug the app running within Docker. You can add breakpoints from within VS Code. When you execute a request, either through postman, curl, or the /docs page in your browser, the breakpoint will apply and you can view the contents of the objects, processes, etc that are in flux.
