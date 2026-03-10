CREATE CONSTRAINT asset_id_unique IF NOT EXISTS FOR (a:Asset) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT node_id_unique IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE;

CREATE INDEX node_name_index IF NOT EXISTS FOR (n:Node) ON (n.name);
CREATE INDEX node_type_index IF NOT EXISTS FOR (n:Node) ON (n.type);
CREATE INDEX node_created_at_index IF NOT EXISTS FOR (n:Node) ON (n.created_at);

CALL dbms.components() YIELD name, versions, edition
RETURN name, versions, edition;
