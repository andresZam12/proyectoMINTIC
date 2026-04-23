#!/bin/bash
# Descarga el JAR JDBC de PostgreSQL dentro del contenedor Jupyter.
# Ejecutar UNA sola vez después de docker-compose up:
#   docker exec mintic_jupyter bash /home/jovyan/src/3_datatransform/setup_jdbc.sh

JAR_URL="https://jdbc.postgresql.org/download/postgresql-42.7.3.jar"
JAR_DST="/usr/local/spark/jars/postgresql-42.7.3.jar"

if [ -f "$JAR_DST" ]; then
  echo "JAR ya existe: $JAR_DST"
else
  echo "Descargando JAR JDBC PostgreSQL..."
  curl -L "$JAR_URL" -o "$JAR_DST"
  echo "Listo: $JAR_DST"
fi
