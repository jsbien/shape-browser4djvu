-- create_aux.sql
CREATE DATABASE IF NOT EXISTS Exercitum__aux
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- switch to aux
USE Exercitum__aux;

-- create views into source DB
CREATE OR REPLACE VIEW documents    AS SELECT * FROM Exercitum.documents;
CREATE OR REPLACE VIEW dictionaries AS SELECT * FROM Exercitum.dictionaries;
CREATE OR REPLACE VIEW shapes       AS SELECT * FROM Exercitum.shapes;
CREATE OR REPLACE VIEW blits        AS SELECT * FROM Exercitum.blits;

-- derived tables
CREATE TABLE IF NOT EXISTS sb_shape_usage (
  document_id INT NOT NULL,
  shape_id    INT NOT NULL,
  usage_count INT NOT NULL,
  PRIMARY KEY (document_id, shape_id),
  INDEX idx_usage_count (usage_count)
);

CREATE TABLE IF NOT EXISTS sb_shape_tree (
  dictionary_id INT NOT NULL,
  shape_id      INT NOT NULL,
  parent_id     INT,
  dfs_pre       INT,
  dfs_post      INT,
  depth         INT,
  sibling_index INT,
  PRIMARY KEY (dictionary_id, shape_id),
  INDEX idx_dict_pre (dictionary_id, dfs_pre),
  INDEX idx_dict_parent (dictionary_id, parent_id)
);

CREATE TABLE IF NOT EXISTS sb_shape_subtree_usage (
  dictionary_id INT NOT NULL,
  shape_id      INT NOT NULL,
  subtree_usage INT NOT NULL,
  PRIMARY KEY (dictionary_id, shape_id),
  INDEX idx_subtree_usage (subtree_usage)
);

-- populate v1 usage table
TRUNCATE sb_shape_usage;
INSERT INTO sb_shape_usage(document_id, shape_id, usage_count)
SELECT document_id, shape_id, COUNT(*) AS usage_count
FROM blits
GROUP BY document_id, shape_id;

-- sanity check
SHOW FULL TABLES;
