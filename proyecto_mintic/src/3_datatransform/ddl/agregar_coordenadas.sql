-- Tabla de coordenadas para las ciudades de fact_informalidad
-- Permite usar el visual de mapa en Power BI con precisión

CREATE TABLE IF NOT EXISTS dim_ciudad (
    id_ciudad   SERIAL PRIMARY KEY,
    ciudad      VARCHAR(120) UNIQUE NOT NULL,
    latitud     NUMERIC(9,6),
    longitud    NUMERIC(9,6),
    departamento VARCHAR(60),
    region      VARCHAR(40)
);

INSERT INTO dim_ciudad (ciudad, latitud, longitud, departamento, region) VALUES
('Total nacional',        4.570868,  -74.297333, NULL,               NULL),
('13 Ciudades y A.M.',    4.570868,  -74.297333, NULL,               NULL),
('23 Ciudades y A.M.',    4.570868,  -74.297333, NULL,               NULL),
('Bogotá D.C.',           4.710989,  -74.072092, 'Bogotá D.C.',      'Andina'),
('Medellín A.M.',         6.244203,  -75.581212, 'Antioquia',        'Andina'),
('Cali A.M.',             3.451647,  -76.531985, 'Valle del Cauca',  'Pacífica'),
('Barranquilla A.M.',    10.963889,  -74.796387, 'Atlántico',        'Caribe'),
('Bucaramanga A.M.',      7.119349,  -73.122742, 'Santander',        'Andina'),
('Manizales A.M.',        5.070408,  -75.513600, 'Caldas',           'Andina'),
('Pasto',                 1.213611,  -77.281111, 'Nariño',           'Andina'),
('Pereira A.M.',          4.813333,  -75.696111, 'Risaralda',        'Andina'),
('Cúcuta A.M.',           7.893900,  -72.507800, 'Norte de Santander','Andina'),
('Ibagué',                4.438889,  -75.232222, 'Tolima',           'Andina'),
('Montería',              8.757780,  -75.881390, 'Córdoba',          'Caribe'),
('Cartagena',            10.391050,  -75.479430, 'Bolívar',          'Caribe'),
('Villavicencio',         4.142900,  -73.626700, 'Meta',             'Orinoquía'),
('Tunja',                 5.535400,  -73.367900, 'Boyacá',           'Andina'),
('Florencia',             1.614500,  -75.606400, 'Caquetá',          'Amazonia'),
('Riohacha',             11.544400,  -72.907200, 'La Guajira',       'Caribe'),
('Santa Marta',          11.240600,  -74.199900, 'Magdalena',        'Caribe'),
('Valledupar',           10.477600,  -73.251200, 'Cesar',            'Caribe'),
('Quibdó',                5.694400,  -76.658100, 'Chocó',            'Pacífica'),
('Armenia',               4.533900,  -75.681200, 'Quindío',          'Andina'),
('Sincelejo',             9.304700,  -75.397500, 'Sucre',            'Caribe'),
('Popayán',               2.441100,  -76.606700, 'Cauca',            'Andina'),
('Neiva',                 2.935100,  -75.281600, 'Huila',            'Andina')
ON CONFLICT (ciudad) DO NOTHING;
