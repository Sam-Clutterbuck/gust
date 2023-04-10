# Gust
> created by @Sam-Clutterbuck on 24/03/2023 developed in python

Gust is a Air gapped network import solution comprised of 2 different components; A server that is installed on an internet connected machine outside of the airgap. And a receiving client deployed internal to the airgap but with a connection to the server on port `11811`.

Gust is best used for repeatable import sources such as plugin repositories, update and patch files, and other downloads that all accessible from a static url.

## [Server](/docs/server)

Due to its access to the internet the server is locked down and is able to download the import files and store them locally however only has write and read access and no executable access outside of its own core python functions. It is also only allowed to access the urls of selected import files and hashes.

The server has a file containing all urls of import sources and must include a hash file url that is downloaded first and ran against any downloaded imports to ensure integrity otherwise the imported file will be removed. Currently Supported Hash Types are:
```
md5
sha256
```
[Find out more about how to use the server in the docs...](/docs/server)

## [Client](/docs/client)

The Client also has to be securely locked down to ensure that its connection to an internet connected device (the  server) doesn't compromise its integrity and confidentiality. To assist in this the client can only connect to the servers specific gust port `11811` and doesn't have access to any http(s) ports or web interfaces. On top of this the client only able to accept files and have write access to files from the server transfer and not any other locations on the interior network.

[Find out more about how to use the client in the docs...](/docs/client)
