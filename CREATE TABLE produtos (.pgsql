DROP TABLE IF EXISTS produtos;

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    id_externo INT UNIQUE,
    nome VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    data_validade DATE,
    quantidade INT DEFAULT 1,
    status_ia VARCHAR(20) DEFAULT 'Seguro'
);

INSERT INTO produtos (id_externo, nome, categoria, data_validade, quantidade, status_ia) VALUES
(101, 'Leite Integral 1L', 'Laticínios', '2026-05-10', 50, 'Seguro'),
(102, 'Iogurte Natural', 'Laticínios', '2026-04-30', 20, 'Crítico'),
(103, 'Arroz 5kg', 'Grãos', '2027-01-15', 10, 'Seguro');
