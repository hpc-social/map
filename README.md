# The HPC.social Community Map

This repository contains static files and workflows to generate the HPC.social map. 

![assets/img/logo.png](assets/img/logo.png)

## How does it work?

The form that is provided [on the site]() is fed into Google Sheets, and the workflow
to [.github/workflows/update-map.yml](.github/workflows/update-map.yml) is able to
parse the sheet for locations and then update the map!

## Development

You can test running the scripts locally! First, prepare a python environment:

```bash
$ python -m venv env
$ source env/bin/activate
```

And install dependencies:

```bash
$ pip install -r scripts/requirements.txt
```

You can then run the script directly:

```bash
$ python scripts/update_map.py
```

This automation runs nightly to update our map. But we aren't perfect, and sometimes
the data going into the form is not perfect! If you see a problem, please [open an issue](https://github.com/hpc-social/map/issues).


## 🎨️ Thanks 🎨️

The HPC.social map is derived from the [US-RSE Map](https://us-rse.org/usrse-map) which was
also designed and implemented by [@vsoch](https://github.com/vsoch).
