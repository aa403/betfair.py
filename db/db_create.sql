CREATE TABLE bfevent_types
(
    name VARCHAR(250),
    bf_id VARCHAR(100),
    id SERIAL PRIMARY KEY NOT NULL
);
CREATE TABLE bfevent_types_id2_seq
(
    sequence_name VARCHAR NOT NULL,
    last_value BIGINT NOT NULL,
    start_value BIGINT NOT NULL,
    increment_by BIGINT NOT NULL,
    max_value BIGINT NOT NULL,
    min_value BIGINT NOT NULL,
    cache_value BIGINT NOT NULL,
    log_cnt BIGINT NOT NULL,
    is_cycled BOOL NOT NULL,
    is_called BOOL NOT NULL
);
CREATE TABLE bfevents
(
    id SERIAL PRIMARY KEY NOT NULL,
    bf_id VARCHAR(100) NOT NULL,
    name VARCHAR(250) NOT NULL,
    country_code VARCHAR(5),
    last_update TIMESTAMP DEFAULT now(),
    market_count INT
);
CREATE TABLE bfevents_id_seq
(
    sequence_name VARCHAR NOT NULL,
    last_value BIGINT NOT NULL,
    start_value BIGINT NOT NULL,
    increment_by BIGINT NOT NULL,
    max_value BIGINT NOT NULL,
    min_value BIGINT NOT NULL,
    cache_value BIGINT NOT NULL,
    log_cnt BIGINT NOT NULL,
    is_cycled BOOL NOT NULL,
    is_called BOOL NOT NULL
);
CREATE TABLE competitions
(
    id SERIAL PRIMARY KEY NOT NULL,
    bf_id VARCHAR(100) NOT NULL,
    name VARCHAR(250) NOT NULL,
    market_count INT
);
CREATE TABLE competitions_id_seq
(
    sequence_name VARCHAR NOT NULL,
    last_value BIGINT NOT NULL,
    start_value BIGINT NOT NULL,
    increment_by BIGINT NOT NULL,
    max_value BIGINT NOT NULL,
    min_value BIGINT NOT NULL,
    cache_value BIGINT NOT NULL,
    log_cnt BIGINT NOT NULL,
    is_cycled BOOL NOT NULL,
    is_called BOOL NOT NULL
);
CREATE TABLE market_book_price
(
    id SERIAL PRIMARY KEY NOT NULL,
    market_id INT NOT NULL,
    runner_id INT NOT NULL,
    last_update TIMESTAMP DEFAULT now() NOT NULL,
    last_traded_price NUMERIC(131089),
    back_price_0 NUMERIC(131089) DEFAULT 1.01 NOT NULL,
    back_price_1 NUMERIC(131089),
    back_price_2 NUMERIC(131089),
    lay_price_0 NUMERIC(131089) DEFAULT 1000 NOT NULL,
    lay_price_1 NUMERIC(131089),
    lay_price_2 NUMERIC(131089),
    back_vol_0 NUMERIC(131089),
    back_vol_1 NUMERIC(131089),
    back_vol_2 NUMERIC(131089),
    lay_vol_0 NUMERIC(131089),
    lay_vol_1 NUMERIC(131089),
    lay_vol_2 NUMERIC(131089)
);
CREATE TABLE market_book_price_id_seq
(
    sequence_name VARCHAR NOT NULL,
    last_value BIGINT NOT NULL,
    start_value BIGINT NOT NULL,
    increment_by BIGINT NOT NULL,
    max_value BIGINT NOT NULL,
    min_value BIGINT NOT NULL,
    cache_value BIGINT NOT NULL,
    log_cnt BIGINT NOT NULL,
    is_cycled BOOL NOT NULL,
    is_called BOOL NOT NULL
);
CREATE TABLE market_catalogues
(
    id SERIAL PRIMARY KEY NOT NULL,
    competition_id INT,
    market_time TIMESTAMP,
    market_base_rate NUMERIC(131089) DEFAULT 2.0 NOT NULL,
    event_type_id INT,
    last_update TIMESTAMP DEFAULT now() NOT NULL,
    bf_id VARCHAR(50) NOT NULL,
    name VARCHAR(250) NOT NULL,
    status VARCHAR(50),
    total_matched NUMERIC(131089),
    total_available NUMERIC(131089)
);
CREATE TABLE market_catalogues_id_seq
(
    sequence_name VARCHAR NOT NULL,
    last_value BIGINT NOT NULL,
    start_value BIGINT NOT NULL,
    increment_by BIGINT NOT NULL,
    max_value BIGINT NOT NULL,
    min_value BIGINT NOT NULL,
    cache_value BIGINT NOT NULL,
    log_cnt BIGINT NOT NULL,
    is_cycled BOOL NOT NULL,
    is_called BOOL NOT NULL
);
CREATE TABLE runners
(
    id SERIAL PRIMARY KEY NOT NULL,
    bf_id VARCHAR(50) NOT NULL,
    name VARCHAR(250) NOT NULL,
    last_update TIMESTAMP DEFAULT now() NOT NULL
);
CREATE TABLE runners_id_seq
(
    sequence_name VARCHAR NOT NULL,
    last_value BIGINT NOT NULL,
    start_value BIGINT NOT NULL,
    increment_by BIGINT NOT NULL,
    max_value BIGINT NOT NULL,
    min_value BIGINT NOT NULL,
    cache_value BIGINT NOT NULL,
    log_cnt BIGINT NOT NULL,
    is_cycled BOOL NOT NULL,
    is_called BOOL NOT NULL
);
ALTER TABLE market_book_price ADD FOREIGN KEY (market_id) REFERENCES market_catalogues (id);
ALTER TABLE market_book_price ADD FOREIGN KEY (runner_id) REFERENCES runners (id);
ALTER TABLE market_catalogues ADD FOREIGN KEY (event_type_id) REFERENCES bfevents (id);
ALTER TABLE market_catalogues ADD FOREIGN KEY (competition_id) REFERENCES competitions (id);
CREATE UNIQUE INDEX unique_bf_id ON runners (bf_id);
