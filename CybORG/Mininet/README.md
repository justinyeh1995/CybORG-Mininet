## Catalog

1. setup.md
2. dev.md

## Setting Up Environment

### Mininet

```bash
git clone https://github.com/mininet/mininet
cd mininet
git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0  # or whatever version you wish to install
cd ..
mininet/util/install.sh
```

### Velociraptor
1. Install Velociraptor:

- Download the appropriate Velociraptor package for your operating system from the official Velociraptor website or GitHub repository.
- Extract the downloaded package to a directory of your choice.

2. Generate server configuration:

    Open a terminal or command prompt and navigate to the directory where you extracted Velociraptor.
    Run the following command to generate the server configuration file:
    ```bash
    ./velociraptor --config server.config.yaml config generate > server.config.yaml
    ```
    This command generates a default server configuration file named server.config.yaml.


3. Customize server configuration:

    Open the server.config.yaml file in a text editor.
    Modify the configuration settings according to your requirements. 
    
    Some important settings to consider:
    
    Client.server_urls: Specify the URL(s) where clients can connect to the server.
    Datastore.implementation: Choose the datastore implementation (e.g., FileBaseDataStore, MySQL, PostgreSQL).
    Datastore.location: Specify the location or connection details for the selected datastore.
    Logging.output_directory: Set the directory where server logs will be stored.
    
    
    Save the changes to the server.config.yaml file.


4. Start the Velociraptor server:

    Run the following command to start the Velociraptor server:
    ```bash
    ./velociraptor --config server.config.yaml frontend
    ```
    The server will start running and listen for incoming client connections.


5. Generate client configuration:

    In a new terminal or command prompt, navigate to the directory where you extracted Velociraptor.
    Run the following command to generate the client configuration file:
    ```bash
    ./velociraptor --config server.config.yaml config client > client.config.yaml
    ```
    This command generates a client configuration file named client.config.yaml based on the server configuration.


6. Deploy the client configuration:

    Copy the client.config.yaml file to the client machines where you want to install the Velociraptor client.
    Place the client.config.yaml file in a directory accessible by the Velociraptor client on each client machine.


7. Install and start the Velociraptor client:

    On each client machine, download and extract the Velociraptor package.
    Open a terminal or command prompt and navigate to the directory where you extracted the Velociraptor client.
    Run the following command to start the Velociraptor client:
    ```bash
    ./velociraptor --config client.config.yaml client
    ```
    The client will connect to the Velociraptor server using the configuration specified in the client.config.yaml file.
    

8. Access the Velociraptor web interface:

    Open a web browser and navigate to the URL where the Velociraptor server is running (e.g., https://localhost:8889).
    Log in using the default administrator credentials (username: admin, password: admin).
    You can now use the Velociraptor web interface to manage clients, create hunts, collect artifacts, and perform other tasks.
    
    
    Note: The above steps provide a basic setup for Velociraptor. Depending on your specific requirements, you may need to perform additional configuration, such as setting up SSL/TLS certificates, configuring authentication, and integrating with other systems.
    It's important to review the Velociraptor documentation and follow security best practices when setting up and using Velociraptor in a production environment.

