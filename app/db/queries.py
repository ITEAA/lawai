ANALYZE_BY_ARTICLE = """
MATCH (a:LawNode {node_type:"ARTICLE"})
WHERE a.law_name = $law_name
  AND a.article_no = $article_no

OPTIONAL MATCH (a)-[r1:HIERARCHY|REFERENCE_WEAK]->(b:LawNode {node_type:"ARTICLE"})
OPTIONAL MATCH (a)-[:PENALTY_LINK]->(p:LawNode {node_type:"ARTICLE"})

RETURN
  a {
    .node_id,
    .law_name,
    .article_no,
    .title,
    .content
  } AS article,

  collect(DISTINCT b {
    .node_id,
    article_no: b.article_no,
    title: b.title,
    relation: type(r1)
  }) AS related_articles,

  collect(DISTINCT p {
    .node_id,
    article_no: p.article_no,
    title: p.title,
    content: p.content
  }) AS penalties
"""

ANALYZE_BY_LAW = """
MATCH (d:LawNode {node_type:"DOC", law_name:$law_name})
      -[:CONTAINS]->(a:LawNode {node_type:"ARTICLE"})

OPTIONAL MATCH (a)-[r1:HIERARCHY|REFERENCE_WEAK]->(b:LawNode {node_type:"ARTICLE"})
OPTIONAL MATCH (a)-[:PENALTY_LINK]->(p:LawNode {node_type:"ARTICLE"})

RETURN
  a {
    .node_id,
    .law_name,
    .article_no,
    .title,
    .content
  } AS article,

  collect(DISTINCT b {
    .node_id,
    article_no: b.article_no,
    title: b.title,
    relation: type(r1)
  }) AS related_articles,

  collect(DISTINCT p {
    .node_id,
    article_no: p.article_no,
    title: p.title,
    content: p.content
  }) AS penalties
"""
