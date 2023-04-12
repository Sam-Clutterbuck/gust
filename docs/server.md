# Gust Server
# Installation
## physical Install location

The Server is designed to be deployed outside of the air gapped network on an internet connected machine. It is recommended that the server is isolated either in a dmz or just generally in a suitable location where it can only have two connections, one connected to the internet and second to the gust client (excluding any monitoring or physical security controls).

## Installation packages
The Server installation should only contain the `core, server & web` packages with their associated src and data directories. There shouldn't be any client packages installed as this could allow the server to reach out to other locations which could pose a security concern.

## Installation steps
There are currently no installation steps laid out but plan to use docker and automations to configure most of it.

# Sources
Sources are the core of the gust system and functionally are a dictionary of urls that you would like to import download files from. These comprise of 4 components:
```
Source Name
Source url
Hash url
Hash type
```
### source name
The source name is a purely human element that should describe the import file. For example:
>program_plugins
>RHEL patches
>etc...
### source & hash url
As they sound the two url sections are where the url for the actual file you want to import and its corresponding hash file are stored. It is important to know that to best use gust these urls should be as static as possible as to limit a continuous need to update the url. 

For example `https://www.plugin-provider.com/download/plugins.tar.gz` is a good link as all subsequent plugins that are updated will use the same link, whilst `https://www.patch-provider.com/downloads/v2/update31223/download/import-patch-1234.rpm` would not work as well as patch 1235 would have a different url and as such require manual intervention to download it.
### hash type
The hash type is simply the type of hash algorithm stored in the hash file that should be run against the imported file to confirm integrity. It is commonly shown appended to the end of the hash file name `hashfile.rpm.sha256` 

**Currently supported hashes *(as of 04/2023)* are:**
```
md5
sha256
```
## Source commands
Source commands are able to be run via the command line however it is recommended for users to connect to the web server to carry out commands for an easier experience. 
*(note you can also manually edit the source list directly by opening `/server/data/gust_store.yaml` in your chosen text editor)*

Both processes will be demonstrated in the 4 main commands listed below:
### add source
This command adds a new source to the source list. It should be noted that if an already existing source with the same name exists it will be overwritten.
#### via web gui
//add photo steps
#### via command line
```
gust-server Add_Source(source_name, source_url, hash_url, hash_type)
```
### update source
This command takes an existing source from the source list and allows the user to update its content. 
#### via web gui
#### via command line
```
gust-server Update_Source(source_name, source_url, hash_url, hash_type)
```
### delete source
This command takes the selected source and deletes it from the source list. 
#### via web gui
#### via command line
```
gust-server Delete_Source(source_name)
```
### download sources
The download sources command runs through all of the sources in the list downloading the hash file and then the associated import file before running an integrity hash check on the pair. If they match then the files are stored in the `/server/data/downloads` folder, otherwise they are removed.
#### via web gui
#### via command line
```
download
```

# Server Cli Service
If you want to interact with the gust server you can either use the cli interface or web gui. If you choose to use the cli run the command:
```
python gust-server
```

The following commands are avaliable to use in the cli:
```
Gust Server Cli Tools
version: 0.0.1
created by: @Sam-Clutterbuck

python gust-server.py 

Commands:

    help          Show this message and exit

    Source Control:

    print_sources   [ARGS]: None
    add_source      [ARGS]: Name, URL, Hash_URL, Hash_Type
    update_source   [ARGS]: Name, URL, Hash_URL, Hash_Type
    delete_source   [ARGS]: Source Name

    Downloads:

    print_downloads [ARGS]: None
    download_all    [ARGS]: None
    download_source [ARGS]: Source Name

    User Control:

    new_user        [ARGS]: Username, Password
    del_user        [ARGS]: Target Username
    passwd_reset    [ARGS]: Target Username, New Password

    Services:

    restart_server  [ARGS]: None
    start_server  [ARGS]: None
    stop_server  [ARGS]: None

```