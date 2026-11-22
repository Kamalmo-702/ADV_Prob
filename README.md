# Stats Lab

A web app for the *Advanced Statistics & Probability* course (Horus University). It combines a **calculator** that shows every solution step with an **interactive learning tool** (plots and simulations) covering the normal distribution, the t / chi-square / F distributions, sampling distributions, the Central Limit Theorem, confidence intervals and sample size.

## Tech stack

| Part | Tools |
|---|---|
| Backend | Python 3.11+, FastAPI, Pydantic, SciPy, NumPy, pytest |
| Frontend | React 18, Vite, React Router, Axios, Plotly, KaTeX |
| DevOps | Docker Compose, GitHub Actions |

## Project structure

```
backend/
  app/
    main.py            FastAPI app, CORS, routers, GET /health
    core/              shared code: schemas, steps helper, z/t critical values, settings
    routers/           one router per module (HTTP layer only)
    services/          one service per module (the statistics logic)
  tests/               pytest tests, one file per module
frontend/
  src/
    api/client.js      Axios client (base URL from VITE_API_URL)
    components/        Layout, Sidebar, StepsViewer, PlotCard, NumberInput, ErrorMessage
    pages/             one page per module
    nav.js             list of modules used by the sidebar, home page and routes
    styles/theme.css   design tokens and base styles
.github/               CI workflow and pull request template
docker-compose.yml     runs backend and frontend together
```

## Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

## Run without Docker

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (new terminal):

```bash
cd frontend
cp .env.example .env              # Windows: copy .env.example .env
npm install
npm run dev
```

Run the tests with `pytest` inside `/backend`, and check the build with `npm run build` inside `/frontend`.

## Modules and owners

| Module | Backend router | Frontend page | Issue | Owner |
|---|---|---|---|---|
| Foundation, shared components, Docker, CI | `core/`, `main.py` | `components/`, `Home.jsx` | #1 | _TBD_ |
| Normal distribution, t / chi-square / F | `normal.py`, `distributions.py` | `NormalDistribution.jsx`, `DistributionsExplorer.jsx` | #2 | _TBD_ |
| Sampling distributions | `sampling.py` | `SamplingDistributions.jsx` | #3 | _TBD_ |
| Confidence intervals and sample size | `ci.py` | `ConfidenceInterval.jsx`, `SampleSize.jsx` | #4 | _TBD_ |
| CLT simulator, CI coverage, slide check | `clt.py`, `verify.py` | `CLTSimulator.jsx`, `CICoverage.jsx`, `CheckSlides.jsx` | #5 | _TBD_ |

## The response format

Every endpoint returns the same shape (`app/core/schemas.py`):

```json
{
  "result": { "...": "the final answer(s)" },
  "steps": ["1-\\alpha = 0.95", "z_{\\alpha/2} = 1.96"],
  "plot": { "x": [], "y": [] },
  "notes": ["np < 5: the normal approximation may be poor"]
}
```

`steps` are LaTeX strings. The frontend shows them with `<StepsViewer steps={data.steps} />`.

## How to add or implement a module

1. **Service**: write the logic in `backend/app/services/<module>_service.py`. Use `StepsBuilder` from `core/steps.py` to build the steps and `z_critical` / `t_critical` from `core/stats_utils.py`.
2. **Router**: keep `backend/app/routers/<module>.py` thin. It validates input (add a Pydantic request model) and calls the service. For a brand new module, create the router and register it in `app/main.py`.
3. **Tests**: replace the placeholder test in `backend/tests/test_<module>.py` with real examples from the lectures.
4. **Page**: replace `PagePlaceholder` in `frontend/src/pages/<Page>.jsx` with the real UI. Call the API with `post()` from `api/client.js`, then show `StepsViewer` and `PlotCard`.
5. **New page**: add an entry to `frontend/src/nav.js` and a `<Route>` in `App.jsx`.
6. Open a pull request (see `CONTRIBUTING.md`).

## Notes for the statistics

- Compute exact values with SciPy rather than copying numbers from the slides. The slides use printed tables, so small differences are normal, and a few slide answers are simply wrong. Report those to the owner of Issue #5 for the "Check the Slides" page.
- Confidence interval case selection follows the lecture: known sigma (normal population or n >= 30) uses Z with sigma; unknown sigma and n >= 30 uses Z with s; unknown sigma, approximately normal population and n < 30 uses T with n-1 degrees of freedom.
