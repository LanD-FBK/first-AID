# first-AID

First-AID is a human-in-the-loop (HITL) data collection framework for knowledge-driven generation of synthetic dialogues using LLM prompting. In particular, our framework implements different strategies of data collection that require different user intervention during dialogue generation to reduce post-editing efforts and enhance the quality of generated dialogues. Find more details in our ACL 2025 paper: <a href="https://aclanthology.org/2025.acl-demo.54/"><em>First-AID: the first Annotation Interface for grounded Dialogues</em></a> (Menini et al., ACL 2025). If you use the First-AID please <a href="https://github.com/LanD-FBK/first-AID/tree/main#bibtex-citation">cite</a> our original paper.

# Installation

First-AID is made by three parts: (i) the backend, written in Python (w/ [FastAPI](https://fastapi.tiangolo.com/) and [SQLite](https://www.sqlite.org/)); (ii) the frontend, written in [VueJS](https://vuejs.org/); (iii) the generation API, written in Python/FastAPI.

## Preliminary steps

* Clone the repository: `git clone https://github.com/LanD-FBK/first-AID`
* Enter the folder: `cd first-AID`

## Run the backend

The backend is written in Python ad it needs Python 3.10+ to be installed on the machine.

* Go to the backend folder: `cd backend`
* Create an environment (or use [conda](https://anaconda.org/anaconda/conda) or similar: `python3 -m venv env`
* Activate the environment: `source env/bin/activate`
* Install the dependencies: `pip install -r requirements.txt`
* Run the server: `uvicorn server:app`

If this is the first time you run the tool and you have not specified any other parameter, a database is created in memory, therefore all the data will be deleted if the service is restarted. To avoid this, run the server with the `DB_ENGINE` variable. For example: `DB_ENGINE=sqlite+pysqlite:////path/to/db uvicorn server:app`.

During the first run, an `admin` user is created, with (default) password `N8Lwcs4G7Vbmkp5t5g`. One can change that password once logged into the web interface (see next section).

If you want to customize the server and/or the port, just add `--host` or `--port` at the end of the command. Example: `DB_ENGINE=sqlite+pysqlite:////path/to/db uvicorn server:app --host 0.0.0.0 --port 12345`.

The FastAPI documentation page is available on [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Run the frontend

The frontend is written in VueJS and it needs npm/node to work properly.

* Go to the frontend folder: `cd frontend`
* Install the dependencies: `npm install`
* Run the server: `VITE_APP_AXIOS_URL=http://localhost:8000 npm run dev`
* Surf to: [http://localhost:5173/](http://localhost:5173/)
* Login: `admin`/`N8Lwcs4G7Vbmkp5t5g`

Depending on your needs, you can change the URL of the API backend by replacing `http://localhost:8000` with the desired address. Similarly to what happens to the backend, host and port can be changed by adding `-- --host 0.0.0.0 --port 12345` to the run command.

## Run the generation API

Some features of First-AID need an API normally linked to a large language model. We provide a dummy one (that uses [Llama](https://www.llama.com/) and [Groqcloud](https://console.groq.com/home)) in the [dialogue-generation-api](dialogue-generation-api) subfolder of the project.

# BibTex Citation

If you use First-AID in your work, please cite the following paper:

```bibtex
@inproceedings{menini-etal-2025-first,
    title = "First-{AID}: the first Annotation Interface for grounded Dialogues",
    author = "Menini, Stefano  and
      Russo, Daniel  and
      Aprosio, Alessio Palmero  and
      Guerini, Marco",
    editor = "Mishra, Pushkar  and
      Muresan, Smaranda  and
      Yu, Tao",
    booktitle = "Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations)",
    month = jul,
    year = "2025",
    address = "Vienna, Austria",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.acl-demo.54/",
    pages = "563--571",
    ISBN = "979-8-89176-253-4"
}
```

# License

This software is released under the Apache 2.0 license.

# Funding Acknowledgement

This work was supported by Provincia Autonoma di Trento under grant agreement No. C49G22001020001 (AIxPA) and by the European Union’s CERV fund under grant agreement No. 101143249 (HATEDEMICS).

