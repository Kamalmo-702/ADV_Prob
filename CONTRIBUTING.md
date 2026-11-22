# Contributing

## Workflow

1. Pick your issue and assign yourself.
2. Update `main`, then create a branch named `feature/<module-name>`, for example `feature/sampling-distributions`.
3. Work only on the files of your module. If you need to change shared code (`core/`, `components/`, `nav.js`, `App.jsx`, `main.py`), tell the team first and keep that change in its own small commit.
4. Open **one pull request per issue** using the PR template and link the issue with `Closes #<number>`.
5. At least **one teammate must review** the PR before it is merged.
6. **Never push directly to `main`.**

## Before opening a pull request

```bash
cd backend && pytest
cd ../frontend && npm run build
```

Both commands must pass. CI runs the same checks on every pull request.

## Commit messages

Use a short imperative sentence with a prefix:

- `feat: add confidence interval endpoint`
- `fix: round sample size up`
- `test: cover the t case with n < 30`
- `docs: explain the response format`
- `style: align sidebar spacing`

## Code style

- Python: type hints on every function, logic in `services/`, no logic in routers.
- React: function components with hooks, one component per file.
- Every endpoint returns `SolutionResponse` (`result`, `steps`, `plot`, `notes`).
- Check your answers against the lecture examples, and against SciPy when the slide looks wrong.
