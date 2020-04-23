## Prerequisites

You need to be in a python3 environment with the `elasticsearch==7.5.1` and `jsonschema` library available. So either restore the Pipfile or run it through Docker (I installed those libraries in the Dockerfile for testing purposes).

## Where does the data come from

At that time, only the vessel_calls are stored in the IH. So they are the only data to be requested from the IH, the other data are entered as "forceInput" in the PAS_instance.json.

## Run the IH retriever for testing

Place the identification files in the `pas_modelling/test/resources/vpn` folder. Those files, `pass.txt` and `romain.opvn`, can be found on the dropbox link for CATIE only: https://www.dropbox.com/home/PIXEL%20port/5-%20wp/WP7/pas_modelling_vpn_resources.

Then connect to the VPN from a first terminal:
```bash
cd pas_modelling
docker run --rm -it --cap-add=NET_ADMIN --device /dev/net/tun --dns 8.8.4.4 --name vpn -v $(pwd)/test/resources/vpn:/vpn dperson/openvpn-client -c $(cat ./test/resources/vpn/pass.txt)
```

We can confirm that we are connected to the VPN by running from another terminal:

```bash
cd pas_modelling
docker run --rm --net=container:vpn byrnedo/alpine-curl http://ipinfo.io/ip  # Should print the IH IP adress and not yours
```

And we can run the `IH_requester_only pipeline` through docker for testing:
```bash
cd pas_modelling
rm -f ./test/resources/vpn/vpn.cert_auth  # This doesn't seem to be an important file, and otherwise we cannot build
docker build -t pas . # Or docker build --no-cache -t pas . in case of issues during package installation
docker run --rm --net=container:vpn pas python3 funkyPAS.py --pipeline IH_only --request_IH "$(cat ./test/resources/PAS_instance.json)"
```

## Integrate this test in Github Actions

Once we'll have the complete working pipeline. We may be able to connect to the IH using github actions and github secrets to store the VPN credentials.
