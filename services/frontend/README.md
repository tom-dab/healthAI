# Frontend — HealthAI Coach
Responsable : Hélie

## Lib

- React (Vite)
- Axios (communication API)
- React Router (navigation)
- Chart.js (visualisation des données)
- HTML / CSS (inline styling)

---

## Structure

services/frontend/
├── Dockerfile
├── src/
│ ├── components/ → Card, Table, Loader
│ ├── layout/ → Layout global + Sidebar
│ ├── pages/ → Dashboard, Users, DataQuality...
│ ├── charts/ → Graphiques (Chart.js)
│ └── services/ → appels API (axios)
├── package.json
├── vite.config.js
└── index.html