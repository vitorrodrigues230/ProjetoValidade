CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_validade DATE NOT NULL,
    quantidade INT DEFAULT 1,
    status_ia VARCHAR(50) 
);

SELECT * FROM produtos;