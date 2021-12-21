FROM postgres:10-alpine

COPY --chown=root:root ./data/postgres /var/lib/postgresql/data
rm
