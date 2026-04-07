CREATE DATABASE IF NOT EXISTS ecommerce_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ecommerce_db;

-- ── Tabla usuarios ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id     INT          NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email  VARCHAR(150) NOT NULL,
    CONSTRAINT pk_usuarios   PRIMARY KEY (id),
    CONSTRAINT uq_email      UNIQUE      (email)
);

-- ── Tabla pedidos ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pedidos (
    id                  INT            NOT NULL AUTO_INCREMENT,
    usuario_id          INT            NOT NULL,
    total               DECIMAL(10,2)  NOT NULL,
    descuento_aplicado  DECIMAL(10,2)  NOT NULL DEFAULT 0,
    fecha               DATETIME       NOT NULL,
    CONSTRAINT pk_pedidos          PRIMARY KEY (id),
    CONSTRAINT fk_pedidos_usuario  FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    CONSTRAINT chk_total_positivo  CHECK (total >= 0)
);

-- ── Tabla pagos ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pagos (
    id         INT           NOT NULL AUTO_INCREMENT,
    pedido_id  INT           NOT NULL,
    monto      DECIMAL(10,2),
    fecha_pago DATETIME      NOT NULL,
    CONSTRAINT pk_pagos          PRIMARY KEY (id),
    CONSTRAINT fk_pagos_pedido   FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    CONSTRAINT chk_monto_positivo CHECK (monto > 0)
);

-- ── Procedimiento almacenado: crear pedido con transacción ───
-- (Alternativa al manejo de transacciones en Python)
DROP PROCEDURE IF EXISTS sp_crear_pedido;

DELIMITER $$

CREATE PROCEDURE sp_crear_pedido (
    IN  p_usuario_id  INT,
    IN  p_total       DECIMAL(10,2),
    OUT p_pedido_id   INT,
    OUT p_monto_pago  DECIMAL(10,2)
)
BEGIN
    DECLARE v_descuento DECIMAL(10,2) DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Calcular descuento del 10 % si total > 1000
    IF p_total > 1000 THEN
        SET v_descuento = ROUND(p_total * 0.10, 2);
    END IF;

    SET p_monto_pago = p_total - v_descuento;

    -- Insertar pedido
    INSERT INTO pedidos (usuario_id, total, descuento_aplicado, fecha)
    VALUES (p_usuario_id, p_total, v_descuento, NOW());

    SET p_pedido_id = LAST_INSERT_ID();

    -- Insertar pago
    INSERT INTO pagos (pedido_id, monto, fecha_pago)
    VALUES (p_pedido_id, p_monto_pago, NOW());

    COMMIT;
END$$

DELIMITER ;