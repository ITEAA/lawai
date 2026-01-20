ANALYZE_BY_LAW = """
MATCH (d:DOC)-[:CONTAINS]->(a:ARTICLE)
WHERE d.law_name = $law_name
  AND ($level IS NULL OR d.level = $level)

OPTIONAL MATCH (a)-[:PENALTY_LINK]->(p:ARTICLE)

OPTIONAL MATCH (a)-[:HIERARCHY]->(h_child:ARTICLE)
OPTIONAL MATCH (h_parent:ARTICLE)-[:HIERARCHY]->(a)

OPTIONAL MATCH (a)-[:REFERENCE_WEAK]->(r:ARTICLE)

RETURN
  a.node_id    AS article_node_id,
  a.law_name   AS law_name,
  a.article_no AS article_no,
  a.title      AS title,
  a.content    AS content,
  d.level      AS level,

  [p_node IN collect(DISTINCT p) WHERE p_node IS NOT NULL |
    {
      node_id: p_node.node_id,
      article_no: p_node.article_no,
      title: p_node.title,
      content: p_node.content
    }
  ] AS penalties,

  (
    [c IN collect(DISTINCT h_child) WHERE c IS NOT NULL |
      {
        node_id: c.node_id,
        article_no: c.article_no,
        title: c.title,
        direction: "CHILD"
      }
    ]
    +
    [p IN collect(DISTINCT h_parent) WHERE p IS NOT NULL |
      {
        node_id: p.node_id,
        article_no: p.article_no,
        title: p.title,
        direction: "PARENT"
      }
    ]
  ) AS hierarchy,

  [r_node IN collect(DISTINCT r) WHERE r_node IS NOT NULL |
    {
      node_id: r_node.node_id,
      article_no: r_node.article_no,
      title: r_node.title
    }
  ] AS reference_weak
"""

ANALYZE_BY_ARTICLE = """
MATCH (d:DOC)-[:CONTAINS]->(a:ARTICLE)
WHERE d.law_name = $law_name
  AND a.article_no = $article_no
  AND ($level IS NULL OR d.level = $level)

OPTIONAL MATCH (a)-[:PENALTY_LINK]->(p:ARTICLE)

OPTIONAL MATCH (a)-[:HIERARCHY]->(h_child:ARTICLE)
OPTIONAL MATCH (h_parent:ARTICLE)-[:HIERARCHY]->(a)

OPTIONAL MATCH (a)-[:REFERENCE_WEAK]->(r:ARTICLE)

RETURN
  a.node_id    AS article_node_id,
  a.law_name   AS law_name,
  a.article_no AS article_no,
  a.title      AS title,
  a.content    AS content,
  d.level      AS level,

  [p_node IN collect(DISTINCT p) WHERE p_node IS NOT NULL |
    {
      node_id: p_node.node_id,
      article_no: p_node.article_no,
      title: p_node.title,
      content: p_node.content
    }
  ] AS penalties,

  (
    [c IN collect(DISTINCT h_child) WHERE c IS NOT NULL |
      {
        node_id: c.node_id,
        article_no: c.article_no,
        title: c.title,
        direction: "CHILD"
      }
    ]
    +
    [p IN collect(DISTINCT h_parent) WHERE p IS NOT NULL |
      {
        node_id: p.node_id,
        article_no: p.article_no,
        title: p.title,
        direction: "PARENT"
      }
    ]
  ) AS hierarchy,

  [r_node IN collect(DISTINCT r) WHERE r_node IS NOT NULL |
    {
      node_id: r_node.node_id,
      article_no: r_node.article_no,
      title: r_node.title
    }
  ] AS reference_weak
"""
