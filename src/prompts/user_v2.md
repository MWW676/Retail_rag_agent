Please answer the following query based on the provided policies and help articles:

[QUERY START]
{{ query }}
[QUERY END]

[REFERENCES START]
{% for c in chunks %}
[chunk_id: {{ c.chunk_id }} | type: {{ c.doc_type }} | updated: {{ c.updated_at or "n/a" }}]
{{ c.text }}
{% if not loop.last %}

{% endif %}{% endfor %}
[REFERENCES END]