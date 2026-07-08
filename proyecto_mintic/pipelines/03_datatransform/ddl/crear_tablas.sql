-- =============================================================
--  DDL — mintic_db · Dashboard Predictivo Mercado Laboral CO
--  Ejecutado automáticamente por Docker al iniciar el contenedor
-- =============================================================

-- ------------------------------------------------------------
-- 1. Dimensión departamento
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_departamento (
    id_departamento SERIAL       PRIMARY KEY,
    codigo_dane     CHAR(2)      NOT NULL UNIQUE,
    nombre          VARCHAR(60)  NOT NULL,
    region          VARCHAR(40),
    es_area_metro   BOOLEAN      DEFAULT FALSE
);

-- Catálogo base (23 departamentos + áreas metropolitanas DANE)
INSERT INTO dim_departamento (codigo_dane, nombre, region, es_area_metro)
VALUES
    ('05', 'Antioquia',                    'Andina',     FALSE),
    ('08', 'Atlántico',                    'Caribe',     FALSE),
    ('11', 'Bogotá D.C.',                  'Andina',     TRUE ),
    ('13', 'Bolívar',                      'Caribe',     FALSE),
    ('15', 'Boyacá',                       'Andina',     FALSE),
    ('17', 'Caldas',                       'Andina',     FALSE),
    ('18', 'Caquetá',                      'Amazonia',   FALSE),
    ('19', 'Cauca',                        'Pacífica',   FALSE),
    ('20', 'Cesar',                        'Caribe',     FALSE),
    ('23', 'Córdoba',                      'Caribe',     FALSE),
    ('25', 'Cundinamarca',                 'Andina',     FALSE),
    ('27', 'Chocó',                        'Pacífica',   FALSE),
    ('41', 'Huila',                        'Andina',     FALSE),
    ('44', 'La Guajira',                   'Caribe',     FALSE),
    ('47', 'Magdalena',                    'Caribe',     FALSE),
    ('50', 'Meta',                         'Orinoquía',  FALSE),
    ('52', 'Nariño',                       'Pacífica',   FALSE),
    ('54', 'Norte de Santander',           'Andina',     FALSE),
    ('63', 'Quindío',                      'Andina',     FALSE),
    ('66', 'Risaralda',                    'Andina',     FALSE),
    ('68', 'Santander',                    'Andina',     FALSE),
    ('70', 'Sucre',                        'Caribe',     FALSE),
    ('73', 'Tolima',                       'Andina',     FALSE),
    ('76', 'Valle del Cauca',              'Pacífica',   FALSE),
    ('AM', 'Área Metropolitana Medellín',  'Andina',     TRUE ),
    ('BC', 'Barranquilla AM',              'Caribe',     TRUE ),
    ('BG', 'Bucaramanga AM',               'Andina',     TRUE ),
    ('CT', 'Cali AM',                      'Pacífica',   TRUE ),
    ('MC', 'Manizales AM',                 'Andina',     TRUE ),
    ('PC', 'Pereira AM',                   'Andina',     TRUE )
ON CONFLICT (codigo_dane) DO NOTHING;


-- ------------------------------------------------------------
-- 2. Dimensión periodo (mes-año 2010-2026, generada en Python)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_periodo (
    id_periodo   SERIAL   PRIMARY KEY,
    anio         SMALLINT NOT NULL,
    mes          SMALLINT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    trimestre    SMALLINT GENERATED ALWAYS AS ((mes - 1) / 3 + 1) STORED,
    fecha_inicio DATE     NOT NULL,
    UNIQUE (anio, mes)
);


-- ------------------------------------------------------------
-- 3. Tabla de hechos principal  (GEIH + FILCO + DANE)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_mercado_laboral (
    id                          BIGSERIAL    PRIMARY KEY,
    id_periodo                  INT          NOT NULL REFERENCES dim_periodo(id_periodo),
    id_departamento             INT          REFERENCES dim_departamento(id_departamento),
    sexo                        VARCHAR(10),                   -- Hombre / Mujer / Total
    grupo_edad                  VARCHAR(20),                   -- 15-28 / 29-45 / 46-65+
    zona                        VARCHAR(20),                   -- Cabecera / Resto / Total
    nivel_educativo             VARCHAR(40),
    rama_actividad              VARCHAR(100),
    posicion_ocupacional        VARCHAR(50),
    tasa_desocupacion           NUMERIC(6,2),
    tasa_ocupacion              NUMERIC(6,2),
    tasa_global_participacion   NUMERIC(6,2),
    tasa_formalidad             NUMERIC(6,2),
    tasa_informalidad           NUMERIC(6,2),
    ingreso_laboral             NUMERIC(14,2),
    afiliacion_seg_social       NUMERIC(6,2),
    variacion_anual_td          NUMERIC(6,2),                  -- calculada en PySpark
    fuente                      VARCHAR(20)  DEFAULT 'DANE',
    fecha_carga                 TIMESTAMP    DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fml_periodo
    ON fact_mercado_laboral (id_periodo);

CREATE INDEX IF NOT EXISTS idx_fml_depto
    ON fact_mercado_laboral (id_departamento);

CREATE INDEX IF NOT EXISTS idx_fml_sexo_zona
    ON fact_mercado_laboral (sexo, zona);


-- ------------------------------------------------------------
-- 4. Tabla de hechos SENA
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_demanda_sena (
    id               BIGSERIAL  PRIMARY KEY,
    id_periodo       INT        REFERENCES dim_periodo(id_periodo),
    id_departamento  INT        REFERENCES dim_departamento(id_departamento),
    ocupacion        VARCHAR(150),
    sector_economico VARCHAR(100),
    inscritos        INT,
    vacantes         INT,
    fuente           VARCHAR(20) DEFAULT 'SENA',
    fecha_carga      TIMESTAMP   DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fds_periodo
    ON fact_demanda_sena (id_periodo);

CREATE INDEX IF NOT EXISTS idx_fds_depto
    ON fact_demanda_sena (id_departamento);


-- ------------------------------------------------------------
-- 5. Predicciones Prophet
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prediccion_td (
    id              SERIAL       PRIMARY KEY,
    fecha           DATE         NOT NULL UNIQUE,
    td_predicha     NUMERIC(6,2) NOT NULL,
    td_lower        NUMERIC(6,2),                              -- intervalo inferior 80%
    td_upper        NUMERIC(6,2),                              -- intervalo superior 80%
    mae             NUMERIC(6,4),
    rmse            NUMERIC(6,4),
    modelo          VARCHAR(30)  DEFAULT 'Prophet-1.1.5',
    fecha_generado  TIMESTAMP    DEFAULT NOW()
);
