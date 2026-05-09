# CI/CD — Uitleg en gebruik

## Wat is CI/CD?

**CI (Continuous Integration)** betekent dat wijzigingen in de code automatisch worden gebouwd en getest zodra ze worden gepusht.  
**CD (Continuous Deployment)** zorgt ervoor dat een goedgekeurde build automatisch wordt uitgerold naar de draaiende omgeving.

In dit project simuleren we dat proces met een **Makefile** die de volledige deployment cyclus beheert.

---

## De Makefile

De Makefile is het centrale CI/CD-hulpmiddel. Plaats hem naast je `docker-compose.yml` en gebruik hem via de terminal.

### Beschikbare commando's

| Commando        | Wat het doet                                                    |
|----------------|-----------------------------------------------------------------|
| `make help`    | Toont alle beschikbare commando's                               |
| `make build`   | Bouwt de `sensor_sim` image opnieuw (zonder cache)              |
| `make up`      | Start de volledige stack op in de achtergrond                   |
| `make down`    | Stopt en verwijdert alle containers (volumes blijven bewaard)   |
| `make deploy`  | Volledige cyclus: build → down → up                             |
| `make restart` | Herstart de stack zonder te rebuilden (sneller)                 |
| `make logs`    | Toont live logs van alle services                               |
| `make status`  | Toont de huidige status van alle containers                     |
| `make clean`   | Volledige reset inclusief volumes (vraagt bevestiging)          |
| `make prune`   | Verwijdert ongebruikte Docker images en netwerken               |

### Typisch gebruik

**Eerste keer opstarten:**
```bash
make deploy
```

**Na een wijziging in sensor_sim:**
```bash
make deploy
```

**Snel herstarten zonder code wijziging:**
```bash
make restart
```

**Alles controleren:**
```bash
make status
make logs
```

---

## Hoe werkt `make deploy`?

```
[1/3] Build  →  docker compose build --no-cache sensor_sim
[2/3] Stop   →  docker compose down
[3/3] Start  →  docker compose up -d
```

Dit garandeert dat altijd de nieuwste versie van de code draait, zonder restanten van oude containers.

---

## Gebruik in een echte pipeline (GitHub Actions)

In een productieomgeving zou je deze Makefile aanroepen vanuit een GitHub Actions workflow. Bij elke push naar `main` wordt automatisch gedeployed op de server:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: self-hosted        # eigen server als runner
    steps:
      - uses: actions/checkout@v3

      - name: Deploy stack
        run: make deploy
```

De stappen zijn dan:
1. Developer pusht code naar GitHub
2. GitHub Actions start automatisch
3. `make deploy` bouwt de nieuwe image, stopt de oude stack en start de nieuwe op
4. De server draait altijd de laatste versie

---

## Optioneel: Watchtower

**Watchtower** is een tool die automatisch draaiende containers herstart wanneer er een nieuw image beschikbaar is op Docker Hub. Voeg dit toe aan je `docker-compose.yml` om updates van publieke images (zoals `nodered`, `influxdb`) automatisch te verwerken:

```yaml
watchtower:
  image: containrrr/watchtower
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  command: --interval 30
  restart: always
```

Dit controleert elke 30 seconden of er nieuwe versies zijn en herstart de betreffende containers automatisch.

> **Let op:** Watchtower werkt het best voor publieke images. Voor de `sensor_sim` image (die lokaal gebouwd wordt) blijf je `make deploy` gebruiken.
